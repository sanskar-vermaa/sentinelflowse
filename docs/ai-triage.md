# AI Triage

SentinelFlow includes an AI-ready triage service. The default provider is
deterministic so the project runs without paid API keys.

## Local Gemini Configuration

Add this to your local `.env` file only:

```txt
AI_PROVIDER=gemini
GEMINI_API_KEY=your-local-key
```

Never commit API keys. If a key is pasted into chat or public history, revoke it
and create a new one.

## Current Scope

The v1 project exposes provider boundaries and safe configuration. A production
Gemini HTTP adapter can be added later without changing incident or alert APIs.
