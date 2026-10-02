import json

import httpx

from app.core.config import Settings
from app.services.triage_service import TriageRequest, TriageService

REQUEST = TriageRequest(
    title="Checkout 5xx", severity="critical", status="open", alert_sources=["monitor:a-1", "monitor:a-2"]
)


def gemini_settings(**kw) -> Settings:
    return Settings(ai_provider="gemini", gemini_api_key="test-key", jwt_secret="x" * 40, **kw)


def client_returning(payload, status=200, seen=None):
    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request)
        body = {"candidates": [{"content": {"parts": [{"text": json.dumps(payload)}]}}]}
        return httpx.Response(status, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_playbook_without_ai():
    result = TriageService(Settings(jwt_secret="x" * 40)).suggest(REQUEST)
    assert result.provider == "deterministic"
    assert result.summary == "CRITICAL incident (open) across 2 grouped alerts: Checkout 5xx"
    assert result.recommended_actions[0].startswith("Page the on-call owner")


def test_playbook_handles_unknown_severity():
    result = TriageService(Settings(jwt_secret="x" * 40)).suggest(TriageRequest(title="t", severity="weird"))
    assert len(result.recommended_actions) == 3


def test_gemini_result_is_used(monkeypatch):
    seen = []
    client = client_returning(
        {"summary": "Payments failing after deploy.", "recommended_actions": ["Roll back", " ", "Page payments"]},
        seen=seen,
    )
    result = TriageService(gemini_settings(), client).suggest(REQUEST)
    assert result.provider == "gemini"
    assert result.recommended_actions == ["Roll back", "Page payments"]
    request = seen[0]
    assert request.headers["x-goog-api-key"] == "test-key"
    assert "gemini-2.5-flash:generateContent" in str(request.url)
    assert "monitor:a-1" in request.content.decode()


def test_gemini_errors_fall_back_to_the_playbook():
    for client in (
        client_returning({}, status=429),
        client_returning({"summary": "", "recommended_actions": []}),
        client_returning({"wrong": "shape"}),
    ):
        assert TriageService(gemini_settings(), client).suggest(REQUEST).provider == "deterministic"


def test_gemini_without_key_uses_playbook():
    config = Settings(ai_provider="gemini", jwt_secret="x" * 40)
    assert TriageService(config).suggest(REQUEST).provider == "deterministic"
