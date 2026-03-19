# Sovereign Pair - CI/CD & DevSecOps Pipelines

This document details the Continuous Integration (CI), Continuous Delivery (CD), and Security ecosystem (DevSecOps) governing the Sovereign Pair repository via GitHub Actions.

The project enforces a **FOSS Enterprise** pipeline standard, guaranteeing that no code reaches production (or Oracle edge nodes) without strictly complying with formatting logic, deep vulnerabilities scans, and overall systemic stability.

---

## 1. FOSS Enterprise DevSecOps (`devsecops.yml`)
This is the primary security pipeline (Central Gateway). It acts as a firewall that intercepts pushed modifications blocking malicious activities from being persistently injected into the user's Local Sovereignty architecture.
* **Triggers:** Push and Pull Requests actions anywhere in the repository.
* **Validation Sub-Gates:**
  * **Zizmor & Actionlint:** Actively audits `.yml` GH files verifying pipeline integrity against *Cache Poisoning*, *Shell Injections*, and *Unpinned Action Vulnerabilities*.
  * **Gitleaks:** Secret scanner that actively blocks the publishing of JWTs, SSH Keys, AWS tokens, mapping RSA keys into an unauthorized blast radius.
  * **Cargo Clippy & Rust-Analyzer (Memory Safety):** Static Application Security Testing strictly built for Rust. Scans the Rust backend core and TypeScript Web UI searching for un-sanitized LLM payload prompts, uncontrolled pointers, and hardcoded flaws.
  * **Trivy (SCA):** Software Composition Analysis, checking active upstream dependencies (e.g. `Cargo.toml` / `package-lock.json`) for known catalogized CVE exploits.
  * **Cargo Fmt:** Enforcement agent for clean Rust design, keeping the compiled architecture solid, free of unused syntax or wild imports.

## 2. Backend API CI/CD (`docker-api.yml`)
The engine compiling the neural heart (Rust Axum).
* **Triggers:** Modifications triggered within `src-rust/`, `Standalone Binaryfile.rust` and `Cargo.toml`.
* **Action Steps:**
  * **Cargo Test & Traits:** Spins up robust async tests to validate RAG memory extraction (`The Nurse`), markdown parsing, parallel semantic ingestions, and unit states.
  * **Cargo Clippy:** Secondary backend guard gate for strict memory structural integrity.
  * **Build & Push ghcr.io:** Exclusively compiles the lean *sovereign-pair-axum* container mirroring the new state, securely exporting it to GitHub's container registry for edge-node consumption.

## 3. Web UI CI/CD (`docker-web.yml`)
Delivery architecture pipeline focused solely on the Frontend presentation (Svelte 5 + Vite).
* **Triggers:** Patches within the `web-ui/` directory subtree or changes in `Standalone Binaryfile.web`.
* **Action Steps:**
  * **Node/npm CI:** Compiles NPM dependency tree matching absolute state boundaries in the lockfile preventing drift packages.
  * **TypeScript Checkout:** Strongly typed checking to detect front-end memory regressions.
  * **Build & Push ghcr.io:** Builds the optimized Cyber-Minimalistic Vite static payload, bundling it within the hyperfast Nginx Alpine layer, deploying it securely mapped on GHCR.

## 4. Deploy Sovereign Cibrid Cloud (`deploy-oci.yml`)
The Heart of automation transiting the edge to Oracle Cloud (Infrastructure Automation).
* **Triggers:** Manually invoked (via *Workflow Dispatch* UI `apply`/`destroy`) or via root updates on `infra/terraform/`.
* **Action Steps:**
  * **OpenTofu Init:** Consumes repository injected encrypted secrets mapping private `Tailscale` clusters, OCI keys, and Network parameters.
  * **Infrastructure Orchestration:** Applies the architecture strictly via OpenTofu (stateful IaC code), communicating recursively with Oracle resolving the *Zero-Trust Network*, creating the A1 processor node, mapping cloud-init payload, booting Standalone Binary natively alongside RAG/N8N Cibrid integration. It serves both scaling upwards and total cloud-burn down (Destroy mode).

## 5. Sensus Vault Plugin Release (`release-sensusvault.yml`)
Distribution module rendering auto-installable packages linking sovereign context into the Sensus Vault PKM grid.
* **Triggers:** Upon any tagged releases configured under `sensusvault-v*`.
* **Action Steps:**
  * Uses pristine Node/NPM cache hooks.
  * Condenses typescript configurations (`main.js`, `styles.css` and `manifest.json`) targeting the local Vault renderer.
  * Minifies and zips all final outputs proactively delivering a cleanly shaped Release package natively over the GH Releases API for instant final-user acquisition.

## 6. CLI Release (`release-cli.yml`)
Automatic release machinery rendering terminal command-line binaries.
* **Triggers:** Manually configured workflow dispatch or version tags.
* **Action:** Compiles and packages the Rust Axum logical codebase recursively into cross-compatible platform standalone bin files providing full retro-compatibility strictly in isolated edge instances without persistent virtualization container layers.
