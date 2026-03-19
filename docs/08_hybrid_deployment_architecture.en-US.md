# Treatise VIII: Hybrid Deployment Architecture

## 1. Network Topology Overview

The infrastructure seeks to decentralize demands while preserving the primary host's role of managing private documents. To compensate for physical limitations on the developer's Desktop, time-consuming free-code inference or external generation are distributed to public cloud providers.

This corporate environment is divided into the following OS mesh:
1. **Central Local Node:** Managed OS environments on Personal Physical Hardware keeping the Markdown vaults (Sensus Vault) and local SQLite vector formats under strict protection.
2. **OCI Auxiliary Node (Cloud Node):** Uses secondary deployment on Oracle OCI Virtual Private Servers (VPS), attested via free 64-bit ARM machines (Ampere A1).

---

## 2. Routing Patterns (Engine Distribution)

The logic that organizes and designates responsibilities within the nodes of the multi-agent environment is divided according to the required native support:

| Modules (Worker) | Architectural Responsibilities | Ideal Minimum Deployment |
| :--- | :--- | :--- |
| **The Mom / FileWatcher** | Modification indexing in static folders (Linux `notify`). | Local Desktop Machine |
| **The Dad / Embedded** | Vector chunk transformations (`bge-m3` via Local Rust). | Local Desktop Machine |
| **The Nurse / Router** | Parametric evaluation categorizing original HTTPS *intents*. | Local Desktop Machine |
| **The Doctor / Engine** | Contextual formatted modeling iterating under the RAG model. | Oracle OCI (External VPS or High-End Local Hardware) |
| **The Coder / Logic** | Strict refactoring documentation analyzer under Rust Axum OpenCode. | Oracle OCI |

---

## 3. VPN Structural Security (Peer-to-Peer mTLS Tunnel)

On a definitive basis, OS LLM API endpoints provided by *Standalone Binary `11434`* or sub-dependent Rust API Axum *8000* will be completely closed to global band instances (No *Bind TCP 0.0.0.0* and devoid of exposed WAN ports).

*   **Operative Cryptographic Validation (WireGuard via Tailscale):** Traffic originating from Cloud calls to local vector files is conducted under an encrypted peer-to-peer connection acting directly through internal interfaces (`100.x.x.x`). The structure facilitates secure remote access independent of the blocking corporate OS routers at the user's local companies.
*   **Passive Contrast Mitigation:** Scans in massive OS external Port Scans will fail since the isolating applications explicitly confine themselves strictly to the VPN subnet, making openings in logical ports of the machine's OS or VPS Server invisible.

---

## 4. ARM64 Server Efficiency and OS Optimizations

In Low-Cost Cloud infrastructure (Free Tiers), OS provisioning in environments providing Limited Storage can present difficulties when tied to large contextual files. Forced processing under Block Storage Volumes causes loss in *IOPS* and freezing upon exhaustion in the OS's native free memory variables (e.g., Local Llama Inference on the Server).

The `Cloud Init` technical parameterization implemented strict structural logic focused on preserving this response time (Timeout Limit Restrictions):

1. **Compact Memory `zram-tools`:** The Linux OS initializes a virtual swap system instantiating partitioned allocation under the `LZ4` Super-Compression algorithm on the OS's free base memory. Mitigates the origin disk computational bottleneck on the platform without increasing server costs and relieves heavy limitations on the network nodes.
2. **Extended LLMs Execution `OLLAMA_FLASH_ATTENTION=1`:** Expressly inserted via `SystemD` config file, this static technical formatting natively oversees fast reading of LLM modeling handling tokens associated with "giant contexts" (Models >32K Tokens/128K Text Strings), improving asynchronous response times provided to the Native Axum Engine's parallel routing schedules.

---

## 5. Dynamic Infrastructure As Code Implementation (IaC System/OpenTofu)

Processes dependent on the creation of the physical node in the Oracle Cloud have been fully automated through *Infrastructure as Code* (OpenTofu) manifested managers.

### Continuous Pipeline via Github Actions
GitHub Operations centralizes and authorizes orchestration code routing via the `deploy-oci.yml` workflow.
1. The reactive base requires updated *Merges* in the manifests located at `./infra/terraform/`.
2. Cloud GitHub Actions secret restrictives contain Oracle Tenant UUIDs, as well as their limiting API Authentication (*OCI_PRIVATE_KEY*) in the OS file's secret base.
3. Submitted to `tofu apply -auto-approve` operational instances, Ubuntu base containers and configurations boot under the cloud, natively reporting their entire "Secure State" strictly to the branch.

## 6. Resilient Procedures (Self-Healing Application Containers)
The base container design obeys the restricted engineering of the base recommendation for immutable systems (e.g., *12-Factor App*). Faced with structural oscillations originating from the OS (Accidental Kernel Reboots, mass updates restarting base primary VPS instances), they do not require interactive SSH initializations by corporate OS users or the machine's local base engineer:

- Their internal tools and volumes will restart in isolation, parameterized under the native Standalone Binary Engine reset configurations (`restart: always`).
- They merely subject the ultimate RAG Engine to the CloudMesh VPN verification (internal interface) and perform the autonomous OS coupling operating relative to the Rust compiled API interfaces (Local Rest) attested as soon as the OS Server resumes basic computational electrical stability.
