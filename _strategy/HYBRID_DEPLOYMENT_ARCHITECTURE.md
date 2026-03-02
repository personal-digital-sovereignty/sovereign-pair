# Sovereign Pair: Hybrid Deployment Architecture (Cibrid Network)

## 1. O Paradigma de Infraestrutura "Cloud-Assistida"
A premissa fundamental do *Sovereign Pair* é a Soberania dos Dados. No entanto, para maximizar o desempenho local (ex: no notebook Ryzen 7 com 32GB RAM), os Modelos de Raciocínio Profundo que não dependem do banco de dados confidencial cru são transferidos para uma malha de nuvem (Cloud Mesh).

Isso nos leva à **Divisão de Cérebros**:
1. **Host Local (Sovereign Node)**: Onde reside o Cofre (Vault do Sovereign Pair), o banco Vetorial SQLite/Chroma, e o Agente Roteador. Nenhuma nota de texto deixa essa máquina em formato aberto.
2. **Oracle Cloud Node (Computing Node)**: Instância A1 (ARM Ampere Altra) gratuita da Oracle atuando estritamente como a "cabeça de inferência" para o VSCode e abstrações complexas.

---

## 2. Posição dos Agentes na Topologia

| Agente | Modelo (Recomendado) | Papel | Hospedagem Fungal |
| :--- | :--- | :--- | :--- |
| **1. The Mom** | Regex / AST Scanner | Indexadora em Fundo `O(1)` | **Local** (Ryzen) |
| **2. The Dad** | `bge-m3` (1024-D) | O Gerador de Vetores Semânticos | **Local** (Ryzen) |
| **3. The Nurse** | Algoritmo Python / `0.5b` | O Roteador de Tráfego Rápido | **Local** (Ryzen) |
| **4. The Doctor** | `llama3.2:3b` | O Clínico Geral & Historiador | **Cloud** (Oracle A1) |
| **5. The Coder** | `qwen2.5-coder:7b` | O Engenheiro (via OpenCode) | **Cloud** (Oracle A1) |

---

## 3. Segurança e Conectividade (Zero-Trust mTLS)

A instância Oracle **NÃO TERÁ IP PÚBLICO ABERTO**. Expor a porta `11434` do Ollama na nuvem é um convite para criptomineradores.
Toda a arquitetura é baseada no **Tailscale (WireGuard)**:

*   **Rede Mesh Privada**: A Instância A1 pertence à mesma VPN P2P (Peer-to-Peer) do Host Local. O tráfego não passa pela internet aberta; ele viaja num túnel mTLS criptografado fim a fim (`100.x.x.x`).
*   **Invisibilidade Externa**: Quem scanear o IP público da Oracle A1 pelo Shodan ou Nmap só encontrará um muro de tijolos (Drop passivo de pacotes). O Ollama fará bind estrito na interface `--host 100.x.y.z`.

---

## 4. Otimização de Performance (O Script "ZRAM de Ouro")

Os processadores ARM da Oracle não têm Swap de alto desempenho nativamente, e a latência de I/O em discos de rede (Block Storage) pode asfixiar a VRAM na transição de tokens do Ollama.
Para fazer a máquina Oracle A1 "render como um A4":

1. **ZRAM (Compressed RAM Swap)**: No *Cloud-Init* do Terraform, instalaremos o `zram-generator`. Ele pegará 8GB dos 24GB de RAM nativa da Oracle e usará como Swap super-comprimido. O Ollama despeja os pesos nativos ali e descompacta agressivamente usando a CPU ARM, ganhando uma sobrevida massiva na alocação de LLMs em alta concorrência sem depender de leitura/escrita no disco lento SSD.
2. **Ollama Tunning**: Modificações no `.service` do SystemD forçarão o `OLLAMA_FLASH_ATTENTION=1` (para contexto massivo rápido no Qwen2.5) e `OLLAMA_NUM_PARALLEL=4`.

---

## 5. Implementação IaC (GitHub Actions + OpenTofu)

O ciclo de vida da Instância Oracle será totalmente automatizado por Infrastructure as Code (OpenTofu) nas esteiras de Continuous Deployment (CD).

### A Esteira de Deploy
Um arquivo `.github/workflows/deploy-oci.yml` fará o orquestramento:
1. O desenvolvedor dá push na branch `main` com alguma alteração na pasta `infra/terraform/`.
2. A Action ativa o runner em um **GitHub Environment chamado `Oracle_Cloud`**.
3. Ela captura os Secrets: `OCI_PRIVATE_KEY`, `OCI_TENANCY_OCID` e `TAILSCALE_AUTH_KEY`.
4. Dispara o `tofu apply -auto-approve`.

### O Bootstrap Físico (Cloud-Init YAML)
Durante a criação da VM (segundo 0), a Oracle recebe o arquivo `cloud-config.yaml` que:
*   Instala o Tailscale e loga invisivelmente na rede local do usuário via Auth Key: `tailscale up --authkey=$TAILSCALE_KEY --ssh`.
*   Aplica o ZRAM Swap (Otimização).
*   Baixa o Docker via GPG.
*   Puxa as imagens oficiais e roda os comandos `ollama pull llama3.2` e `ollama pull qwen2.5-coder:7b`.
*   O host local fica só assistindo; quando o Ollama terminar (aproximadamente 15 minutos do boot autônomo), a API Mestre no Ryzen redireciona o tráfego pesado automaticamente para o IP na subnet `100.x.x.x`.

---

## 6. System Resilience & Auto-Recovery (Appliance Mode)

Para garantir que o Sovereign Pair opere como um _appliance_ indestrutível e "à prova de usuários", a infraestrutura dockerizada foi projetada para recuperação autônoma completa em 100% dos cenários de reboot local ou falha de força.

### A Política *Restart: Always*
O orquestrador `docker-compose.yml` impõe a diretiva `restart: always` em absolutamente todos os contêineres da tríade e periféricos cognitivos:
- `caddy` (Proxy Reverso e SSL)
- `postgres` (Banco Relacional)
- `chroma` (Banco Vetorial)
- `api` (Backend Python/FastAPI)
- `web` (Frontend Estático VueJS / Nginx)
- `tailscale` (VPN Zero-Trust)
- `ollama` (Motor Local de LLM)

### Fluxo de Boot Autônomo
Sempre que a máquina do host (ex: Ryzen 7) reinicia, o Daemon do Docker inicializa junto ao SystemD. A partir desse momento:
1. A rede isolada (`sovereign-net`) é restabelecida.
2. O Tailscale sobe e autentica as chaves da malha (Mesh), permitindo acesso à Oracle (Cloud Node) imediatamente.
3. Bancos de dados (`postgres` e `chroma`) montam seus volumes físicos montados no host.
4. O contêiner da `api` inicia (que agora usa mapeamento limpo virtual `/app/data` blindado contra `PermissionError` do host) preenchendo o contexto no grafo (AST).
5. O contêiner `web` expõe a UI pré-compilada, e o `caddy` expõe o tráfego seguro para o navegador.

**Garantia:** O usuário não precisa abrir o terminal para digitar nenhum comando de subida. O sistema volta "sozinho" com o mesmo estado exato do último milissegundo antes do desligamento (Stateful).
