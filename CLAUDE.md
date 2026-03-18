# CLAUDE.md — ACDC AI Notetaker

Guidelines for AI engineers working on this repo with Claude Code.

## Project Overview

Autonomous agentic system: 3 Celery-based agents process Teams meetings end-to-end without human intervention. Django REST API + Next.js frontend.

## Architecture Notes

- **Agents** live in `backend/apps/agents/`. The three core agents are `monitor.py`, `recap_generator.py`, `followup_manager.py`. Their Celery task wrappers are in `tasks.py`.
- **Graph integration** is in `backend/apps/graph/`. The `client.py` handles token acquisition (app-level for daemon, user-level for delegated).
- **Settings** are split: `base.py` (shared) → `development.py` / `production.py`. Always use `env()` from `django-environ` for secrets.
- **LLM abstraction**: `recap_generator.py` supports both Anthropic and OpenAI via `LLM_PROVIDER` env var. Default: `anthropic` with `claude-sonnet-4-6`.

## Key Conventions

- **Never hardcode secrets**. Use `env("VAR_NAME")` everywhere. All secrets live in `.env` (gitignored).
- **Async work goes through Celery**. Don't call Graph API or LLMs synchronously in API request handlers.
- **Retry with backoff**. All Celery tasks that call external APIs use `max_retries=3` and `default_retry_delay=60`.
- **Log at the right level**. Use `logger.info` for normal flow, `logger.warning` for skips/fallbacks, `logger.error` for failures.
- **ProcessingLog** every significant event in the meeting pipeline for debuggability.

## Running Locally

```bash
docker compose up --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

Frontend at http://localhost:3000, API at http://localhost:8000/api.

## Testing

```bash
# Backend
docker compose exec backend python manage.py test apps

# Type check frontend
cd frontend && npm run type-check
```

## Common Tasks

**Trigger manual recap generation:**
```python
from apps.agents.tasks import process_meeting_task
process_meeting_task.delay(meeting_id=42)
```

**Check Celery task status:**
```bash
docker compose exec celery_worker celery -A config inspect active
```

**Tail agent logs:**
```bash
docker compose logs -f celery_worker celery_beat
```

## LLM Prompt Changes

Edit `SYSTEM_PROMPT` in `backend/apps/agents/recap_generator.py`. Always test prompt changes against real transcripts before merging. The expected output schema is validated by `json.loads()` — if the LLM returns invalid JSON, the task retries.

## Microsoft Graph Webhook

In development, use `ngrok` to expose localhost for Graph webhook validation:
```bash
ngrok http 8000
# Then register: https://your-ngrok-url.ngrok.io/api/graph/webhook/
```
