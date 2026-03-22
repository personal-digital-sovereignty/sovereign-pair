# Architectural Report: Hybrid Mesh Model Trainer & Knowledge Distillation

**Date:** March 2026
**Subject:** Sovereign Pair - Distributed Local Model Training & Mesh Inference
**Classification:** Public Architecture Documentation

---

## 1. Executive Summary
The **Sovereign Pair** architecture was fundamentally designed to solve the physical constraints of local AI execution (Limited VRAM & Low Compute on end-user devices). To achieve actual "Digital Sovereignty" without sacrificing intelligence, the application employs a **Hybrid Mesh Model Trainer**.

This architecture allows a lightweight local agent (e.g., Mac/Windows Laptop running the UI) to orchestrate complex operations—like Knowledge Distillation and LoRA Fine-Tuning—by transparently dispatching the heavy workloads to more potent nodes within the user's private Mesh network (e.g., an Oracle Cloud robust node or a local desktop workstation with dedicated GPUs).

## 2. Global Node Mesh (The Sovereign Cluster)
The Sovereign Core (`api_settings.rs` and `api_mesh.rs`) maintains an active index of all Ollama nodes available to the user. Each node registers its unique `URI`, physical computational profile, and installed models (`/api/tags`).

When a user opens the **Model Trainer** dashboard on their local device, the engine natively queries the active **Worker Node**.
- If the configured Active Node is `http://10.0.0.5:11434` (A remote Oracle Cloud server), the Model Trainer dynamically targets this remote instance.
- The UI's **Unsloth Monitor** stream receives Server-Sent Events (SSE) directly piped from the remote server's tensor sync status (`/api/create`), rendering real-time metrics locally as if the hardware were physically inside the user's laptop.

## 3. Knowledge Distillation: From 70B/GPT-4 to Local 3B
Knowledge Distillation within the Sovereign Pair is not merely symbolic; it is built on an orchestrated pipeline of data extraction and subsequent model replacement.

### Multi-Tier Distillation Scenarios

**Scenario A: Third-Party Teacher (GPT-4o) ➡️ Local Student (Llama 3.2 3B)**
The user can leverage proprietary intelligence to forge open-source localized sovereignty.
1. The user specifies `Teacher: gpt-4o` and `Student: llama3.2:3b`.
2. The Rust Sovereign Core securely queries OpenAI's API (using the user-provided KMS-encrypted API keys).
3. The engine extracts structural reasoning responses, forming a high-quality "Gold Dataset" directly into the local SQLite memory base (`sovereign_memory.db`).
4. This dataset is then fed back to the local Ollama instance to inject these capabilities through parameter adjustments or pre-prompt alignment logic, solidifying the external knowledge offline.

**Scenario B: Sovereign Remote Teacher (Llama 3 70B) ➡️ Local Student (Qwen 1.5B)**
For zero-trust environments, external APIs are completely bypassed.
1. A powerful Llama 3 70B model runs on an attached Mesh Node (e.g., AWS/Oracle Server).
2. The Model Trainer orchestrates generation requests across the VPN/Mesh tunnel, extracting logical deductions from the 70B teacher.
3. The derived datasets are pulled to the local node and utilized to train a highly optimized 1.5B/3B student model locally on the user's laptop.
4. The user achieves highly specialized offline reasoning capabilities without compromising privacy or relying on external endpoints.

## 4. Resilient Engineering Design
To ensure stability during heavy operations:
- **Asynchronous Task Pools**: Rust's `tokio::spawn` dispatches the HTTP requests to external Ollama APIs without blocking the main event loop.
- **Broadcast Channels**: `tokio::sync::broadcast` guarantees that the UI telemetry stream (Unsloth Monitor) survives brief network degradations during the tuning processes.
- **O.S Abstraction**: The `SettingsModal.svelte` dynamically reads model tags, treating both local binaries and remote Mesh instances identically. The UI does not differentiate between a local GPU and a connected supercomputer.

## 5. Conclusion
The Model Trainer is more than a UI wrapper; it is a **Distributed Sovereign AI Operating System**. It predicts a world where personal devices handle the orchestration, UI rendering, and private context manipulation, while raw tensor manipulation and intelligence extraction are effortlessly routed to wherever the silicon permits.
