# Treatise V: Interoperability Protocol (API & MCP)

The Sovereign Pair project exposes its internal brain through two distinct protocols, catering both to corporate automation engineers and native software developers.

## 1. The REST API (HTTP & N8N Integration)

The primary entry point is the native Rust Axum application (`src-rust/main.rs`), typically running on the Oracle Cloud Orchestrator or local instances. 

It provides synchronous and asynchronous endpoints optimized for standard webhooks. This is the **preferred method** when connecting Sovereign Pair to platforms like N8N, Make, or custom Svelte frontends.

### 1.1 Key Endpoints
- `POST /v1/chat/completions`: The primary route and central cognitive engine. Accepts OpenAI-compatible payload structures (`messages: []`). This route automatically triggers the **Sovereign RAG** pipeline (BM25 + Vector Search) and applies the "Sovereign Bypass" to prevent system crashes on "Day Zero" (the exact moment of deployment when the `sqlite-vec` vector indexing table is still physically devoid of data and no PDFs have been ingested).
- `GET /v1/projects`: Scans the layout of the root `Sensus Vault` directory and returns a JSON array mapping the Project subdirectories. These act as unbreakable logical containers to isolate Multiple Tenants.
- `POST /v1/sys/stats`: Consolidates and reports raw hardware telemetry (VRAM and OS memory consumption of the Inference Node), attesting to system robustness and Uptime.

> [!WARNING]
> Due to the physical limitations of executing 7B parameter models on mid-tier hardware, standard HTTP webhook requests from N8N might take up to 3 minutes to return a response. Ensure your HTTP nodes are configured to ignore standard 60-second timeouts.

> [!NOTE] 
> ▫️ **Core Webhook Controller:** `src-rust/main.rs`
> ▫️ **Application Init:** Cargo Binary
> ▫️ **God-Mode SPA (Svelte):** Consuming natively from `src/ui/`

---

## 2. Model Context Protocol (MCP) Integration

The original LangGraph/Rust architecture (which trapped complex, inflexible graphs in the cloud API) was completely decommissioned to natively expose the deep reasoning engines of its Agents (The Doctor, The Nurse, The Coder) through Anthropic's open **Model Context Protocol (MCP)** via optimized C++ and Rust dependencies. The architectural and market appeal of this shift is clear: Instead of isolating intelligence within the Rust application's endpoint, it transforms the entire backend into a powerful "Skill Expansion Module". This umbilical cord dynamically plugs into modern corporate IDEs (VSCode, Cursor, Cline-based projects, and the upcoming *OpenCode* ecosystem).

### 2.1. Absolute Local-First Sovereignty
Unlike traditional Web REST APIs over HTTP—which can potentially leak packets interceptable via network *Sniffing* attacks—the MCP connection scheme operates strictly via **Stdio** (Standard Input/Output) Inter-Process Communication (IPC). The IDE initiates a blind socket bridge inside local RAM. Your proprietary corporate code architecture **will never traverse a routed network packet**, rendering the environment Zero-Trust and inviolable. **[Living Code: Pure IPC bind at `src-rust/mcp_stdio.rs`]**

### 2.2. IDE Client Setup (OpenCode / VSCode)
To inject the Sovereign Vault directly into your coding workflow (e.g., a VSCode integrated via OpenCode), utilize the configuration of the AI Assistant (widely known as *Cline* or its derivative forks). Simply tweak the local `cline_mcp_settings.json` file by appending:

```json
"mcpServers": {
  "sovereign-pair": {
    "command": "cargo",
    "args": ["run", "--release", "--bin", "sovereign-mcp-server"],
    "env": {
      "RUST_LOG": "info",
      "CARGO_MANIFEST_DIR": "/absolute/path/to/sovereign-pair"
    }
  }
}
```

### 2.3. MCP Resources vs. Tools
Once the IDE connects to the `mcp_stdio.rs` engine:
- **Resources:** The coupled AI gains the astonishing passive ability to read the shielded Project subdirectories of your `Sensus Vault` and root itself in your business philosophy BEFORE attempting to scaffold generic boilerplate code based on biased hallucinations from external SaaS platforms. **[Living Code: Passive capability via `@mcp.resource()`]**
- **Tools:** The AI running inside your IDE suddenly gains corporate superpowers tied to programmable live Rust functions. By calling the `sensus_vault_search` logic, the IDE's agent can scan the Sovereign `sqlite-vec` index mechanism in the middle of a CSS task just to retrieve and consult vital business guidelines hidden within a legacy Requirements PDF. **[Living Code: Exposed capability via `@mcp.tool()`]**

> [!TIP]
> **Junior Hacker Fast-Track:**
> Think of MCP as a USB cable for AI. Instead of opening a web browser (HTTP) to ask ChatGPT a question, you plug the AI "cable" directly into your VSCode. Now the AI can read your code folders, search your local Vector Database, and write files for you, without ever sending your company's code to the cloud.

> [!NOTE] 
> ▫️ **Local IPC Rust Engine (Stdio Server):** `src-rust/mcp_stdio.rs`
> ▫️ **Assistant Client Config (Cline):** `cline_mcp_settings.json`

---

## 3. The OpenCode Ecosystem (TUI & Pair Programming)

**OpenCode** has been officially integrated into the Sovereign Pair ecosystem to offer an express proxy to VS Code. Through this integration, all your IDE typing flows through an *OpenAI-Compatible* Proxy directly into the Hybrid Cibrid RAG (Local Ollama or the remote *"The Coder"* running on a high-density Oracle node) without ever touching the Internet.

### 3.1 Setup and Binding
To install and mirror Sovereign Pair's power into your Visual Studio Code using the OpenCode Terminal User Interface (TUI):

1. **Install the Underlying Binary:**
   On Arch Linux (or via your corresponding package manager):
   ```bash
   sudo pacman -S opencode
   ```
2. **Install the Magic Extension in your IDE:**
   Go to your VS Code Extensions, search for and install the official `OpenCode` package (SST developer). This sets up the "Command Unit" in your sidebar.
3. **Plant the Isolating JSON File (`opencode.json`):**
   In the absolute root of the Workspace you want to analyze (like inside the `sovereign-pair` repo itself or `home-organizer` projects), create a file named `opencode.json`:
   
   ```json
   {
       "$schema": "https://opencode.ai/config.json",
       "provider": {
           "sovereign-local": {
               "npm": "@ai-sdk/openai",
               "name": "Sovereign Pair Local Gateway",
               "options": {
                   "baseURL": "http://localhost:8000/v1/opencode",
                   "apiKey": "sovereign-local"
               },
               "models": {
                   "qwen2.5-coder:7b": {
                       "name": "Local NPU/GPU Worker"
                   },
                   "coder": {
                       "name": "Sovereign The Coder (Oracle Remote Node)"
                   }
               }
           }
       }
   }
   ```
   }
   ```

### 3.2 CLI Command Line Express Bypass (OS Variables)
Alternatively, if the developer strictly prohibits coupling static `opencode.json` files within corporate repositories aiming for absolute *Zero-Trust*, it is perfectly logical to "trick" the OpenCode engine. This trick is done by injecting the Sovereign host through O.S Environment Variables (OpenAI Native Pattern) directly upon terminal invocation:

```bash
# Strict Proxy Base Native Injection (OpenAI Bypass)
OPENAI_BASE_URL="http://localhost:8000/v1/opencode" OPENAI_API_KEY="sovereign-local" opencode
```
This terminal execution immediately suppresses the web routes natively coded into the extension/CLI, forcing 100% of the Coder's telemetry and payload flows against the local Rust Axum validations.

### 3.3 Systemic Invocation within the Environment (IDE Terminal)
Once the backend servers are compiled and roaring natively via Cargo Build / Axum Local on port `8000`, you can trigger the OS calls straight into the native sub-terminal (using customized shortcuts *e.g., Ctrl+Esc* inside your IDE). This roots pure local physical constraints natively bypassing external endpoints—allowing the generation of hyper-private code iterations free from WAN commercial API constraints.
