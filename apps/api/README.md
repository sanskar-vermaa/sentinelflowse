# SentinelFlow API

FastAPI backend for auth, incidents, alerts, workflows, audit logs, and
dashboard summaries.

## Run

```bash
pip install -e . pytest httpx email-validator
uvicorn app.main:app --reload
```

## Demo Database

```bash
copy .env.demo.example .env
python -m app.db.seed
```

Open API docs at `http://localhost:8000/docs`.
