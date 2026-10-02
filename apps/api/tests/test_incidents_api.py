from tests.conftest import incident_payload


def test_create_get_and_list(owner):
    created = owner.post("/incidents", incident_payload())
    assert created.status_code == 201
    incident = created.json()
    assert incident["status"] == "open"

    assert owner.get(f"/incidents/{incident['id']}").json()["title"] == "Checkout latency"
    assert [i["id"] for i in owner.get("/incidents").json()] == [incident["id"]]


def test_list_filters_by_status_and_paginates(owner):
    first = owner.post("/incidents", incident_payload(title="First one")).json()
    owner.post("/incidents", incident_payload(title="Second one"))
    owner.patch(f"/incidents/{first['id']}", {"status": "resolved"})

    resolved = owner.get("/incidents", params={"status": "resolved"}).json()
    assert [i["title"] for i in resolved] == ["First one"]
    assert len(owner.get("/incidents", params={"limit": 1}).json()) == 1
    assert owner.get("/incidents", params={"limit": 0}).status_code == 422
    assert owner.get("/incidents", params={"limit": 101}).status_code == 422


def test_update_records_timeline_and_audit(owner):
    incident = owner.post("/incidents", incident_payload()).json()
    res = owner.patch(f"/incidents/{incident['id']}", {"status": "acknowledged", "severity": "critical"})
    assert res.status_code == 200
    assert res.json()["severity"] == "critical"

    timeline = owner.get(f"/incidents/{incident['id']}/timeline").json()
    assert [e["event_type"] for e in timeline] == ["incident.created", "incident.updated"]
    assert "status changed from open to acknowledged" in timeline[1]["body"]

    actions = [log["action"] for log in owner.get("/audit-logs").json()]
    assert "incident.updated" in actions and "incident.created" in actions


def test_noop_update_adds_no_timeline_event(owner):
    incident = owner.post("/incidents", incident_payload()).json()
    owner.patch(f"/incidents/{incident['id']}", {"status": "open"})
    assert len(owner.get(f"/incidents/{incident['id']}/timeline").json()) == 1


def test_assignee_must_be_an_org_member(owner, register, add_member):
    incident = owner.post("/incidents", incident_payload()).json()
    outsider = register()
    res = owner.patch(f"/incidents/{incident['id']}", {"assignee_id": outsider.user_id})
    assert res.status_code == 422

    responder = add_member(owner, "responder")
    res = owner.patch(f"/incidents/{incident['id']}", {"assignee_id": responder.user_id})
    assert res.status_code == 200
    assert res.json()["assignee_id"] == responder.user_id


def test_missing_incidents_are_404(owner):
    missing = "00000000-0000-0000-0000-000000000000"
    assert owner.get(f"/incidents/{missing}").status_code == 404
    assert owner.patch(f"/incidents/{missing}", {"status": "resolved"}).status_code == 404
    assert owner.get(f"/incidents/{missing}/timeline").status_code == 404
    assert owner.get("/incidents/not-a-uuid").status_code == 422


def test_other_organizations_are_isolated(owner, register):
    incident = owner.post("/incidents", incident_payload()).json()
    other = register(org="Other Org")

    # Another org's member can't reach this org's data at all...
    other.org_id, mine = owner.org_id, other.org_id
    assert other.get("/incidents").status_code == 403
    assert other.get(f"/incidents/{incident['id']}").status_code == 403
    assert other.post("/incidents", incident_payload()).status_code == 403

    # ...and an incident id from another org is invisible inside their own org.
    other.org_id = mine
    assert other.get(f"/incidents/{incident['id']}").status_code == 404
    assert other.patch(f"/incidents/{incident['id']}", {"status": "resolved"}).status_code == 404


def test_viewers_can_read_but_not_write(owner, add_member):
    incident = owner.post("/incidents", incident_payload()).json()
    viewer = add_member(owner, "viewer")
    assert viewer.get("/incidents").status_code == 200
    assert viewer.get(f"/incidents/{incident['id']}/timeline").status_code == 200
    assert viewer.post("/incidents", incident_payload()).status_code == 403
    assert viewer.patch(f"/incidents/{incident['id']}", {"status": "resolved"}).status_code == 403
    assert viewer.post(f"/incidents/{incident['id']}/triage").status_code == 403


def test_responders_can_write(owner, add_member):
    responder = add_member(owner, "responder")
    assert responder.post("/incidents", incident_payload()).status_code == 201


def test_triage_records_a_timeline_entry(owner):
    incident = owner.post("/incidents", incident_payload(severity="critical")).json()
    res = owner.post(f"/incidents/{incident['id']}/triage")
    assert res.status_code == 200
    body = res.json()
    assert body["provider"] == "deterministic"
    assert body["summary"].startswith("CRITICAL incident (open)")
    assert len(body["recommended_actions"]) == 3

    timeline = owner.get(f"/incidents/{incident['id']}/timeline").json()
    assert timeline[-1]["event_type"] == "ai.triage"
    assert body["recommended_actions"][0] in timeline[-1]["body"]


def test_triage_unknown_incident_is_404(owner):
    assert owner.post("/incidents/00000000-0000-0000-0000-000000000000/triage").status_code == 404
