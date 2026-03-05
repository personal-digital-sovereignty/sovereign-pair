melqu# Corporate Configuration and Troubleshooting Guide

**Status:** Production (Cibrid & Zero-Trust)
**Engine:** Sovereign API (FastAPI) & Sensus Vault
**Basic Requirements:** Python `3.11` or `3.12` (Python 3.14 unsupported due to Pydantic V1). 

This manual is intended for SRE Engineers and System Administrators responsible for the configuration and sustainment of the Sovereign Pair RAG, covering the partitioning of environment variables (`.env`) and common failure mitigation protocols.

---

## 1. Environment Variables Topology (`.env`)

The project does not track environment files. All cryptographic security and infrastructure alignment must be declared via a strict `.env` allocated at the root of the project.

### 1.1 Model Configuration (Core Intelligence)
| Variable | Scope | Standard Use | SRE Observations |
|---|---|---|---|
| `OLLAMA_BASE_URL` | Network | `http://localhost:11434` | If operated remotely on a *Local Node* of the Tailscale network, use the Tailnet IPv4 (E.g., `http://100.x.x.x:11434`). Remember to configure `OLLAMA_HOST="0.0.0.0"` on the target daemon. |
| `LLM_MODEL` | Inference | `llama3.2` or `qwen` | Defines the primary computational weight. The chosen model must be previously injected into the Docker/Daemon cache (`ollama pull [name]`). |
| `EMBED_MODEL` | Vectorization | `nomic-embed-text` | Responsible for mapping into a 768-dimensional hyper-space. The *Embedding* model must never be altered after ChromaDB is spun up, otherwise, corrupted hashes will void the database. |
| `REQUEST_TIMEOUT` | Networking | `120.0` | Set to `180.0` for *On-Premises Hardware* or on Oracle Free Tier clouds (generic low-processing A1.Flex). |

### 1.2 Vector Database Mechanics and Context
| Variable | Scope | Recommended | Behavior |
|---|---|---|---|
| `CHROMA_COLLECTION_NAME` | RAG | `sovereign_knowledge` | Isolation by *namespaces*. Allows multi-tenant RAGs on the same node pointing to distinct IPs. |
| `CHUNK_SIZE` | Parsing Text | `1024` | Physical size of Tokens absorbed prior to fractionation. Ideal for `nomic`. |
| `CHUNK_OVERLAP` | Parsing Text | `200` | Marginal elastic memory so as not to sever logical topics in the Vector transition. |
| `MAX_WEB_SEARCH_RESULTS` | Cibrid | `3` | Defines Scraping volume for injection via Web Search. Larger volumes demand higher Timeouts. |

### 1.3 Parameterized Identity Customization
| Variable | Usage and System Prompt Injection |
|---|---|
| `OWNER_NAME` | Your corporate name. Triggers a formal greeting from the RAG. |
| `OWNER_NICKNAME` | Nickname or *Callsign*. The assistant will reference direct commands this way. |
| `SOVEREIGN_NAME` | Name of the A.I (E.g., *Sovereign*, *Jarvis*). Regulates biography based on the entity. |
| `LANGUAGE` | Regulates output. Force `Português do Brasil` or `US English` to suppress the natural volatility of multilingual LLM Models. |
| `GEOLOCATION` | Static baseline for Search Queries. E.g., `São Paulo, Brasil`. Replaces native Browser coordinate submission needs. |
| `OCCUPATION` | Formats jargon. E.g., `Senior SRE` forces the machine to adopt an elevated technical tone. |

---

## 2. Gold Standards for Troubleshooting

Network problems and Vector collapses are mitigable by following strict tracking matrices. Never delete databases without prior isolation of logs.

### 2.1 Vectorial Collapse (`input length exceeds the context length`)
*ChromaDB Status 400 Error.*
- **Incident:** The Embedding model rejects dense packets whose embedded characters violated the local model's Token Limit (Common in documents converted from PDF/OCR).
- **Engineering Resolution:** 
  1. In the `.env`, reduce volumetry by shrinking `CHUNK_SIZE` (Roll back to `512` in worse cases, and fall back to `128` if the model so requests, as in the case of `all-minilm`).
  2. Submit a new Ingestion scan after clearing the `data/.ingestion_history.json` flag.

### 2.2 Zero-Trust Disconnection with Ollama (Timeout or TCP Refusal)
*The UI freezes trying to invoke the FastAPI endpoint generating `500 Internal Server`.*
- **Incident:** The Inference node (Ryzen Gamer Machine) detaches from the Orchestrator Node (Oracle Cloud) or vice versa.
- **Engineering Resolution:**
  1. Obtain *shell* via `tailscale ping [Node]`. If it doesn't ping, the underlying barrier was sporadically cut by cooling, ISP error, or ACL.
  2. Ensure the Inference server initiated the Docker Ollama mapping the Gateway. The default `OLLAMA_HOST` parameter in SystemD distributions unviable external NATing.
  3. On Inference Linux: Add a `/etc/systemd/system/ollama.service.d/override.conf` file containing `Environment="OLLAMA_HOST=0.0.0.0"`.

### 2.3 Python Mismatch Issues
*Syntax Warnings in Pydantic upon uvicorn backend Boot up.*
- **Incident:** The project attempted to run natively on Python `>= 3.13` or higher, forcing breakage in *Legacy* libraries (such as the ChromaDB engine).
- **Engineering Resolution:** The corporate environment rules complete pack isolation. Abort failed environments, invoke `pyenv` installing the strict 3.12.x *patch* branch, and recreate your V-Env `python3.12 -m venv .venv` ignoring the global Host machine.

### 2.4 Incremental State Corruption (Divergent Hashes)
*The scan says the file does not exist, but Markdown viewer on the UI proves otherwise.*
- **Incident:** Detachment between the Historical `.json` database and the native `ChromaDB` indexing. (Usually caused by accidental *Hard Resets* during vectorization).
- **Engineering Resolution:** Reset the vector brain.
```bash
# SRE Runbook: Absolute Vector DB Purge.
rm -rf data/chroma_db
rm data/.ingestion_history.json
python src/ingest.py # Enforce the Manual Full parameter
```

## 3. Analytical Logs
All API Engine telemetry rolls through `stdout`. Chain with corporate *Log-Rotation* managers. For densified Reasoning logs (Agent *Thoughts*), inject `AGENT_VERBOSE=true` in the env. The A.I will begin to "Talk to itself" in console output, exposing its *ReAct* flowchart for advanced Cibrid debugging.

---

## 4. Model Context Protocol (MCP) Integration

Sovereign Pair natively exposes its internal engines (The Doctor, The Nurse) and the `Sensus Vault` context through the Anthropic **MCP Standard**. This capability transforms the backend into a "Local-First Cognitive Expansion Module" for corporative IDEs like VSCode, Cursor, and Cline (or OpenCode).

### 4.1. Absolute Local-First Sovereignty
The connection scheme operates strictly via **Stdio** (Standard Input/Output) Inter-Process Communication (IPC). The IDE initiates a silent, memory-based socket. Data **never traverses the network**, ensuring Zero-Trust code architecture.

### 4.2. IDE Client Setup (VSCode / Cline)
To inject the Sovereign Vault directly into your coding workflow, append the following block to your IDE's MCP Configuration JSON (`settings.json` or Cline setup):

```json
"mcpServers": {
  "sovereign-pair": {
    "command": "python",
    "args": ["-m", "src.mcp_stdio"],
    "env": {
      "PYTHONPATH": "/absolute/path/to/sovereign-pair"
    }
  }
}
```

### 4.3. Usage
Once connected, the Agent within the IDE will automatically read the `VAULT_DIR` Markdown files (*Resources*) prior to scaffolding architectures and can dynamically query the Vector Database (*sensus_vault_search tool*) to fetch custom business rules, shielding your local proprietary code from generic LLM Internet hallucinations.