import pytest

INGEST = "/api/v1/alerts/ingest"


@pytest.fixture
def api_key(owner):
    res = owner.post("/api-keys", {"name": "Prometheus"})
    assert res.status_code == 201
    return res.json()["secret"]


def alert(external_id="a-1", title="High error rate", **payload):
    return {
        "source": "monitor",
        "external_id": external_id,
        "title": title,
        "payload": {"service": "checkout", "environment": "prod", **payload},
    }


def ingest(client, key, body):
    return client.post(INGEST, json=body, headers={"X-API-Key": key})


def test_api_key_is_shown_once_and_listed_without_secret(owner, api_key):
    assert api_key.startswith("sf_")
    keys = owner.get("/api-keys").json()
    assert len(keys) == 1
    assert "secret" not in keys[0]
    assert keys[0]["key_prefix"] == api_key[:12]


def test_ingest_requires_a_valid_key(client, api_key):
    assert client.post(INGEST, json=alert()).status_code == 401
    assert ingest(client, "sf_wrong", alert()).status_code == 401
    assert ingest(client, api_key[:-1] + ("A" if api_key[-1] != "A" else "B"), alert()).status_code == 401


def test_first_alert_opens_an_incident(client, owner, api_key):
    res = ingest(client, api_key, alert(severity="critical", summary="5xx above 2%"))
    assert res.status_code == 202
    body = res.json()
    assert body["deduplicated"] is False
    incident = owner.get(f"/incidents/{body['incident_id']}").json()
    assert incident["severity"] == "critical"
    assert incident["description"] == "5xx above 2%"


def test_matching_alerts_group_into_the_open_incident(client, owner, api_key):
    first = ingest(client, api_key, alert("a-1", severity="medium")).json()
    second = ingest(client, api_key, alert("a-2", severity="critical")).json()

    assert second["deduplicated"] is True
    assert second["incident_id"] == first["incident_id"]
    assert len(owner.get("/incidents").json()) == 1

    incident_id = first["incident_id"]
    assert owner.get(f"/incidents/{incident_id}").json()["severity"] == "critical"
    grouped = owner.get(f"/incidents/{incident_id}/alerts").json()
    assert [a["external_id"] for a in grouped] == ["a-1", "a-2"]
    timeline = owner.get(f"/incidents/{incident_id}/timeline").json()
    assert "Severity raised from medium to critical" in timeline[-1]["body"]


def test_lower_severity_duplicates_do_not_downgrade(client, owner, api_key):
    first = ingest(client, api_key, alert("a-1", severity="high")).json()
    ingest(client, api_key, alert("a-2", severity="low"))
    assert owner.get(f"/incidents/{first['incident_id']}").json()["severity"] == "high"


def test_different_services_open_separate_incidents(client, owner, api_key):
    ingest(client, api_key, alert("a-1"))
    ingest(client, api_key, {**alert("a-2"), "payload": {"service": "search", "environment": "prod"}})
    assert len(owner.get("/incidents").json()) == 2


def test_resolved_incidents_do_not_absorb_new_alerts(client, owner, api_key):
    first = ingest(client, api_key, alert("a-1")).json()
    owner.patch(f"/incidents/{first['incident_id']}", {"status": "resolved"})
    again = ingest(client, api_key, alert("a-2")).json()
    assert again["deduplicated"] is False
    assert again["incident_id"] != first["incident_id"]


def test_redelivery_is_idempotent(client, owner, api_key):
    first = ingest(client, api_key, alert("a-1")).json()
    retry = ingest(client, api_key, alert("a-1")).json()
    assert retry["alert_id"] == first["alert_id"]
    assert retry["duplicate_delivery"] is True
    assert len(owner.get("/alerts").json()) == 1


def test_alerts_are_scoped_to_the_key_organization(client, owner, register, api_key):
    ingest(client, api_key, alert())
    other = register(org="Other")
    other_key = other.post("/api-keys", {"name": "theirs"}).json()["secret"]
    ingest(client, other_key, alert())
    assert len(owner.get("/alerts").json()) == 1
    assert len(other.get("/alerts").json()) == 1


def test_unknown_severity_defaults_to_medium(client, owner, api_key):
    body = ingest(client, api_key, alert(severity="sev-banana")).json()
    assert owner.get(f"/incidents/{body['incident_id']}").json()["severity"] == "medium"


def test_api_keys_need_organization_manage(owner, add_member):
    admin = add_member(owner, "admin")
    assert admin.get("/api-keys").status_code == 403
    assert admin.post("/api-keys", {"name": "nope"}).status_code == 403


def test_ingest_validates_body(client, api_key):
    assert ingest(client, api_key, {"source": "pager", "external_id": "x", "title": "abc"}).status_code == 422
    assert ingest(client, api_key, {"source": "monitor", "external_id": "", "title": "abc"}).status_code == 422
