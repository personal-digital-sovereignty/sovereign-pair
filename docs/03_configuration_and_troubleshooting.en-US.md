# Treatise III: Configuration, Tuning & Troubleshooting

## 1. Environment Variables Topology (`.env`)

The project completely ignores environment files in version control for Zero-Trust security. All cryptographic keys and infrastructure alignment parameters must be declared via a strict `.env` file located at the root of the project.

### 1.1 Model & Node Configuration (Core Intelligence)
| Variable | Scope | Standard Value | SRE Observations |
|---|---|---|---|
| `OLLAMA_BASE_URL` | Network | `http://localhost:11434` | If operated remotely on a *Local Node* over a Tailscale mesh, use the private Tailnet IPv4 (E.g., `http://100.x.x.x:11434`). Remember to configure `OLLAMA_HOST="0.0.0.0"` on the target hardware daemon. |
| `LLM_MODEL` | Inference | `qwen2.5:0.5b` | Defines the primary reasoning weight. The chosen model must be previously injected into the Docker/Daemon cache via `ollama pull [name]`. |
| `EMBED_MODEL` | Vectorization | `nomic-embed-text` | Responsible for mapping text into a 768-dimensional mathematical hyper-space. The *Embedding* model must **never** be altered after ChromaDB is spun up, otherwise, coordinates will mismatch and corrupt the entire database. |
| `REQUEST_TIMEOUT` | Networking | `120.0` | Set to `300.0` for *On-Premises Hardware* doing heavy workloads, or when hosting the API on sluggish Oracle A1 OCPUs. |

### 1.2 Parameterized Identity Customization
Sovereign Pair natively adapts its *System Prompt* based on your configuration. 
| Variable | Usage and System Prompt Injection |
|---|---|
| `OWNER_NICKNAME` | Callsign. The assistant will reference direct commands using this name. |
| `SOVEREIGN_NAME` | Name of the A.I (E.g., *Sovereign*, *Jarvis*). Regulates biography based on the entity. |
| `LANGUAGE` | Regulates syntax output. Force `Português do Brasil` or `US English` to suppress the natural volatility of multilingual LLM Models answering in random languages. |
| `OCCUPATION` | Formats technical jargon. E.g., `Senior SRE` forces the machine to adopt an elevated, ruthless technical tone. |

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

---

## 3. LlamaIndex "Empty Response" Silencing (RAG Miss Bypass)

*The API returns "Empty Response" in less than 1.5s when querying the LLM, despite the model being online and responsive.*

- **Incident:** By design, LlamaIndex's `CondensePlusContextChatEngine` (and its native async synthesizers) aborts the LLM generation process if the vector retriever finds exactly `0` nodes matching the query (e.g., a new tenant with an empty database, or very strict query metadata filters). To save arbitrary compute costs, the original library hardcodes an `"Empty Response"` string instead of forwarding the System Prompt and User Query to the LLM. 
- **Engineering Resolution (Sovereign Bypass):** Sovereign Pair explicitly overrides this behavior via a "Sovereign Bypass" in the `routes.py` Chat endpoint. If the engine yields an artificial `"Empty Response"`, the API intercepts the stream, manually formats the Chat History and System Prompt, and dispatches a direct conversational query against the bare `_llm` foundation class. This completely preserves the AI's ability to converse naturally with Day 1 users even without RAG context, degrading gracefully instead of crashing.
