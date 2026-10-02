import pytest

from app.core.config import settings
from tests.conftest import incident_payload

NOTIFY = {"steps": [{"type": "notify", "channel": "on-call"}]}


def create(account, **overrides):
    body = {"name": "Page on-call", "trigger": "incident.created", "definition": NOTIFY, **overrides}
    return account.post("/workflows", body)


@pytest.fixture
def inline(monkeypatch):
    monkeypatch.setattr(settings, "workflow_execution", "inline")


def test_create_list_and_get(owner):
    workflow = create(owner).json()
    assert workflow["is_enabled"] is True
    assert [w["id"] for w in owner.get("/workflows").json()] == [workflow["id"]]
    assert owner.get(f"/workflows/{workflow['id']}").json()["name"] == "Page on-call"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"trigger": "incident.exploded"}, "Unknown trigger"),
        ({"definition": {}}, "non-empty 'steps'"),
        ({"definition": {"steps": [{"type": "email"}]}}, "type must be one of"),
        ({"definition": {"steps": [{"type": "notify"}]}}, "needs a 'channel'"),
        ({"definition": {"steps": [{"type": "timeline"}]}}, "needs a 'message'"),
        ({"definition": {"steps": [{"type": "escalate", "severity": "huge"}]}}, "valid 'severity'"),
        ({"definition": {**NOTIFY, "conditions": {"min_severity": "x"}}}, "min_severity"),
        ({"definition": {**NOTIFY, "conditions": []}}, "'conditions' must be"),
        ({"definition": {"steps": [{"type": "notify", "channel": "c"}] * 21}}, "at most 20"),
    ],
)
def test_invalid_definitions_are_rejected(owner, overrides, message):
    res = create(owner, **overrides)
    assert res.status_code == 422
    assert message in res.json()["detail"]


def test_incident_creation_queues_matching_runs(owner, session_factory):
    from app.models.workflow import WorkflowRun

    workflow = create(owner).json()
    create(owner, name="Only critical", definition={**NOTIFY, "conditions": {"min_severity": "critical"}})
    create(owner, name="On resolve", trigger="incident.resolved")
    owner.post("/incidents", incident_payload(severity="high"))

    runs = owner.get(f"/workflows/{workflow['id']}/runs").json()
    assert [r["status"] for r in runs] == ["queued"]
    assert session_factory().query(WorkflowRun).count() == 1


def test_disabled_workflows_do_not_run(owner):
    workflow = create(owner).json()
    assert owner.patch(f"/workflows/{workflow['id']}", {"is_enabled": False}).json()["is_enabled"] is False
    owner.post("/incidents", incident_payload())
    assert owner.get(f"/workflows/{workflow['id']}/runs").json() == []


def test_inline_execution_runs_steps_on_the_incident(owner, inline):
    steps = [
        {"type": "notify", "channel": "#incidents"},
        {"type": "timeline", "message": "Runbook started"},
        {"type": "escalate", "severity": "critical"},
    ]
    workflow = create(owner, definition={"steps": steps}).json()
    incident = owner.post("/incidents", incident_payload(severity="medium")).json()

    run = owner.get(f"/workflows/{workflow['id']}/runs").json()[0]
    assert run["status"] == "succeeded"
    assert len(run["output_payload"]["steps"]) == 3
    assert owner.get(f"/incidents/{incident['id']}").json()["severity"] == "critical"
    bodies = [e["body"] for e in owner.get(f"/incidents/{incident['id']}/timeline").json()]
    assert "Workflow 'Page on-call' notified #incidents." in bodies
    assert any("Runbook started" in b for b in bodies)
    assert "workflow.run.succeeded" in [log["action"] for log in owner.get("/audit-logs").json()]


def test_resolution_triggers_resolve_workflows(owner, inline):
    workflow = create(
        owner,
        trigger="incident.resolved",
        definition={"steps": [{"type": "timeline", "message": "Write the postmortem"}]},
    ).json()
    incident = owner.post("/incidents", incident_payload()).json()
    owner.patch(f"/incidents/{incident['id']}", {"status": "acknowledged"})
    assert owner.get(f"/workflows/{workflow['id']}/runs").json() == []
    owner.patch(f"/incidents/{incident['id']}", {"status": "resolved"})
    assert len(owner.get(f"/workflows/{workflow['id']}/runs").json()) == 1


def test_manual_run(owner, inline):
    workflow = create(owner, trigger="manual").json()
    incident = owner.post("/incidents", incident_payload()).json()
    res = owner.post(f"/workflows/{workflow['id']}/runs", {"incident_id": incident["id"]})
    assert res.status_code == 202
    assert res.json()["status"] == "succeeded"

    no_incident = owner.post(f"/workflows/{workflow['id']}/runs", {}).json()
    assert no_incident["status"] == "succeeded"


def test_manual_run_rejects_unknown_ids(owner):
    workflow = create(owner, trigger="manual").json()
    missing = "00000000-0000-0000-0000-000000000000"
    assert owner.post(f"/workflows/{missing}/runs", {}).status_code == 404
    assert owner.post(f"/workflows/{workflow['id']}/runs", {"incident_id": missing}).status_code == 404


def test_escalate_without_an_incident_fails_the_run(owner, inline):
    workflow = create(owner, trigger="manual", definition={"steps": [{"type": "escalate", "severity": "high"}]}).json()
    run = owner.post(f"/workflows/{workflow['id']}/runs", {}).json()
    assert run["status"] == "failed"
    assert "needs an incident" in run["output_payload"]["error"]


def test_permissions(owner, add_member):
    workflow = create(owner).json()
    responder = add_member(owner, "responder")
    assert responder.get("/workflows").status_code == 200
    assert create(responder).status_code == 403
    assert responder.patch(f"/workflows/{workflow['id']}", {"is_enabled": False}).status_code == 403
    assert responder.post(f"/workflows/{workflow['id']}/runs", {}).status_code == 403
    admin = add_member(owner, "admin")
    assert create(admin).status_code == 201


def test_missing_workflow_is_404(owner):
    missing = "00000000-0000-0000-0000-000000000000"
    assert owner.get(f"/workflows/{missing}").status_code == 404
    assert owner.get(f"/workflows/{missing}/runs").status_code == 404
    assert owner.patch(f"/workflows/{missing}", {"name": "New"}).status_code == 404


def test_dashboard_counts_only_this_org(owner, register, inline):
    create(owner)
    owner.post("/incidents", incident_payload())
    other = register(org="Other")
    create(other)
    other.post("/incidents", incident_payload())
    other.post("/incidents", incident_payload(title="Another"))

    summary = owner.get("/dashboard/summary").json()
    assert summary == {"open_incidents": 1, "alerts_processed": 0, "workflow_runs": 1}
    assert other.get("/dashboard/summary").json()["workflow_runs"] == 2


def test_audit_log_needs_organization_manage(owner, add_member):
    admin = add_member(owner, "admin")
    assert admin.get("/audit-logs").status_code == 403
    assert owner.get("/audit-logs").status_code == 200
