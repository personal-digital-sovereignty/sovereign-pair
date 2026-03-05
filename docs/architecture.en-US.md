# Sovereign Pair - Hybrid Systems Architecture (Cibrid)

**Topology Version:** 3.3.0
**Document Classification:** Engineering & Infrastructure Operations (SRE)
**Focus:** On-Premises RAG, Orchestrator Node (OCI), and Zero-Trust Networks.

This official compendium details the topological blueprint of Sovereign Pair. It is intended for Solutions Architects and Site Reliability Engineers (SREs) responsible for extending or auditing the Retrieval-Augmented Generation (RAG) infrastructure in mission-critical scenarios.

---

## 1. Macro Topology: The Cibrid Paradigm

The architecture transcends monolithic Node applications, branching into two symbiotic and independent execution planes unified by a Software-Defined Network (SDN) mesh. The dense computational cost layer operates under an *Intranet/Air-Gapped* (*On-Premises*) premise, while resilience and API orchestration run lightly on High-Availability nodes in a public cloud (Oracle OCI).

### 1.1 Dense Inference Plane (On-Premises / Deep Compute)
- **Location:** Workstations with Parallel Tensor Accelerators (Local AMD/NVIDIA GPUs - Min: 8GB VRAM).
- **Engines:**
  - **Ollama Daemon:** Native C++ memory allocation engine (Llama.cpp) resident on port `11434`. Operates entirely Offline (Air-Gapped), free of egress traffic to the internet.
  - **ChromaDB Vector Store:** Operates on the *PersistentClient* protocol using the physical tree `data/chromadb` targeting local SSD/NVMe drives for massive parallel Embeddings writes. It handles the core matrix of dense semantic collections overlaying zero cloud cost and zero external transit.

### 1.2 Coordination and Orchestration Plane (OCI Cloud Free Tier)
- **Location:** Oracle Public Cloud (Node Compute A1 Flex - ARM64 / 24GB RAM).
- **Engines:**
  - **RAG Microservice (FastAPI/Uvicorn):** *Stateless* app built purely with Pydantic V2 dependency injection acting as a Gatekeeper in the communication between frontends, analogue engines (N8N), and the local GPU base.
  - **Ephemeral Transactional Database (SQLite/PostgreSQL):** Stores only session states, related to prompts and relational keys to the physical local Vault generated in OCI.
  - **Frontend SPA (Vue3 Proxy):** Delivered through Caddy/Nginx Servers acting purely as an optimized cache.

---

## 2. Network Patterns and Cryptographic Security (Zero-Trust)

The integration between the *On-Premises* (inference) and *Cloud* (orchestration/APIs) poles refutes port forwarding over the TCP protocol on the public internet (`0.0.0.0`), which would violate the law of open attack surfaces.

### 2.1 Encrypted WireGuard Mesh (Tailscale mTLS)
The architectural glue between the Cloud Node and the GPU Workstation is the virtual IP subsystem managed by Tailscale. 
Traffic flows point-to-point encrypted (e2e) in a UDP/Wireguard wrapper. 
The applications (FastAPI in the Cloud listening to the DB in the Cloud) and the requested GPU *On-Premises* "think" they are hosted on the same physical `100.x.x.x` LAN subnet, which completely suppresses cognitive overloads when crafting complex firewalls and dangerous DMZs in the cloud. There is no need for expensive reverse Static IPs.

### 2.2 API Traffic Control (Inbound/Outbound)
Any traffic extrinsic to the mesh requesting communication (e.g., A user's Web device) runs into *Rate Limiters*, strict transversal *CORS* rules (only origins vetted in the *Allowed Origins*), and the imperative Bearer verification with Signatures based on Strong Operational Secret.

---

## 3. The Intelligent Hybrid Ingestion Pattern (RAG Pipeline)

To neutralize *Critical Hallucinations* and *Temporal Blindness* (where the LLM invents facts or ignores crucial dates passed in chats), the engine abandons the trivial flawed technique of isolated Cosine Simulation, deploying a densified Hybrid Search Architecture pattern.

### 3.1 Real-Time Search Routing
1. **Query Trigger:** Upon crossing the RESTful APIs and triggering the `engine_builder` module, the subsystem fragments the user's request.
2. **Simultaneous Relational Evaluation (Optimized TDD):** Two separate indexing trees are scanned in parallel by Threads.
   - The *Vector Indexer* (ChromaDB) translates philosophical and fluid semantic concepts.
   - The *BM25 Custom Retriever* translates positional rigor (raw words, log UUIDs, identical fiscal numbers in reports).
3. **Statistical Fusion:** Conflicting scores concerning the same retrieved documents across the 2 instances undergo modeling via the Reciprocal Rank algorithm. Only the Top-*K* most qualified (adjusted from ~15 down to 5 nodes for economy under extreme VRAM loads) cross over alive for injection assembly within the "Context Window" tied to the live stream feeding down to the LLM.

---

## 4. Folder-Based Orchestration (Vault Session Storage)

Instead of adopting structures based on hyper-normalized Foreign Keys (Which inflame logic flaws and asynchronous distributed transactions in SQLite), the "Contextual String Metadata" Design Pattern was adopted.

In the `chat_sessions` relational table of the system, a sole `folder_name` column ensures the categorization of projects, chats, and focus areas. If `null`, the node inhabits the general base. This converts the processing of building the Organizational Logic Tree in the Front-End Framework into something computed in the RAM of the browser nodes upon API rendering read, relieving the physical stress on the local database of being taxed with complex and useless Joins, preserving lightning-fast I/O in micro-transactional time.

---

## 5. Model Context Protocol (The IDE Cognitive Expansion)

Beyond consuming the Cibrid RAG mesh via Web UI, the 3.3.0 topology adopts the Anthropic **MCP (Model Context Protocol)** standard. This positions the Sovereign Pair as a passive context expansion module for reverse software engineering.

### 5.1 Stdio Architecture (Standard I/O)
Clients and autonomous coding agents attached to IDEs (e.g., OpenCode, Cline, or Cursor) invoke the `src/mcp_stdio.py` binary. The Sovereign Pair initializes a `JSON-RPC` communication loop via standard input and output (RAM/Local Socket).
- **Zero-Trust Isolation:** The IDE Agent does not make external network calls or listen to LAN ports;
- **Sensus Resources:** The `VAULT_DIR` base is natively mirrored to the IDE, instructing worker AIs (The Coder) on the business rules written in Obsidian prior to code submission.
- **Integrated Tools:** The local Agent can trigger manual semantic searches in ChromaDB via the `sensus_vault_search` Tool without violating the corporate Sandbox.

---

**Referenced Technical Glossary:** See `docs/glossary.en-US.md`.