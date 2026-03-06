# Treatise II: Deployment & Infrastructure Operations

## 1. Zero-Cost Omnipresent Architecture (OCI Free Tier)

Sovereign Pair was engineered to be financially invisible. While its core engine (the LLM reasoning) demands heavy processing, the orchestrator (API, RAG Router, Auth, and N8N webhook gateway) is designed to run on **ARM64 architectures with severely constrained resources**.

You can orchestrate your entire digital brain on an **Oracle Cloud Infrastructure (OCI) Ampere A1 Compute Instance**, which provides 4 ARM OCPUs and 24GB of RAM perpetually for $0.00/month.

### 1.1 The Docker-Compose Symphony

The entire stack is containerized. No host dependencies are required beyond Docker and a mesh VPN.

1.  **FastAPI Backend (`sovereign-api`):** The beating heart. It receives NLP queries, parses RAG tokens in Python 3.12, and orchestrates the Multi-Tenant context.
2.  **ChromaDB Vector Store (`chroma`):** The isolated spatial memory. It stores embeddings in immutable flat files mapped directly to the local disk.
3.  **N8N Automations (`n8n`):** The limbs. Connects to the real world (webhooks, email parsing, calendar syncing), triggering the Sovereign API when automation requires reasoning.
4.  **Redis (`redis`):** High-speed ephemeral cache used exclusively to mediate the Queue Mode for N8N horizontal scaling.
5.  **PostgreSQL (`postgres`):** The persistence layer for session chats, system prompts, and configuration data.

> [!TIP]
> **Junior Hacker Fast-Track:**
> *Docker* is just a magical box. Instead of installing Python, Postgres, Redis, and dozens of libraries on your PC (and inevitably breaking an update), Docker runs a mini-computer for each service safely inside a locked box. To start the entire infrastructure, you only type `docker-compose up -d`.

---

## 2. Zero-Trust Networking (The Gatekeeper)

When deploying on the public internet (like an Oracle Cloud VPS), **never** expose ports `8000` (API), `5678` (N8N), or `8000` (Chroma) to the public web (WAN/IGW). 

Sovereign Pair relies on a Mesh VPN (e.g., **Tailscale** or ZeroTier) to act as a cryptographic gatekeeper. 

### 2.1 The Cybrid Connection (Cloud to Home)
1. Install Tailscale on the Oracle VPS (The ARM Inference Node).
2. Install Tailscale on your Home PC/Laptop (The Vault Orchestrator).
3. Both machines will receive a private `100.x.x.x` IPv4 address.
4. In your VPS `docker-compose.yml`, bind the exposed ports strictly to the Tailnet IP.
   * *Example:* `ports: ["100.x.x.x:11434:11434"]`
5. Since the exact core of the project (Sensus Vault, API, N8N, ChromaDB) lives hyper-securely inside your **Physical Local Machine**, you will offload heavy LLM computation to the cloud to save laptop battery. Edit your local PC's `.env`, setting `OLLAMA_BASE_URL` to point to the Oracle VPS Tailscale IP (`http://100.y.y.y:11434`).

> [!WARNING]
> By default, the `ollama` daemon binds to `127.0.0.1` (localhost). It will reject connections from the Cloud Orchestrator. You must configure Ollama on your home PC to bind globally by executing `OLLAMA_HOST=0.0.0.0 ollama serve`. Do this **ONLY** if your Home PC's physical router blocks incoming external traffic.

---

## 3. Hardware Inferencing Limits (Trade-offs)

### The Cloud Inference Node (OCI ARM A1 Flex OCPU)
- **Role:** Remote worker purely offloaded to execute heavy neural/cognitive loads (`Ollama`). It acts as the predictive mind for high-level agents (The Doctor / The Coder).
- **Limit:** Being an ARM architecture without GPUs/NPUs, it strictly requires `ZRAM` (high-compression Linux swap) to handle 24GB+ of Heavy Quantized Models without kernel panics.
- **Config:** Achieves validated engineering metrics of ~6.3 Tokens/Second running dense code models (e.g., `qwen2.5-coder:7b`).

### The Vault Orchestrator (Physical PC / Home Laptop)
- **Role:** The Zero-Trust Fortress. Fiercely guards your PDFs ("Sensus Vault"), ChromaDB Vector index, and executes standard HTTP/RAG logic (FastAPI, N8N).
- **Limit:** Designed to preserve local battery and IDE performance. Running AI background daemons constantly on your development machine drains resources brutally.
- **Config:** Quickly ingests and retrieves data locally, only parsing the text inference securely through the Cloud Tailscale mesh when reasoning is inherently needed, sparing your physical GPU.

> [!NOTE]
> If a developer connects the Sovereign API to a weak hardware node and the LLM takes 4 minutes to generate a response, the N8N HTTP Request node (or a typical browser) will drop the connection via an `Axios Timeout`. To mitigate this, we inject an absolute upper limit of `REQUEST_TIMEOUT="300.0"` in our API logic. It ensures the Orhcestrator explicitly waits 5 minutes before throwing a `500 Internal Server Error`.
