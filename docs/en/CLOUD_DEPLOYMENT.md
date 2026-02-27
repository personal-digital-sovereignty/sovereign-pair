# Sovereign Pair: Cloud Deployment

This guide covers the process of setting up and hosting Sovereign Pair in Public Cloud environments (AWS, Google Cloud, Oracle Cloud, generic VPS) utilizing best-in-class Cloud-Native and Zero-Trust practices.

## Cloud-Native Architecture

The repository ships with complete Docker Compose orchestration that encapsulates:
1. **Vue.js Frontend:** Multi-stage built and served via a lightning-fast `nginx:alpine` image.
2. **FastAPI Backend:** Lean image based on `python:3.12-slim` running under a secure *non-root* user.
3. **Vector & Relational Persistence:** Uses official ChromaDB and native PostgreSQL 15 images.
4. **Caddy Edge Router (Auto-HTTPS):** A modern replacement for Nginx/Cert-Manager that self-signs TLS for private network traffic or uses Let's Encrypt for real domains with zero manual configuration.
5. **Tailscale VPN Sidecar:** (Optional) Exposes the API and App solely within a WireGuard mTLS mesh VPN, without needing to open ports 80/443 to the broader internet, instantly blocking cloud scanners.

---

## 🚀 Deployment Step-by-Step

### 1. Preparing the VM (Host)
You will need a machine with at least 4GB of RAM (8GB recommended if you plan to manage very extensive local knowledge bases).
Install the core prerequisites:
- Git
- Docker Engine & Docker Compose V2

### 2. Configuring the Environment and API Keys
Clone the repository and create your definitive `.env` file:
```bash
git clone https://github.com/Sovereign-Pair/sovereign-pair.git
cd sovereign-pair
cp .env.example .env
```
Fill out the `.env` following security tips:
- Set strong passwords for `POSTGRES_PASSWORD`.
- *Optionally* insert the `TS_AUTHKEY` if you want the Zero-Trust mesh enabled.
- Add your Cloud API Keys (e.g., `GEMINI_API_KEY` or `OPENAI_API_KEY`). **The backend will automatically handle the redaction of these keys from logs thanks to our built-in Security Filter.**

### 3. HTTPS and Domain (Automatic Edge Router)
Sovereign Pair uses **Caddy** to bridge and terminate SSL/TLS:
- Take a look at the `Caddyfile` located at the root.
- **If you do NOT have a domain (Tailscale or direct IP use):** Leave the file as is. Caddy will force local self-signed HTTPS automatically.
- **If you DO have a public custom domain:** Uncomment Section 1 of the `Caddyfile` and replace `yourdomain.com` with your real domain. Caddy will issue the Let's Encrypt SSL certificate for you on the fly.

### 4. Secure Initialization (Run)
Spin up all containers and build the Vue assets with a single command:
```bash
docker compose up -d --build
```
After the build (which will take 2 to 5 minutes the first time to download DB images, compile NPM, and install Python Machine Learning libs), your Personal RAG will be alive, running on shielded ports behind Caddy.

Access the interface via your browser: `https://[YOUR-DOMAIN-OR-TAILSCALE-IP]`
