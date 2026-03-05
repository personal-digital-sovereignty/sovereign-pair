# Sovereign Pair - Guia de Implantação em Nuvem (Deployment)

**Versão da Infraestrutura:** 3.3.0
**Target Ambiental:** Oracle Cloud Infrastructure (OCI) / On-Premises Docker
**Pré-requisitos:** Terraform (OpenTofu) >= 1.6.0, Docker Engine >= 24.0.0

Este documento fornece as diretrizes operacionais de implantação da plataforma Sovereign Pair. Destina-se a Engenheiros DevOps responsáveis por instanciar a malha RAG Cíbrida (Nó Cloud Orquestrador + Nó Físico Inferencial) utilizando abordagens de Infraestrutura como Código (IaC).

---

## 1. Arquitetura de Contêineres (Plano de Dados)

O provisionamento isolado no nó ocorre através da especificação declarativa do Docker Compose. A topologia padrão `enterprise` segrega os serviços em uma rede em ponte interna (`sovereign-net`).

### 1.1 Serviços Baseativos (Core Services)
1. **`sovereign-db` (PostgreSQL 15+):** Gerencia metadados de sistema, controle Multi-Tenant e rastreabilidade das Sessões Vault.
2. **`sovereign-chroma` (ChromaDB):** O Data Store Vetorial. Hospeda matrizes semânticas em discos de bloco atrelados via *Bind Mounts* ou Volumes Nomeados persistentes.
3. **`sovereign-api` (FastAPI / Uvicorn):** Núcleo lógico. Orquestra a injeção RAG e o roteamento das LLMs (Ollama) sob o protocolo HTTP REST e Server-Sent Events (SSE).
4. **`sovereign-web` (Vue3 / Nginx Proxy):** Entrega os artefatos SPA pré-compilados (*dist*) otimizados estaticamente.

### 1.2 Guarda-Costas de Rede (Ingress/Egress)
1. **`sovereign-caddy` (Proxy Reverso M2M):** Intercepta o tráfego 443. Resolve domínios na intranet emitindo certificados TLS assinados nativamente para segurança zero-config.
2. **`sovereign-tailscale` (VPN Sidecar):** O nó SDN (Software-Defined Network). Conecta a DMZ dos contêineres à malha criptografada (Mesh) da Tailnet baseada em WireGuard, desobrigando a exposição física de portas públicas no provedor de Cloud.

---

## 2. Padrões de Operação Cloud (OCI A1 Flex)

A hospedagem do Plano de Orquestração baseia-se prioritariamente no serviço Core Computes da *Oracle Cloud Infrastructure (OCI)* usufruindo das OCPUs Ampere (ARM64).

### 2.1 Especificações do Nó (Target Baseline)
- **Shape:** `VM.Standard.A1.Flex`
- **CPU:** 4 a 6 OCPUs (Dependente de Tier PAYG ou Always Free)
- **RAM:** 24 GB
- **Sistema Operacional:** Ubuntu 22.04 LTS (Canonical) ou Oracle Linux 9.

### 2.2 Gatilho de Automação (Cloud-Init)
A injeção de estado no Oracle VM é inteiramente automatizada pelo Terraform. O arquivo `infra/terraform/compute.tf` repassa um payload em Base64 (*cloud-init.yaml*) responsável por:
1.  Atualização das Cadeias de Certificados e `apt-get` base.
2.  Instalação transparente do Docker Engine nativo.
3.  Autenticação Unsupervised do Tailscale, associando a máquina instantaneamente à sua sub-rede privada sem exigir pares de chaves pré-existentes além do token efêmero (`TS_AUTHKEY`).

### 2.3 Tratamento de Capacidade Host (Erro 500 OCI)
Devido à restrição extrema no agrupamento de Racks Ampere em Datacenters com alta demanda (ex: us-ashburn-1), as implantações automáticas sofrem com a carência da mensagem `Out of host capacity`.

**Solução Operacional:**
Engenheiros devem delegar a tarefa de criação ao script autônomo. O binário `retry_deploy.sh` embala a instrução `tofu apply -auto-approve` num loop otimizado, assaltando slots de Hardware que vagam na borda do provedor a cada 2 minutos. **Aviso SRE:** Cancele deleções manuais (Destroy). Modifique configurações puramente por substituição de blocos (In-Place Updates) no *tfvars* para não descer para o fim da fila de requisições Tofu.

---

## 3. Topologia de Rede Zero-Trust e TLS

A exposição a superfícies externas foi mitigada por design. Os módulos de Ingress Controllers da AWS/OCI/GCP não abrigam regras permissivas no Sovereign Pair.

### 3.1 Fluxo Inbound HTTPS (Loopback Interno)
O Tailscale atribui dinamicamente um registro A no DNS gerado pelo MagicDNS (ex: `sovereign-oraclenode.tailxxxx.ts.net`).
- **Passo 1:** A terminação (Handshake) TLS gerada via ACME Let's Encrypt acontece nativamente dentro do *Sidecar* Container da Tailscale na rede externa.
- **Passo 2:** A comunicação descriptografada entra apenas internamente (Layer 7 Loopback local) da `porta 443` da Tailscale para a `porta 80` do Web Server *Caddy*.
- **Passo 3:** O *Caddy* distribui o processamento atômico internamente: URI `/api` reverte para a API em Python e o estático colide com o Nginx Frontend.

### 3.2 O Fluxo "Headless" Mobile e Resolução DNS (NextDNS/DoH)
Dispositivos End-User equipados com interceptadores de DNS Privado (como NextDNS atuando sob o *Android Private DNS Engine*) bloquearão domínios *ts.net*, já que este se recusa a delegar requisições ao DNS Interno fornecido pela placa *100.100.100.100* do Tailscale local.

**Procedimento de SRE/Admin (Solução Definitiva):**
Adicione uma diretiva fixa de *Custom Rewrite* no painel do seu Firewall DNS DNS (NextDNS Web Admin).
- **Target Record (`A`):** `[magic_dns_da_maquina].ts.net`
- **Target IP:** Endereço da Máquina `100.x.x.x` (IP Privado local forjado pelo Tailscale).
Desta forma o resolvedor em nuvem da NextDNS entrega o túnel Cíbrido diretamente dentro do cliente sem quebrar a Cadeia de Segurança DoT/DoH do Mobile.

---

## 4. Instruções Diretas de Ignição

### Parametrizações IaC (Terraform)
1. Modifique o arquivo `infra/terraform/terraform.tfvars`.
2. Inclua suas credenciais rígidas (OCIDs, RSA Pública de Computação, Region e Availability Domain).
3. Execute as validações de plano Tofu:
```bash
tofu init
tofu plan -out=tfplan
tofu apply tfplan
```

### Configurações Sidecar VPN (`.env`)
Todo Contêiner necessita da Variável de Identidade para provisionar o nó M2M na Sub-Rede.
1. Gere um *Reusable Ephemeral Key* de Alta Disponibilidade no Dashboard Web Administrativo Tailscale.
2. Aloque a string unificada à diretiva `TS_AUTHKEY` no seu `.env` raiz do Compose.
3. Levante as pontes:
```bash
docker compose up -d
```

---

**Glossário Técnico Referenciado:** Vide `docs/glossary.pt-BR.md`.
