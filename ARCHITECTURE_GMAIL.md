> ⚠️ **PROPRIETARY CODE — UNAUTHORIZED USE PROHIBITED.** See [LICENSE.md](LICENSE.md).

# Architecture — Gmail API Ingestion

This document describes the **real Gmail ingestion implementation** of the AI Email Agent.

> This document covers only the Gmail-specific layer. Core system concepts — AI classification, real-time synchronization, and design principles — are documented in [CORE_ARCHITECTURE.md](CORE_ARCHITECTURE.md). The local JSON source is documented in [ARCHITECTURE_LOCAL_JSON.md](ARCHITECTURE_LOCAL_JSON.md).

---

## Purpose

Gmail ingestion connects the agent to a **live inbox**. On each poll the worker pulls unread messages from Gmail, normalizes them into the shared internal email shape, and hands them to the exact same classification → persistence → broadcast pipeline used by mock mode.

This realizes the source-agnostic promise of the core architecture: the worker does not know or care whether an email came from a JSON file or Gmail.

---

## Source Adapter Design

All ingestion sources implement a single contract in [`sources/base.py`](backend/agent/services/sources/base.py):

```python
class EmailSource(ABC):
    @abstractmethod
    def fetch(self) -> list[dict]: ...
```

Every source returns the same normalized dictionary, which is what keeps the pipeline source-agnostic:

| Key | Description |
|---|---|
| `email_id` | Globally unique ID (Gmail message id) — feeds the `ProcessedEmail` idempotency guard |
| `sender` | Raw `From` header |
| `subject` | Subject header |
| `body` | Plain-text body |
| `received_at` | ISO-8601 timestamp |

The factory [`get_email_source()`](backend/agent/services/sources/__init__.py) selects the implementation from `MOCK_MODE`:

```
MOCK_MODE=True  -> MockJSONSource   (reads mock_emails.json, no credentials)
MOCK_MODE=False -> GmailSource      (reads real unread Gmail)
```

`GmailSource` is imported lazily, so mock mode never requires the Google client libraries or a token to be present.

---

## Authentication

| Property | Value |
|---|---|
| Method | OAuth 2.0, "Desktop app" client |
| Scope | `https://www.googleapis.com/auth/gmail.readonly` (read-only) |
| Client secret | `credentials.json` (downloaded from Google Cloud, gitignored) |
| Stored token | `token.json` (generated locally, gitignored) |

Authentication is a **one-time, out-of-band step** handled by the management command
[`gmail_auth`](backend/agent/management/commands/gmail_auth.py):

```bash
cd backend
python manage.py gmail_auth
```

This opens a browser, completes the OAuth consent, and writes `token.json`. The background worker then runs **fully headless** — it loads `token.json` and silently refreshes the access token using the stored refresh token, so no browser is ever needed at runtime.

> **Why read-only?** The inbox is never modified. Duplicate prevention is handled entirely by the existing `ProcessedEmail` table, so messages do not need to be marked as read.

---

## Fetch Logic

Implemented in [`sources/gmail_source.py`](backend/agent/services/sources/gmail_source.py).

```
1. Build an authenticated Gmail service (cached across poll cycles)
2. users().messages().list(userId='me', q=GMAIL_QUERY, maxResults=GMAIL_MAX_RESULTS)
3. For each message id:
     a. users().messages().get(format='full')
     b. Parse From / Subject from headers
     c. Extract text/plain body by walking the MIME tree
        (fall back to the message 'snippet' if no plaintext part)
     d. Parse the Date header into an ISO timestamp
4. Return the list of normalized dicts
```

| Env var | Default | Purpose |
|---|---|---|
| `GMAIL_QUERY` | `is:unread` | Any Gmail search syntax (labels, senders, time windows) |
| `GMAIL_MAX_RESULTS` | `10` | Max messages pulled per 2-minute cycle |
| `GMAIL_CREDENTIALS_PATH` | `credentials.json` | OAuth client file (relative to `backend/`) |
| `GMAIL_TOKEN_PATH` | `token.json` | Saved token file (relative to `backend/`) |

---

## Idempotency

Gmail message IDs are globally unique and stable, so they slot directly into the existing guard with no schema change:

```python
if ProcessedEmail.objects.filter(email_id=email_id).exists():
    continue  # already processed — skip
```

Because the worker uses `is:unread` but never marks mail as read, the same unread message may be returned on the next poll — the `ProcessedEmail` table ensures it is classified exactly once regardless.

---

## Execution Flow (Gmail Mode)

```
Gmail inbox (unread)
      │
      ▼
GmailSource.fetch()  ── OAuth token.json (auto-refreshed)
      │
      ▼  normalized email dicts
pipeline_worker.py (background thread, every 2 min)
      │
      ├─ email_id in ProcessedEmail? ──Yes──► skip (silent)
      │
      No
      ▼
ai_classifier.py (Gemini, temperature=0.0)
      │
      ├─ important: false ──► discard (silent)
      │
      └─ important: true
            ├─ Write ProcessedEmail (idempotency)
            ├─ Write ImportantNotification (storage)
            └─ Broadcast via Django Channels WebSocket
                        │
                        ▼
                 React dashboard (card appears live)
```

---

## Security Notes

- `credentials.json` and `token.json` are **gitignored and dockerignored**. They hold OAuth secrets and must never be committed.
- In Docker, the `./backend:/app` bind mount exposes these files to the container automatically when placed in `backend/`.
- The read-only scope guarantees the agent can never send, delete, or modify mail.

---

## License

This implementation is proprietary. See [LICENSE.md](LICENSE.md) for full usage restrictions.
