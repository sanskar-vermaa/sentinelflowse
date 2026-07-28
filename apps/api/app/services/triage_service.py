from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class TriageRequest:
    title: str
    severity: str
    summary: str | None = None


@dataclass(frozen=True)
class TriageResult:
    provider: str
    summary: str
    recommended_actions: list[str]


class TriageService:
    def suggest(self, request: TriageRequest) -> TriageResult:
        if settings.ai_provider == "gemini" and settings.gemini_api_key:
            return self._gemini_placeholder(request)
        return self._deterministic(request)

    def _deterministic(self, request: TriageRequest) -> TriageResult:
        return TriageResult(
            provider="deterministic",
            summary=f"{request.severity.upper()} incident: {request.title}",
            recommended_actions=[
                "Confirm current customer impact",
                "Review recent deployments and alerts",
                "Assign an owner and record mitigation steps",
            ],
        )

    def _gemini_placeholder(self, request: TriageRequest) -> TriageResult:
        return TriageResult(
            provider="gemini",
            summary=f"Gemini triage is configured for: {request.title}",
            recommended_actions=[
                "Connect the Gemini HTTP client in the provider adapter",
                "Keep API keys in local environment variables",
                "Store AI output as advisory timeline context",
            ],
        )

