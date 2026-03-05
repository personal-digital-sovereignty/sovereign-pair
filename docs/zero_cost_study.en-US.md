# Sovereign Pair - Zero-Cost Architecture Study

**Project Phase:** 42 (Orchestration and Cibrid Integration)
**Objective:** Elaborate the architectural blueprint for deploying an automation ecosystem (N8N) supported by an in-memory cache (Redis) with a strictly zero ($0.00) computational cost, capitalizing on closed secure meshes (Tailscale).

---

## 1. Engineering Premises

To satisfy the absolute requirement of `Zero Cost`, the topology discards managed PaaS (Platform as a Service) like RedisLabs, AWS ElastiCache, or N8N Cloud. The architecture will rely entirely on the *Self-Hosted* paradigm over *Always Free Tiers* slices of Public Clouds.

*   **Computational Power:** Oracle Cloud Infrastructure (OCI).
*   **Networking & Security:** Tailscale (WireGuard Mesh VPN).
*   **Container Orchestration:** Native Docker Compose.
*   **Target Applications:** N8N (Community Edition) and Redis (Alpine/Docker).

---

## 2. Hardware Selection (OCI Free Tier)

Oracle Cloud provides the most generous `Always Free` tier on the market for ARM64 (Ampere) processors. 

**Allocated Specifications (Orchestrator Node):**
*   **Instance:** `VM.Standard.A1.Flex`
*   **CPU:** 4 OCPUs (Equivalent to 4 robust vCPUs).
*   **RAM:** 24 GB unified.
*   **Storage:** 50 GB of Block Volume (SSD).
*   **Contractual Cost:** $0.00/month perpetually.

*SRE Note:* 24GB of RAM is exponentially sufficient to run the N8N NodeJS engine at its fullness (which suffers critical bottlenecks on AWS T2.Micro instances with merely 1GB) and accommodate the transactional memory persistence of Redis.

---

## 3. Zero-Trust Topology (Tailscale Network)

One of the biggest pitfalls of *Self-Hosted* solutions is exposing administrative interfaces (like port `5678` for N8N or `6379` for Redis) directly to the public Internet (`0.0.0.0`), drawing scanners and malicious bots native to Cloud providers.

**The Cibrid Solution:**
1.  **IPV4 Isolation:** In the `docker-compose.yml`, Redis and N8N will not bind to the public host network.
2.  **Exclusive Tailnet:** The OCI machine will be hitched to the corporate Tailscale mesh through ephemeral Auth Keys in provisioning (Cloud-Init).
3.  **N8N ↔ Redis Communication:** Will occur isolated within the internal Docker *Bridge Network* (`sovereign-net`). N8N will see Redis by the container's hostname (`redis:6379`).
4.  **User Access to N8N:** The Sovereign Interface or the Developer will only be able to access the N8N GUI by connecting to the Tailscale VPN from their own devices. Access to the N8N panel will be mapped via a reverse proxy (Caddy) exclusively listening to incoming traffic derived from the Tailscale virtual interface (`tailscale0`).

*   **Tailscale Cost:** The Personal Plan supports up to 100 virtual devices, entirely unmetered traffic (native P2P), for $0.00.

---

## 4. Caching and Persistence Strategy (Redis and N8N)

### 4.1 N8N Queue Mode vs Regular Mode
N8N allows scaling via Redis (Queue Mode) delegating complex executions to parallel Workers.
For the Sovereign Pair RAG, we will initially adopt the **Regular (Standalone)** architecture aiming for overhead economy, but Redis will act on two vital fronts:
1.  Storage and rate-limiting of keys/Sessions (Sovereign API limiters).
2.  Temporary storage of massive Webhook payloads transiting between N8N and FastAPI.

### 4.2 Redis Restrictions (Ephemeral Bind)
Redis will be implemented by the lightweight `redis:alpine` image in Docker. Disk persistence (`AOF/RDB`) will not be forced, ensuring blazing fast I/O (Ephemeral), since the "Absolute Truth" of data lives in the *Vault* files on the user's machine.

---

## 5. Proven Cost Matrix

| Service/Infra | Provider | Component | Monthly Cost (USD) |
| :--- | :--- | :--- | :--- |
| Cloud Compute | Oracle Cloud (OCI) | VM A1.Flex (4 Core/24GB) | $0.00 |
| Cryptography / VPN | Tailscale | Personal Plan (Zero-Trust) | $0.00 |
| Proxy and TLS | Caddy via Docker | Let's Encrypt Certificates | $0.00 |
| Workflow Engine | N8N | Docker Community Edition | $0.00 |
| Queue & Cache | Redis | Docker Alpine | $0.00 |
| **Total Cost** | --- | Estimated Monthly TCO | **$0.00** |

---

## 6. Next Steps (Execution Plan)

To materialize this study into the CI/CD pipelines and local nodes:
1. Enhance the IaC manifest (`infra/terraform/compute.tf`) to validate strict Oracle machine behaviors.
2. Write the attached `docker-compose.n8n.yml` script declaring the Redis dependencies.
3. Test locally simulating the Prod environment, invoking simple N8N webhooks that call the Sovereign Pair's `/v1/chat` API route, attesting the isolation.
