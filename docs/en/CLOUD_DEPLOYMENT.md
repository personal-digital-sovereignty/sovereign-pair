# ☁️ Cloud Deployment & Security Guide (Docker)

Welcome to the Official **Sovereign Pair** Deployment Guide. This document explains in detail how our container infrastructure works, and the "magic" behind our Edge-Router and Zero-Trust Network.

---

## 🏗️ Container Architecture
When you run `docker compose up -d`, our orchestrator spins up an army of **6 containers** working in unison inside an isolated virtual network (Bridge named `sovereign-net`). 

1. **`sovereign-db` (PostgreSQL):** The relational database that manages users, chat history, and enterprise settings.
2. **`sovereign-chroma` (ChromaDB):** Our "Vectorial Brain". This is where the Embeddings of the RAG (Retrieve-Augmented Generation) live.
3. **`sovereign-api` (FastAPI/Python):** The core Intelligence. It hosts the RAG API, orchestrates LLMs, and acts as a bridge between the Database and the frontends.
4. **`sovereign-web` (Vue.js/Nginx):** Our beautiful visual interface, served extremely fast by a static Nginx Server.
5. And the two magical infrastructure guardians: **Caddy** and **Tailscale**.

---

## 🔒 The Magic of Caddy (Auto-HTTPS & Reverse Proxy)

If you've ever tried to spin up a secure web system before, you know the headache of configuring Nginx, generating SSL keys via OpenSSL, and trying to make local certificates work. We solved this by using **Caddy** (`sovereign-caddy`).

Caddy acts as the gatekeeper of our system. Instead of needing to access the Frontend on port 80 and the API on port 8000 (without encryption), Caddy handles everything elegantly and securely on `Port 443 (HTTPS)`.

### How does Caddy work locally?
In the `Caddyfile`, we use the `tls internal` directive. 
This makes Caddy, the millisecond it starts, act as its **own local Certificate Authority (CA)**. It generates and signs a Digital TLS Certificate itself, encrypting your connection with the local `localhost`.

When you access `https://localhost`:
1. Caddy intercepts the request, validates the SSL, and decrypts the packet.
2. If the request is for `/api/*` or `/docs`, it forwards it silently to the `sovereign-api` container through the invisible Docker network.
3. If it's any other request, it delivers the Vue.js page (`sovereign-web`).

**Result:** You browse locally with 100% encrypted traffic and unified routes, without manually configuring any certificates!

---

## 🌐 The Magic of Tailscale (Zero-Trust VPN)

Imagine you installed Sovereign Pair on your home Desktop (or on a lightweight Oracle/AWS VPS), but you want to pull out your phone on 4G outside and talk to your AI.

The old (and extremely dangerous) way to do this would be to open port 443 on your router to the Internet. This exposes your server to hackers, botnets, and DDoS attacks.

**Here enters `sovereign-tailscale`:**
Tailscale is a Mesh VPN based on the ultra-secure **WireGuard** protocol. We encapsulate it natively as a "Sidecar" container in our Docker Compose.

### How does it work in practice?
1. When Compose spins up, the Tailscale container outputs a URL in the logs (`docker logs sovereign-tailscale`).
2. You click on that URL and associate that container with your Tailscale account.
3. **The Magic:** You don't need to open *any* ports on your router. Tailscale punches through your provider's NAT (NAT Traversal) using outbound connections and creates an encrypted Point-to-Point tunnel directly to their coordination servers.
4. The container advertises the Docker *Subnet* (the virtual network where the API and DB live) to your private tunnel.

**The Result:** From your phone on 4G (with the Tailscale App installed), you access something like `https://sovereign-api` from your browser. The traffic "flies" encrypted from your device, passes invisibly through the open internet infrastructure, and "lands" ultra-securely decrypted inside the virtual Docker bridge at your home.

No hacker on the internet can "see" or "hit" your API, because it literally *does not exist* on the map of worldwide public IPs. It only exists in your Zero-Trust Private Dimension! 🌌

> [!NOTE]
> **Regarding the `Authorization failed: requested tags [tag:server] are invalid` error:**
> If you have previously tried using the `--advertise-tags=tag:server` flag in your docker-compose and received this error, this occurs because of Tailscale's **ACLs (Access Control Lists)** system. Users on Free/Starter accounts generally do not have permission to self-assume corporate tags. For personal accounts, default authorization (without strict tags) ensures that your "MagicDNS" works perfectly without administrative panel security blocks.

---

## 🚀 Quick Start & VPN Pairing Guide (Zero-Trust)

1. Clone the repository.
2. Create or copy the `.env` file (insert your OpenAI/Gemini/Anthropic API keys).
3. Ignite the engines:
```bash
docker compose up -d
```
4. **VPN Pairing (Tailscale):** If you haven't configured the optional `TS_AUTHKEY` variable in the `.env`, the container will require your manual authorization the first time it spins up.
   - Run the command below in the terminal to read the Tailscale logs:
     ```bash
     docker logs sovereign-tailscale
     ```
   - Look in the logs for a message similar to this:
     `To authenticate, visit: https://login.tailscale.com/a/xxxxxxx`
   - Click the generated link, log in with your Tailscale account, and **approve the new machine** (which will be listed as `sovereign-rag-cloud`).
5. **IP/DNS Access:** On the Tailscale dashboard, copy the IP assigned to the machine (e.g., `100.x.x.x`) or its MagicDNS (e.g., `sovereign-rag-cloud.tailxxxx.ts.net`).
6. **Configuring Obsidian (Mobile or External Laptop):**
   - In Obsidian, go to `Settings > Sovereign Pair`.
   - Change the **API URL** to `https://[YOUR_IP_OR_DNS_HERE]`. Caddy will handle the HTTPS certificate automatically and without any insecure warnings on your corporate device!
7. Open your browser locally at `https://localhost` (or remotely with the VPN IP above) and be amazed!
