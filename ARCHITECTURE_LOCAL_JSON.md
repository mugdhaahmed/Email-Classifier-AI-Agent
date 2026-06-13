> ⚠️ **PROPRIETARY CODE — UNAUTHORIZED USE PROHIBITED.** See [LICENSE.md](LICENSE.md).

# Architecture — Local JSON Ingestion

This document describes the **local JSON-based ingestion implementation** of the AI Email Agent.

> This document covers only the JSON-specific layer. Core system concepts — AI classification, real-time synchronization, and design principles — are documented in [CORE_ARCHITECTURE.md](CORE_ARCHITECTURE.md).

---

## Purpose

The local JSON ingestion mode exists to:

- Validate and demonstrate the core pipeline architecture without external dependencies
- Test deterministic AI classification against a controlled, reproducible dataset
- Simulate production-style queue behavior using a static file

It intentionally mirrors how a production ingestion adapter would behave, making it a direct stand-in for IMAP or webhook sources during development.

---

## Data Source

| Property | Value |
|---|---|
| Input file | `backend/agent/data/mock_emails.json` |
| Processing model | Sequential background polling |
| Processing guarantee | Exactly-once (idempotent) |
| Environment | Local development (`MOCK_MODE=True`) |

Each record in the JSON file represents a single email message. The file intentionally includes one duplicate record to verify idempotency behavior.

**Record structure:**

```json
{
  "msg_id": "msg_001_2026",
  "sender": "billing@stripe-alerts.com",
  "subject": "URGENT: Chargeback settlement failure — Action required",
  "body": "A chargeback has been initiated on transaction #TXN-8821...",
  "received_at": "2026-06-12T10:00:00Z"
}
```

---

## Ingestion Engine

**File:** [`backend/agent/services/pipeline_worker.py`](backend/agent/services/pipeline_worker.py)

The pipeline worker runs as a background thread, started automatically when Django boots (via `AppConfig.ready()`). It does not share the web server's request/response cycle.

**Execution loop (every 2 minutes):**

```
1. Read and parse mock_emails.json
2. For each record:
   a. Check idempotency guard → skip if already processed
   b. Pass message to AI classifier
   c. If important: persist + broadcast via WebSocket
   d. If not important: discard silently
3. Sleep for 2 minutes, then repeat
```

---

## Idempotency & Duplicate Prevention

Each JSON record must contain a globally unique `msg_id`. Before classification, the worker checks this ID against the `ProcessedEmail` database table:

```python
if ProcessedEmail.objects.filter(message_id=email_id).exists():
    continue  # already processed — skip
```

**Guarantees:**

- Each message is classified exactly once
- Worker restarts do not reprocess previously handled messages
- The duplicate record in `mock_emails.json` is silently skipped on its second encounter
- Behavior matches production-level reliability expectations

---

## AI Classification

Each JSON message is passed to the AI classification layer as defined in [CORE_ARCHITECTURE.md](CORE_ARCHITECTURE.md). The classifier uses Google Gemini 2.5 Flash at `temperature=0.0` to ensure reproducible decisions.

**File:** [`backend/agent/services/ai_classifier.py`](backend/agent/services/ai_classifier.py)

**Output contract:**

```json
{
  "important": true,
  "priority": "HIGH",
  "category": "BILLING",
  "reason": "Payment failure detected with direct financial impact requiring immediate action."
}
```

**Fallback behavior:** If the Gemini API is unavailable, the classifier falls back to keyword-based rule matching (e.g., `chargeback`, `failure`, `crash`, `unreachable`) to ensure uninterrupted operation.

---

## Example Classification Outcomes

The following outcomes are produced from the four records in `mock_emails.json`:

| Message ID | Sender / Subject | AI Decision | Result |
|---|---|---|---|
| `msg_001_2026` | `billing@stripe-alerts.com` — Chargeback failure | `important: true`, `HIGH`, `BILLING` | Persisted + pushed to dashboard |
| `msg_002_2026` | `noreply@github.com` — GitHub Universe newsletter | `important: false` | Silently discarded |
| `msg_003_2026` | `devops-alerts@internal-monitor.net` — DB crash | `important: true`, `HIGH`, `SYSTEM` | Persisted + pushed to dashboard |
| `msg_001_2026` | *(duplicate of msg_001)* | — | Skipped by idempotency guard |

---

## Execution Flow (JSON Mode)

```
mock_emails.json
      │
      ▼
pipeline_worker.py (background thread)
      │
      ├─ msg_id in ProcessedEmail? ──Yes──► skip (silent)
      │
      No
      │
      ▼
ai_classifier.py
      │
      ├─ important: false ──► discard (silent, nothing written)
      │
      └─ important: true
            │
            ├─ Write ProcessedEmail record (idempotency)
            ├─ Write ImportantNotification record (storage)
            └─ Broadcast via Django Channels WebSocket
                        │
                        ▼
                 React dashboard
                 (new card appears instantly)
```

---

## Database Models

| Model | Purpose |
|---|---|
| `ProcessedEmail` | Stores processed `msg_id` values — the idempotency guard |
| `ImportantNotification` | Stores classified important emails for REST API and dashboard display |

---

## License

This implementation is proprietary. See [LICENSE.md](LICENSE.md) for full usage restrictions.
