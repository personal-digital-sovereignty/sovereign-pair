# Treatise V: Interoperability Protocol (API & MCP)

The Sovereign Pair project exposes its internal brain through two distinct protocols, catering both to corporate automation engineers and native software developers.

## 1. The REST API (HTTP & N8N Integration)

The primary entry point is the FastAPI application (`src/api/routes.py`), typically running on the Oracle Cloud Orchestrator. 

It provides synchronous and asynchronous endpoints optimized for standard webhooks. This is the **preferred method** when connecting Sovereign Pair to platforms like N8N, Make, or custom Vue.js frontends.

### 1.1 Key Endpoints
- `POST /v1/chat/completions`: The main conversational route. Accepts OpenAI-compatible payload structures (`messages: []`). This route automatically triggers the **Sovereign RAG** pipeline (BM25 + Vector Search) and applies the "Sovereign Bypass" if no context is found.
- `GET /v1/projects`: Scans the physical `Sensus Vault` directory and returns a JSON array of all currently ingested multi-tenant paths.
- `POST /v1/sys/stats`: Returns telemetry (RAM, VRAM, Uptime) from the Inference Node.

> [!WARNING]
> Due to the physical limitations of executing 7B parameter models on mid-tier hardware, standard HTTP webhook requests from N8N might take up to 3 minutes to return a response. Ensure your HTTP nodes are configured to ignore standard 60-second timeouts.

---

## 2. Model Context Protocol (MCP) Integration

Sovereign Pair natively exposes its internal engines (The Doctor, The Coder) and the `Sensus Vault` context through the open **Anthropic MCP Standard**. This capability transforms the backend into a "Local-First Cognitive Expansion Module" for corporate IDEs like VSCode, Cursor, and Cline (or OpenCode).

### 2.1. Absolute Local-First Sovereignty
Unlike REST APIs over HTTP, the MCP connection scheme operates strictly via **Stdio** (Standard Input/Output) Inter-Process Communication (IPC). The IDE initiates a silent, memory-based socket. Data **never traverses the network**, ensuring Zero-Trust code architecture. No tokens leak to the public internet.

### 2.2. IDE Client Setup (VSCode / Cline)
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

### 2.3. MCP Resources vs. Tools
Once the IDE connects to the `mcp_stdio.py` engine:
- **Resources:** The IDE can automatically command the AI to passively read any Markdown files stored inside your `Sensus Vault`. This grounds the AI in your company's proprietary architecture documents before it starts scaffolding code.
- **Tools:** The IDE gains the ability to "call" functions in Sovereign Pair. For example, triggering the `sensus_vault_search` tool allows the IDE's LLM to dynamically semantic-search your Vector Database for specific business rules mid-conversation.

> [!TIP]
> **Junior Hacker Fast-Track:**
> Think of MCP as a USB cable for AI. Instead of opening a web browser (HTTP) to ask ChatGPT a question, you plug the AI "cable" directly into your VSCode. Now the AI can read your code folders, search your local Vector Database, and write files for you, without ever sending your company's code to the cloud.
