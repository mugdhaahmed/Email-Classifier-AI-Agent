> ⚠️ **PROPRIETARY CODE — UNAUTHORIZED USE PROHIBITED.** See [LICENSE.md](LICENSE.md).

# Core Architecture — AI Email Agent

This document describes the **core, data-source-agnostic architecture** of the AI Email Agent. It covers system design principles, execution flow, AI inference guarantees, and real-time synchronization mechanics.

> This document intentionally avoids referencing any specific input format (JSON, IMAP, SMTP, webhooks, etc.). Each ingestion source has its own dedicated architecture document.

---

## Architectural Goals

| Goal | Description |
|---|---|
| **Deterministic classification** | AI produces the same decision for the same input, every time |
| **Idempotency** | Every message is processed exactly once, even across restarts |
| **Noise-free signal** | Unimportant messages are dropped before reaching storage or the UI |
| **Real-time observability** | Important alerts surface on the dashboard the moment they are classified |
| **Decoupled components** | Ingestion, classification, and presentation evolve independently |

---

## System Layers

The platform is divided into three independent but coordinated layers:

```
┌──────────────────────────────────────────────────────────┐
│                   LAYER 1: INGESTION                     │
│              (Source-Agnostic Background Worker)         │
│                                                          │
│   Pull messages → Normalize → Idempotency check         │
└───────────────────────────┬──────────────────────────────┘
                            │ New, unique message
                            ▼
┌──────────────────────────────────────────────────────────┐
│              LAYER 2: AI CLASSIFICATION                  │
│         (Google Gemini · LangChain · Pydantic)           │
│                                                          │
│   Analyze → Validate schema → Assign priority            │
└──────────────┬────────────────────────────┬──────────────┘
               │ important: true            │ important: false
               ▼                            ▼
┌──────────────────────────┐         (silently discarded —
│   LAYER 3: REAL-TIME     │          never stored, never
│   SYNCHRONIZATION        │          reaches the UI)
│   (Django Channels/ASGI) │
│                          │
│   Persist → Broadcast    │
│   WebSocket → React UI   │
└──────────────────────────┘
```

---

### Layer 1 — Ingestion (Source-Agnostic)

**Responsibilities:**
- Continuously pull messages from an external source
- Normalize raw input into a standard internal message object
- Enforce idempotency before passing to classification
- Run entirely in the background, independent of the web server

**Design properties:**
- Background execution (does not block HTTP request handling)
- Restart-safe (processes only messages not already seen)
- Queue-like sequential behavior
- Exactly-once processing guarantee

---

### Layer 2 — AI Classification & Triage

**Responsibilities:**
- Analyze message content using an LLM
- Produce a structured, schema-validated output
- Assign importance, priority, and category
- Generate a human-readable reasoning string
- Fall back to rule-based classification if the AI service is unavailable

**Determinism guarantees:**
- `temperature = 0.0` — identical inputs produce identical outputs
- Schema-bound JSON parsing via Pydantic — malformed responses are rejected
- Validation is enforced before any write to the database

**Output contract:**

```json
{
  "important": true,
  "priority": "HIGH",
  "category": "BILLING",
  "reason": "Chargeback settlement failure detected with direct financial impact."
}
```

| Field | Type | Values |
|---|---|---|
| `important` | boolean | `true` → surface to dashboard; `false` → discard |
| `priority` | enum | `HIGH`, `MEDIUM`, `LOW` |
| `category` | string | `BILLING`, `DATABASE`, `SYSTEM`, `MARKETING`, … |
| `reason` | string | Human-readable AI-generated justification |

---

### Layer 3 — Real-Time Synchronization

**Responsibilities:**
- Maintain persistent WebSocket connections with connected clients
- Broadcast newly classified important events immediately after persistence
- Serve historical notifications via REST API on initial page load
- Act as the live observability channel between backend and UI

**Core characteristics:**
- ASGI-based (non-blocking, handles HTTP and WebSocket concurrently)
- Event-driven (no polling — the backend pushes to clients)
- Group-based broadcasting (all connected clients receive the same event)

---

## End-to-End Execution Flow

```
1.  Ingestion worker fetches the next message from the source
2.  Idempotency guard checks if the message ID has been seen before
      └─ Duplicate → skip silently
3.  Message is passed to the AI classifier
4.  Classifier returns a structured, validated decision
5.  Decision is evaluated:
      ├─ important: false → message is discarded, nothing is written
      └─ important: true  →
            a. Mark message ID as processed (idempotency record)
            b. Persist the notification to the database
            c. Broadcast the notification via WebSocket to all clients
6.  React dashboard receives the WebSocket event and renders the card
```

---

## Extensibility

The core architecture is intentionally source-agnostic. Adding a new ingestion source (IMAP, webhook, streaming queue) requires only:

1. A new ingestion adapter that normalizes messages into the standard internal object
2. A new architecture document describing that specific implementation

The classification layer, real-time layer, and UI are untouched.

| Source | Status |
|---|---|
| Local JSON file | Implemented (see [ARCHITECTURE_LOCAL_JSON.md](ARCHITECTURE_LOCAL_JSON.md)) |
| IMAP email server | Planned |
| HTTP webhooks | Planned |
| Message queues (Redis, SQS) | Planned |
