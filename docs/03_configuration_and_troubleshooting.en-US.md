# Treatise III: Configuration, Tuning & Troubleshooting

## 1. Environment Variables Topology (`.env`)

The project completely ignores environment files in version control for Zero-Trust security. All cryptographic keys and infrastructure alignment parameters must be declared via a strict `.env` file located at the root of the project.

### 1.1 Model & Node Configuration (Core Intelligence)
| Variable | Scope | Standard Value | SRE Observations |
|---|---|---|---|
| `OLLAMA_BASE_URL` | Network | `http://localhost:11434` | If operated remotely on a *Local Node* over a Tailscale mesh, use the private Tailnet IPv4 (E.g., `http://100.x.x.x:11434`). Remember to configure `OLLAMA_HOST="0.0.0.0"` on the target hardware daemon. |
| `LLM_MODEL` | Inference | `qwen2.5:0.5b` | Defines the primary reasoning weight. The chosen model must be previously injected into the Docker/Daemon cache via `ollama pull [name]`. |
| `EMBED_MODEL` | Vectorization | `bge-m3` | Responsible for mapping text into a 1024-dimensional mathematical hyper-space with deep Multilingual cognitive support. **Hardware Trade-off:** If you require extreme ingestion speed on mid-tier local hardware (e.g., Ryzen 7 5800H + 32GB RAM routing ZRAM on ArchLinux), you can downgrade to `nomic-embed-text` (768 dimensions). It is ~3x faster but heavily English-biased, forcing the system to lose cross-lingual indexing accuracy. The *Embedding* model must **never** be altered after ChromaDB is spun up, or it will corrupt the entire database structure entirely. |
| `REQUEST_TIMEOUT` | Networking | `120.0` | Set to `300.0` for *On-Premises Hardware* doing heavy workloads, or when hosting the API on sluggish Oracle A1 OCPUs. |

> [!NOTE] 🧬 **Living Code: Environment Config Matrix (SHA: `94bfb2f`)**
> ▫️ **Pydantic Validation Node:** `src/api/config.py`
> ▫️ **Model Builders (Llama/BGE-M3):** `src/engine_builder.py`

### 1.2 Parameterized Identity Customization
Sovereign Pair natively adapts its *System Prompt* based on your configuration. 
| Variable | Usage and System Prompt Injection |
|---|---|
| `OWNER_NICKNAME` | Callsign. The assistant will reference direct commands using this name. |
| `SOVEREIGN_NAME` | Name of the A.I (E.g., *Sovereign*, *Jarvis*). Regulates biography based on the entity. |
| `LANGUAGE` | Regulates syntax output. Force `Português do Brasil` or `US English` to suppress the natural volatility of multilingual LLM Models answering in random languages. |
| `OCCUPATION` | Formats technical jargon. E.g., `Senior SRE` forces the machine to adopt an elevated, ruthless technical tone. |

> [!NOTE] 🧬 **Living Code: The Identity Forge (SHA: `94bfb2f`)**
> ▫️ **System Prompt Factory:** Function `build_chat_engine()` inside `src/engine_builder.py`. It dynamically merges these DB variables into the LLM logic at runtime.

---

## 2. SRE Runbook for ChromaDB Collapses

Network drops and Vector collapses are completely mitigatable by following strict tracking matrices. **Never** delete databases without prior isolation of logs.

### 2.1 Incremental State Corruption (Divergent Hashes)
*The scan says the file does not exist, but the Markdown viewer on the UI proves otherwise.*
- **Incident:** Detachment between the Historical `.json` hashing database and the native `ChromaDB` sqlite indexing. Usually caused by accidental *Hard Resets* or power outages during bulk vectorization.
- **Engineering Resolution:** Nuke and reset the vector brain. No data is lost because the true files remain safe in your `Sensus Vault` directory. Sovereign pair will simply rebuild the math.

```bash
# SRE Runbook: Absolute Vector DB Purge.
rm -rf data/chroma_db
rm data/.ingestion_history.json
# Restart the container or run the manual ingest script
python src/ingest.py 
```

> [!NOTE] 🧬 **Living Code: Math Reconstruction Engine (SHA: `94bfb2f`)**
> ▫️ **Vector Healing Script:** The core logic inside `src/ingest.py` (Handles parsing and deduplication across Chroma).

---

## 3. Historic Dependency Vulnerability: The "LlamaIndex Empty Silencing"
Early prototypes of the Sovereign framework leaned on commercial SDK wrappers (like LlamaIndex and LangChain configurations). During active deployment audits, a critical restriction surfaced linking open-source structures to Cloud vulnerabilities.

- **Incident:** By design, LlamaIndex's Python classes evaluated query operations against databases. If exactly `0` nodes returned a match, the codebase aborted inference and transmitted a hardcoded `Empty Response` text string towards clients—or worse, executed silent fallbacks attempting external OpenAI networking (breaking the zero-trust mesh isolation policies).
- **The Sovereign Solution (Rust Migration):** Addressing the inherent flaws exposed by the standard commercial API routing logic, the `Sovereign Bypass` methodology originally mitigated empty response bugs using fallback logic wrappers (`astream_chat( )`). Ultimately, engineering dismantled the Python dependency structures. The entire internal system routing, API mapping, and logic validation RAG structure currently executes over **Rust compiled binaries (Axum/Tokio)** ensuring direct queries over mapped vectors without vendor abstractions. Cibrid networks now process bare-metal LLM prompts deterministically handling unstructured scenarios perfectly avoiding logic crashes unconditionally.

> [!NOTE] 🧬 **Living Code: The Sovereign Bypass Engine (SHA: `94bfb2f`)**
> ▫️ **Root Cause & Reference:** Known rigid behaviors in legacy `LlamaIndex` Python implementations preventing infinite loops. Resolved internally shifting backend control dynamically via C++ and Rust compilation components overriding API vendor lock-ins.
