# Sovereign Pair - User Manual and Frontend Operations

**Interface Version:** 3.3.0
**Default Access (Local):** `https://localhost`
**Cloud Access (Tailscale):** `https://sovereign-rag-cloud.[YOUR_TAILNET].ts.net`

This document is structured for Analysts, Engineers, and End Users of Sovereign Pair RAG, detailing exploration, session management, and operation on the high-performance Web Interface (PWA) powered by `Vue3`.

---

## 1. Web Interface Topology

The Sovereign Pair interface was architected under the principles of extreme focus and clean information density (native *Dark/Light Mode*). The layout is divided into strict spatial components:

### 1.1 Activity Bar
Located at the far left edge of the screen (Collapsible/Invisible on smaller resolutions). Serves as the primary navigation rudder between isolated system modules.
- **Chat Icon:** Returns to the Cibrid Sessions and Dialogs Center.
- **Vault Icon (Sensus):** Expands the Real-Time File System explorer.
- **Settings Icon:** Opens the customization panels (LLM Temperature, Model Switching, Tokens).

### 1.2 Session List Panel
Adjacent to the Activity Bar. Displays the persistent registry of all dialogs established with the Postgres Back-End. Sessions are archived chronologically. 
- Engages silent routing mechanics to preserve local context without trafficking unnecessary *overheads*.

---

## 2. Accessing Intelligence (Chat Module)

The Chat module is the primary *Prompt* Injection pathway.
Communication flows via *Server-Sent Events (SSE)*, providing predatory token emission without *timeouts* on dense analytical responses.

### 2.1 Metadata Usage and Contextualization
Unlike isolated chat systems, our engineering implements the concept of RAG. Whenever the user clicks on a file through the Sensus Vault and fills the Chat, that document's ID guides the context.
- When the semantic mesh is triggered, it will textually intersect your prompt with the strictly vectorized information in the database corresponding to the open context.

### 2.2 Model and Temperature Selectors
In the Top Panels (Hidden Dropdowns), the user can toggle cognitive load instantly:
- **Model:** Toggle between Local Ollama endpoints (`llama3.2`) or corporate calls on the OpenAI API, without losing the conversational thread of the session.
- **Temperature:** Dynamic slider. Change to `0.0` for dry code extraction, or raise to `0.7` for architectural analyses requiring abstraction.

---

## 3. File Management (Sensus Vault Director)

Sovereign Pair transcends Traditional Web applications by providing a Systemic File Manager injected directly into the Interface via SSR.

### 3.1 Folder CRUD Operations
The `Vault` displays your corporate document tree mirroring the isolated logical Server Host disk at `data/vault`.
1. **Recursive Navigation:** Directories are linearly expanded, respecting logical allocations and alphabetical order.
2. **Quick Creation:** "New Folder" and "New File" icons at the top of the tree materialize instances directly on the disk via API dispatches.
3. **Security Restrictions (Path Traversal):** Any attempt to create files by injecting relative strings (`../`) will be intercepted by the `sovereign-api` Zero-Trust barrier, preventing privilege escalation.

### 3.2 Built-in Markdown Viewer
Selected `.md` files in the Sensus Vault are hydrated in a robust central renderer. This panel will compile logical markdowns, code blocks with *Syntax Highlighting*, and fluent formatting for immersive side-by-side reading with the Active Chat tab.

---

## 4. The Knowledge Injection System (Ingestion)

### 4.1 Incremental Hybrid Pipeline
Every batch file update needs to be processed and registered in the RAG Vector mind (ChromaDB) so that the AI can reason about them.
- The Process is executed natively by the Host CLI (via `python src/ingest.py`). 
- **Incremental Mode** tracks the SHA256 Hashes of the entire Host document vault. It smartly identifies which paragraphs underwent modifications and strictly vectorizes the delta snippets, injecting brutal agility (computational savings > 90%).

### 4.2 Natively Supported Files:
- Plain and Structured Texts (`.md`, `.txt`, `.csv`, `.json`).
- Dense Pagination (`.pdf`, `.docx`, `.html`).
The Ingestor applies corporate chunking rules where long sentences are kept intact in mathematical overlaps so that systemic responses never return cut off without context to Frontend users.

---

## 5. Cibrid Identity Guidelines (Mobile Zero-Trust)
Whenever accessing the corporate system off-premises via Cellular or Public Networks, ensure the Metric HTTPS key strictly reflects the authenticated Tailscale Domain of the corresponding node, and the App's sidebar reports `Status: Connected and Shielded` proven via Edge-issued JWT tokens.

- The Web Application will implement aggressive strategies on the Service Worker to keep functional artifacts alive even during transitions through areas with no coverage (3G/4G). Reconnection will silently stack pending telemetry. 

---
**Referenced Technical Glossary:** See `docs/glossary.en-US.md`.