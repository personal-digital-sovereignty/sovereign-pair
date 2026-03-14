# Treatise IV: The RAG Pipeline & Cognitive Mapping

Sovereign Pair achieves cognition not through static pre-training, but through dynamic context retrieval. This is achieved via our hybrid Retriever-Augmented Generation (RAG) pipeline.

## 1. The ingestion Lifecycle (Digestion)

When a new Markdown or PDF document enters the Vault (`/data/vault/`), the engine does not simply "read" it. It mathematical fractions it.

1.  **Parsing:** Internal Rust-based markdown mapping routines strip raw HTML and format codes, leaving naked text parsed statically via OS Regex validations.
2.  **Chunking (`CHUNK_SIZE` and `CHUNK_OVERLAP`):** It is impossible to feed a 500-page book into an LLM simultaneously. The engine uses a rolling window. It cuts the text into chunks of 1024 tokens (words/syllables) each. It leaves an overlap of 200 tokens between Chunk A and Chunk B so the AI doesn't lose the context of a sentence split in half.
3.  **Embedding (`bge-m3`):** Each text chunk is mathematically converted into a 1024-dimensional coordinate, crossing language barriers smoothly. 
4.  **Vector Storage:** The embeddings are saved into `sqlite-vec` directly coupled to the internal DB structure.

> [!NOTE] 
> ▫️ **Chunking Core Loop:** `src-rust/core/ingest.rs`
> ▫️ **File Watchdog/Observer:** `src-rust/core/watcher.rs`

---

## 2. The Hybrid Search (Vector + BM25)

When a User asks a question, Sovereign Pair does not do a standard `CTRL+F` search. It executes a **Hybrid Context Fusion**.

### 2.1 The Math (Vector Search)
The system calculates the mathematical coordinate of your question. If you ask *"How to fix the car engine?"*, the system looks for document chunks stored geometrically near those coordinates (e.g., retrieving a manual about "automotive combustion repair"). This catches *intent*.

> [!NOTE] 
> ▫️ **BGE-M3 Geometric Axum Loader:** `src-rust/core/engine_builder.rs`

### 2.2 The Keyword (BM25 Search)
A pure mathematical search often fails with hyper-specific names like `"Error Code 0x88F7"`. The system executes a simultaneous old-school BM25 lexical keyword search to guarantee exact matches are not lost in the math.

> [!TIP]
> **Junior Hacker Fast-Track:**
> RAG (Retrieval-Augmented Generation) is essentially giving the AI an open-book test. Instead of answering from memory, the AI searches your private folders, copies the relevant paragraphs, pastes them into an invisible prompt, and then summarizes the answer for you.

> [!NOTE] 
> ▫️ **Custom Lexical Base (BM25):** `CustomBM25Retriever` class inside `src-rust/core/custom_retrievers.rs`.
> ▫️ **The Hybrid Retriever (RRF Semantic):** Instanced in `src-rust/core/engine_builder.rs`.

---

## 3. Cognitive Mapping (Glossary)

To understand Sovereign Pair's codebase, one must learn the nomenclature of its architecture:

| Term | Domain | Definition |
|---|---|---|
| **Sensus Vault** | Storage | The physical directory where your raw Markdown/PDF files rest. It is the "Brain" before it is mathematically digested. |
| **Node / Chunk** | RAG | A fractional piece of a document (e.g., 1024 tokens) returned natively directly from sqlite-vec mapping arrays. |
| **Orchestrator** | Infrastructure | The Cloud Server (e.g., Oracle OCI Free Node) running the Cognitive Routing Logic (PostgreSQL, N8N, and the Rust Axum API instances). It manages user connections but offloads heavy text inference to the external node. **[Living Code: Axios HTTP Resilience via `REQUEST_TIMEOUT="300.0"` in `.env`]** |
| **Inference Node** | Infrastructure | The external powerful hardware (e.g., Home Ryzen Desktop over VPN) operating pure graphical VRAM acceleration (Ollama/GGUFs), acting as a sheer processing worker for the Oracle Cloud. **[Living Code: Native Linux Kernel Hacks at `scripts/optimize_ollama_ryzen.sh`]** |
| **System Prompt** | AI Persona | The invisible preamble sent before every user question. It dictactes behavior (e.g., "You are The Sentinel. You must block hacks. Respond in Portuguese.") |
| **Cibrid (Cybrid)** | Topology | The architectural state of running Front-End code on a public Cloud, securely tunneled to heavy Back-End processing on private localized hardware via peer-to-peer mesh. |
