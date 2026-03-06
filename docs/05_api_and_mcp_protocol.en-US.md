# Treatise V: Interoperability Protocol (API & MCP)

The Sovereign Pair project exposes its internal brain through two distinct protocols, catering both to corporate automation engineers and native software developers.

## 1. The REST API (HTTP & N8N Integration)

The primary entry point is the FastAPI application (`src/api/routes.py`), typically running on the Oracle Cloud Orchestrator. 

It provides synchronous and asynchronous endpoints optimized for standard webhooks. This is the **preferred method** when connecting Sovereign Pair to platforms like N8N, Make, or custom Vue.js frontends.

### 1.1 Key Endpoints
- `POST /v1/chat/completions`: The primary route and central cognitive engine. Accepts OpenAI-compatible payload structures (`messages: []`). This route automatically triggers the **Sovereign RAG** pipeline (BM25 + Vector Search) and applies the "Sovereign Bypass" to prevent system crashes on "Day Zero" (the exact moment of deployment when the ChromaDB vector store is still physically empty and no PDFs have been ingested).
- `GET /v1/projects`: Scans the layout of the root `Sensus Vault` directory and returns a JSON array mapping the Project subdirectories. These act as unbreakable logical containers to isolate Multiple Tenants.
- `POST /v1/sys/stats`: Consolidates and reports raw hardware telemetry (VRAM and OS memory consumption of the Inference Node), attesting to system robustness and Uptime.

> [!WARNING]
> Due to the physical limitations of executing 7B parameter models on mid-tier hardware, standard HTTP webhook requests from N8N might take up to 3 minutes to return a response. Ensure your HTTP nodes are configured to ignore standard 60-second timeouts.

> [!NOTE] 🧬 **Living Code: The Complete REST Route (SHA: `94bfb2f`)**
> ▫️ **Core Webhook Controller:** `src/api/routes.py`
> ▫️ **Application Init:** `src/api/main.py`
> ▫️ **God-Mode SPA (Vue.js):** Consuming natively from `src/ui/`

---

## 2. Model Context Protocol (MCP) Integration

The original LangGraph architecture (which trapped complex, inflexible graphs in the cloud API) was deprecated to natively expose the deep reasoning engines of its Agents (The Doctor, The Nurse, The Coder) through Anthropic's open **Model Context Protocol (MCP)**. The architectural and market appeal of this shift is clear: Instead of isolating intelligence within the RAG application's endpoint, it transforms the entire backend into a powerful "Skill Expansion Module". This umbilical cord dynamically plugs into modern corporate IDEs (VSCode, Cursor, Cline-based projects, and the upcoming *OpenCode* ecosystem).

### 2.1. Absolute Local-First Sovereignty
Unlike traditional Web REST APIs over HTTP—which can potentially leak packets interceptable via network *Sniffing* attacks—the MCP connection scheme operates strictly via **Stdio** (Standard Input/Output) Inter-Process Communication (IPC). The IDE initiates a blind socket bridge inside local RAM. Your proprietary corporate code architecture **will never traverse a routed network packet**, rendering the environment Zero-Trust and inviolable. **[Living Code: Pure IPC bind at `src/mcp_stdio.py`]**

### 2.2. IDE Client Setup (OpenCode / VSCode)
To inject the Sovereign Vault directly into your coding workflow (e.g., a VSCode integrated via OpenCode), utilize the configuration of the AI Assistant (widely known as *Cline* or its derivative forks). Simply tweak the local `cline_mcp_settings.json` file by appending:

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

### 2.3. MCP Resources vs. Tools
Once the IDE connects to the `mcp_stdio.py` engine:
- **Resources:** The coupled AI gains the astonishing passive ability to read the shielded Project subdirectories of your `Sensus Vault` and root itself in your business philosophy BEFORE attempting to scaffold generic boilerplate code based on biased hallucinations from external SaaS platforms. **[Living Code: Passive capability via `@mcp.resource()`]**
- **Tools:** The AI running inside your IDE suddenly gains corporate superpowers tied to programmable live Python functions. By calling the `sensus_vault_search` logic, the IDE's agent can scan the Sovereign ChromaDB vector store in the middle of a CSS task just to retrieve and consult vital business guidelines hidden within a legacy Requirements PDF. **[Living Code: Exposed capability via `@mcp.tool()`]**

> [!TIP]
> **Junior Hacker Fast-Track:**
> Think of MCP as a USB cable for AI. Instead of opening a web browser (HTTP) to ask ChatGPT a question, you plug the AI "cable" directly into your VSCode. Now the AI can read your code folders, search your local Vector Database, and write files for you, without ever sending your company's code to the cloud.

> [!NOTE] 🧬 **Living Code: The Anthropic MCP Server (SHA: `94bfb2f`)**
> ▫️ **Local IPC Engine (Stdio Server):** `src/mcp_stdio.py`
> ▫️ **Assistant Client Config (Cline):** `cline_mcp_settings.json`
