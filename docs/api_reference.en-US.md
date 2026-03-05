# Sovereign Pair - Integration API Reference

**Architecture Status:** Stable (Release 3.3.0)
**Protocol:** HTTP/RESTful + Server-Sent Events (SSE)
**Security (Auth):** Bearer Token (JWT / Tailscale M2M)

This document is intended for Integration Engineers (SRE/DevOps) and developers of secondary tools (such as auxiliary scripts, N8N, or custom Obsidian clients). It details the RESTful signatures hosted by the central port of the Sovereign Pair's on-premises FastAPI engine, enabling external handling of the RAG (Retrieval-Augmented Generation) mesh under a Zero-Trust infrastructure.

---

## Authentication and Access Topology

Sovereign Pair discards public routing. Access to the documented endpoints requires traffic encapsulated via an authorized tunnel (Tailscale Darknet IP) or `localhost`.

Every external request originating from the VPN mesh (e.g., Oracle OCI instantiating N8N) mandates the temporal presence of the canonical Authorization header containing the Bearer string signed by the infrastructure's *Secret-Key* or an M2M Auth generated via Tailscale:

```http
Authorization: Bearer <your_shielded_session_jwt>
```

---

## 1. Inference Engine (LLM & RAG)

### Asynchronous Reactive Engine Invocation (`POST /v1/chat`)
Vital endpoint to dialogue with the Cibrid RAG mesh. Injects raw prompts based on the user machine's organic context. Supports standardized atomic responses or Server-Sent Events (SSE) Stream for real-time UX progressive rendering.

**Endpoint:** `POST /api/v1/chat`
**Headers:** `Content-Type: application/json`

**JSON Payload:**
```json
{
  "message": "What is the root password documented in the OCI manual?",
  "stream": true,
  "agent_role": "the_coder",
  "folder_context": "Corporate Projects"
}
```

**Body Properties (Trade-Offs):**
*   `message` *(required)*: The user's injection (prompt) in raw string.
*   `stream` *(optional, default false)*: Enables chunking over `text/event-stream`. When set to `true`, perceived latency drops drastically. Recommended for human interfaces (Vue/React).
*   `agent_role` *(optional)*: Overrides the inferential Persona. Redirects system Prompt parameters (e.g., `"the_coder"` triggers dense Python logic blocks, `"the_doctor"` triggers meticulous causal and philosophical taxonomy). Absence assumes the The Mom/The Dad guideline.
*   `folder_context` *(optional)*: Locks the search into a semantic compartment rather than globally reading the entire `/home/` structure, preventing cross-contamination of RAG sources by limiting the BM25/Cosine retriever.

**Streaming Return (SSE - HTTP 200):**
The packet limit returned subdivides into renderable tokens until coupling the exact references used by Llama.
```text
data: {"token": "T", "done": false}
data: {"token": "he", "done": false}
data: {"token": " root", "done": false}
data: {"token": " password", "done": false}
data: {"token": " is", "done": false}
data: {"token": " 123.", "done": false}
data: {"sources": ["file:///vault/dev/oracle.md"], "done": true}
```

**Atomic Return (HTTP 200 - When `stream`: false):**
```json
{
  "response": "The root password is 123.",
  "sources": [
    "file:///vault/dev/oracle.md"
  ]
}
```

---

## 2. Ingestion Trigger (Vector Operations)

### Sensus Vault Recalculation (`POST /v1/ingest`)
Forces the reevaluation of the memory vectors in the database (ChromaDB) by inspecting differences, deletions, and unmapped additions from the file subsystem on the host operating system.

**Operational Warning:** 
Given the CPU-intensive I/O nature, calls to this module queue processing in Asynchronous Threads limited by the Python Global Interpreter Lock (GIL), operating `compute_hashes_parallel` internally at rates 4x higher than classic blocking I/O. Massive triggers (DDoS) without rate-limits will stagnate local visual interface resources, hence treat this Trigger exclusively via restricted corporate instances or File Watcher Webhooks controlled by Cronjob/N8N.

**Endpoint:** `POST /api/v1/ingest`

**Asynchronous Validation Return (HTTP 200):**
```json
{
   "status": "success",
   "message": "Differential scan operation triggered in Background queues.",
   "total_dirty_files_queued": 14
}
```

---

*Internal Team Note (QA): Legacy endpoints based on pure Python monolithic utilities were deprecated locally, being encapsulated into the Anthropic MCP integration SDK in subsequent phases.*