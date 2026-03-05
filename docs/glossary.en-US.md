# Sovereign Pair - Corporate Glossary

This document consolidates the architectural terms and technical protocols employed in the Sovereign Pair ecosystem. Its objective is to baseline engineers and operators on a unified understanding of the system, acting as the foundation for all User Manuals, Deployment Guides, and Architecture Documentation.

## Core Architecture Terminology

### Sovereign Pair
The complete Artificial Intelligence orchestration suite composed of the immersive local interaction interface (Vue3), multi-model RAG inference engines on the edge (Local GPU/Metal), and cloud automation instances (OCI). The ecosystem promotes absolute digital sovereignty for the user over their data, abdicating from third-party telemetry or ingestion (Zero-Knowledge).

### Cibrid (Cloud-Hybrid)
Deployment model where the heaviest layer of matrix calculations or lifetime storage (LLMs, Vector Ingestion, and Vault) is strictly hosted "On-Premises" on the user's physical machine (e.g., Workstation with Local GPU), while the coordination interface, queues, and message-brokers transparently operate lightly on free cloud instances (Oracle OCI A1 Flex).

### Zero-Trust / Darknet
Applies to the Tailscale network model operated at the system's core. Operational Cibrid engines (N8N, Redis, APIs, and Ollama) never expose direct listening ports to the public internet (`0.0.0.0` at the Ingress/IGW). The entire data flow runs exclusively through the internal VPN (e.g., `100.x.x.x` addresses of the Mesh topology), ensuring that connections without validated certificates and unauthorized nodes are intrinsically discarded at the lowest layer of the network.

## Intelligence Engine Components

### RAG (Retrieval-Augmented Generation)
Architecture that retrieves local documents before Llama infers any sentence. Prevents hallucinations by forcing the semantic engine (LLM) to strictly read the vector facts extracted from the user's Vault (Sensus).

### BM25 & Hybrid Search
Combinatorial ranking method that solves mathematical flaws of cosine similarity. Sovereign Pair merges the probabilistic scores of raw word frequencies (Lexical/BM25) with semantic meaning relationships (Vector/ChromaDB), resulting in an extreme recovery accuracy of dates or non-textual text metadata (e.g., UUIDs).

### Vault (Sensus Vault / God Mode)
The physical, literal directory tree of the local computer permanently monitored by Sovereign Pair. It requires no copying or deep relational abstraction to work: it is the organic repository (folders, `.md`, `.pdf`, spreadsheets) where the system's agents inhabit, ingest, and reflect. The visual abstraction that reads these trees in the GUI is the Sensus Vault (Side Dashboard and Graph UI).

## Orchestration (N8N / Core MCP)

### MCP (Model Context Protocol) 
Protocol natively established (by Anthropic) that Sovereign Pair inherits in its core APIs so that third-party tools and LLMs can request actions (like READ_VAULT, EXECUTE_BASH, INGEST_DATA) via a universal corporate standard. The internal FastAPI hosts an MCP Server that dictates the vital resources available in the Vault.

### TDD & Zero-Bypass
Organizational mandate adopted starting from Release 3.3.0. The entire code suite and the CI/CD must run uninterrupted without weak fault-tolerant directives like ignore lint (`# noqa`) or permissions for purposefully exposed secrets in the scanners (`.gitleaksignore`). The system artifacts must shield themselves purely through software architecture (Robust Mocks and structured Re-imports).

---
> *Internal Documentation Note: New architectural terms emerging in upcoming phases must be logged solely in this document alphabetically within their correlated groups.*