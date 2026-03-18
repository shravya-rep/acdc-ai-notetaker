# ACDC Teams AI Notetaker

Autonomous agentic system that monitors Microsoft Teams meetings, generates intelligent recaps, and proactively manages action item follow-ups.

## Architecture

Three cooperating autonomous agents:
- **Meeting Monitor** — polls Microsoft Graph API every 15 minutes, detects completed meetings, queues jobs
- **Recap Generator** — fetches transcripts, classifies meeting type, calls LLM (Claude/GPT-4), stores structured recap, sends email
- **Follow-up Manager** — daily scan of open action items, sends deadline reminders

**Stack**: Django 5 + DRF · Next.js 14 · PostgreSQL 16 · Redis 7 · Celery 5 · Microsoft Graph API · Anthropic/OpenAI

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Azure AD app registration with Microsoft Graph permissions
- Anthropic or OpenAI API key

### Setup

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your Azure AD credentials and API keys

# 2. Start all services
docker compose up --build

# 3. Run migrations
docker compose exec backend python manage.py migrate

# 4. Create superuser
docker compose exec backend python manage.py createsuperuser
```

### Services
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000/api |
| Django Admin | http://localhost:8000/admin |

## Project Structure

```
acdc-meeting-intelligence/
├── backend/                  # Django 5 + DRF
│   ├── apps/
│   │   ├── users/            # Auth, Microsoft OAuth
│   │   ├── meetings/         # Meeting models, API endpoints
│   │   ├── graph/            # Microsoft Graph client, webhooks
│   │   └── agents/           # Autonomous agents + Celery tasks
│   └── config/               # Django settings, Celery config
├── frontend/                 # Next.js 14 + TypeScript
│   └── src/
│       ├── app/              # App Router pages
│       └── lib/              # API client
├── docker-compose.yml
└── .env.example
```

## Microsoft Graph Setup

1. Register app in Azure Portal → Azure Active Directory → App Registrations
2. Add API permissions: `Calendars.Read`, `OnlineMeetings.Read`, `User.Read`, `CallRecords.Read.All`
3. Create client secret, add to `.env`
4. Register webhook: `POST /api/graph/webhook/` as notification URL

## Agents

### Meeting Monitor (every 15 min)
Polls Graph API for completed meetings, applies skip rules (short meetings, personal events), queues `process_meeting_task`.

### Recap Generator (event-driven)
Fetches transcript with exponential backoff, classifies meeting type, calls LLM with contextual prompt, stores structured JSON recap, emails all attendees.

### Follow-up Manager (daily at 8am UTC)
Scans `ActionItem` table for items due within 24 hours, sends reminder emails, logs escalations for overdue items.

## Development

```bash
# Backend only
cd backend && pip install -r requirements.txt
python manage.py runserver

# Run Celery worker
celery -A config worker --loglevel=info

# Frontend only
cd frontend && npm install && npm run dev
```

## Environment Variables

See `.env.example` for all required variables. Never commit `.env`.

## Team

- **AI Engineer 1** (Backend Lead): Django API, Graph integration, DB design, Celery agents
- **AI Engineer 2** (Full-Stack): LLM integration, prompt engineering, meeting classifier
- **AI Engineer 3** (Frontend Lead): React dashboard, API client, UI/UX
- **AI Engineer 4** (DevOps, optional): Docker, monitoring, CI/CD
