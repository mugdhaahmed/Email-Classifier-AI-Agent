⚠️ PROPRIETARY CODE — UNAUTHORIZED USE PROHIBITED

# 🧠 Core Architecture — Email Classifier AI Agent

This document describes the **core, data-source-agnostic architecture** of the Email Classifier AI Agent.

It focuses on:
- System design principles
- Execution flow
- AI inference guarantees
- Real-time synchronization mechanics

⚠️ This file intentionally avoids referencing any specific input format (JSON, IMAP, SMTP, etc.).

---

## 🎯 Architectural Goals

- Deterministic AI-driven classification
- Production-grade idempotency
- Noise-free signal extraction
- Real-time UI observability
- Decoupled, scalable components

---

## 🏗️ High-Level System Layers

The platform is divided into **three independent but coordinated layers**:

---

### 
1️⃣ Ingestion Layer (Source-Agnostic)

**Responsibilities**
- Continuously pull messages from an external source
- Normalize raw input into internal message objects
- Enforce idempotency before classification
- Operate independently from the web server

**Design Principles**
- Background execution
- Restart-safe
- Queue-like behavior
- Exactly-once processing

---

### 
2️⃣ AI Classification & Triage Layer

**Responsibilities**
- Perform structural classification using an LLM
- Enforce strict output schemas
- Assign importance, priority, and category
- Generate transparent reasoning
- Provide fail-safe behavior

**Determinism Guarantees**
- Low temperature inference (`temperature = 0.0`)
- Schema-bound JSON parsing
- Validation before persistence

**Standard Output Contract**
```json
{
  "important": true,
  "priority": "HIGH",
  "category": "SYSTEM",
  "reason": "Critical system failure detected"
}

---

### 3️⃣ Real-Time Synchronization Layer

**Responsibilities**

- Maintain persistent WebSocket connections
- Broadcast newly classified important events
- Enable instant UI updates without refresh
- Act as a live observability channel

- Core Characteristics:
- ASGI-based
- Non-blocking
- Event-driven


🔁 End-to-End Execution Flow
- Ingestion layer fetches a new message
- Idempotency guard prevents duplicates
- AI classifier evaluates message structure
- Decision is validated and persisted
- Important events are broadcast in real time
- Non-important events are silently discarded


🧩 Extensibility Philosophy
- The architecture is intentionally designed to support multiple ingestion sources, such as:
- Local JSON datasets
- IMAP email servers
- Webhooks
- Streaming queues


<--- Each source introduces its own architecture file, without modifying this core document. --->