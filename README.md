# AI Email Agent

An AI-powered email triage system that automatically classifies incoming emails using **Google Gemini**, stores actionable alerts in a database, and streams them to a **real-time React dashboard** over WebSockets — with zero polling.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.0-092E20?style=flat&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat&logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietary-red?style=flat)

---

## What It Does

The agent runs a background pipeline that continuously reads from an email source, sends each message to an AI classifier, and takes one of two paths:

- **Important emails** (billing failures, system crashes, etc.) are stored and instantly pushed to the dashboard via WebSocket.
- **Unimportant emails** (newsletters, promotions, etc.) are silently discarded — they never touch the database or the UI.

The result is a low-noise, real-time alert dashboard for emails that actually matter.

---

## Features

- **Deterministic AI classification** — Google Gemini at `temperature=0.0` produces consistent, reproducible decisions for the same email content
- **Idempotent pipeline** — a `ProcessedEmail` guard table ensures each email is classified exactly once, even across server restarts
- **Real-time dashboard** — WebSocket pushes new alerts instantly; REST API serves historical data on initial load
- **Priority triage** — AI assigns `HIGH`, `MEDIUM`, or `LOW` priority and a human-readable reason for every decision
- **Noise filtering** — unimportant emails are dropped at the classification layer and never persisted
- **Fallback classifier** — rule-based keyword detection handles Gemini API failures gracefully
- **Source-agnostic core** — the pipeline is designed to support JSON, IMAP, webhooks, or streaming queues without changes to the core architecture

---

## How the AI Works

Every email is passed through the classification service in [`ai_classifier.py`](backend/agent/services/ai_classifier.py), which uses a **hybrid approach**:

1. **Primary — Google Gemini 2.5 Flash** (via LangChain) reads the sender, subject, and body and reasons about the email. It runs at `temperature=0.0` for deterministic, reproducible decisions, and its output is validated against a strict Pydantic schema.
2. **Fallback — rule-based classifier.** If no API key is configured or the API call fails, a keyword-based engine takes over so the pipeline never stops.

For every email, the AI produces a structured decision:

```json
{
  "important": true,
  "priority": "HIGH",
  "category": "PAYMENT_ISSUE",
  "reason": "A chargeback dispute threatens account suspension and requires immediate action."
}
```

| Field | Meaning |
|---|---|
| `important` | `true` → shown on dashboard · `false` → silently dropped (pure spam only) |
| `priority` | `HIGH` (payment/outage/urgent complaint), `MEDIUM` (non-urgent request), `LOW` (newsletters/automated) |
| `category` | One of `PAYMENT_ISSUE`, `SERVER_DOWN`, `CLIENT_COMPLAINT`, `SUBSCRIPTION`, `SPAM` |
| `reason` | A human-readable sentence justifying the decision |

**What gets flagged as important:** client complaints and urgent requests, payment/billing issues, system outages, and low-priority automated/subscription emails (shown with `LOW` priority). Only pure spam is dropped.

## How the Dashboard Works

The dashboard is a React single-page app that combines two data channels:

1. **On load** — it fetches all previously stored important notifications from the REST endpoint `GET /api/notifications/` so the user sees history immediately.
2. **Live** — it opens a persistent WebSocket to `/ws/emails/`. When the background worker classifies a new important email, the backend broadcasts it and the card appears on the dashboard instantly, with no refresh or polling.

Each notification card displays all six required fields: **sender, subject, priority, category, AI reason, and time received.** Incoming events are de-duplicated by `email_id` in the client state, and the user can filter the view by priority (`HIGH` / `MEDIUM` / `LOW`).

## Limitations

This is a proof-of-concept. Known limitations:

- **Mock data source.** The current ingestion reads from `mock_emails.json`. Gmail/IMAP adapters are designed for but not yet implemented (see [CORE_ARCHITECTURE.md](CORE_ARCHITECTURE.md)).
- **In-memory channel layer.** WebSocket broadcasting uses Django Channels' in-memory backend, which works for a single process only. Production multi-worker deployments would need Redis (`channels-redis` is already in `requirements.txt`).
- **SQLite database.** Fine for development; a production deployment should use PostgreSQL.
- **Polling interval.** The worker polls every 2 minutes, so there is up to a 2-minute delay between an email arriving in the source and appearing on the dashboard.
- **Dev server in Docker.** The frontend container runs the Vite dev server. A production setup would build static assets and serve them via Nginx.
- **Gemini dependency.** Without a valid `GEMINI_API_KEY`, the system runs entirely on the rule-based fallback, which is less nuanced than the LLM.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 5.0 + Django REST Framework |
| Real-Time | Django Channels 4 + Daphne (ASGI) |
| AI Model | Google Gemini 2.5 Flash via LangChain |
| Schema Validation | Pydantic 2 |
| Frontend | React 19 + Vite 8 + TailwindCSS 4 |
| Database | SQLite (dev) |
| Containerization | Docker + Docker Compose |

---

## Getting Started

### Prerequisites

- Docker and Docker Compose installed, **or** Python 3.11+ and Node 22+ for a local setup
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### With Docker (recommended)

```bash
# 1. Copy the environment template and fill in your Gemini API key
cp .env.example backend/.env

# 2. Build and start both services
docker compose up --build
```

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend API: [http://localhost:8000/api/notifications/](http://localhost:8000/api/notifications/)

### Without Docker

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

**Frontend (separate terminal):**
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Copy `.env.example` to `backend/.env` and configure:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development |
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `MOCK_MODE` | `True` to use `mock_emails.json` as the email source |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed frontend origins |

---

## Documentation

| Document | Contents |
|---|---|
| [CORE_ARCHITECTURE.md](CORE_ARCHITECTURE.md) | Source-agnostic system design, execution flow, and design principles |
| [ARCHITECTURE_LOCAL_JSON.md](ARCHITECTURE_LOCAL_JSON.md) | JSON ingestion implementation, idempotency mechanics, and classification examples |

---

## Author

**Golam Ahmed Mugdha**
Junior Software Engineer — Backend & AI Systems
Focused on scalable automation, AI agents, and intelligent backend architectures.

---

## License

This project is proprietary. See [LICENSE.md](LICENSE.md) for full usage restrictions.
Viewing for evaluation and learning purposes is permitted. All other use requires explicit written permission.
