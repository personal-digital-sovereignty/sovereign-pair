# OCI Manual Provisioning Guide (Fallback)

This document outlines the manual steps to provision the Server Node (The Coder / The Doctor) in the Oracle Cloud Infrastructure (OCI) in case the automated `cloud-init` fails during Terraform execution.

## Prerequisites
- SSH access to the newly created instance.
- A **GitHub Personal Access Token (PAT)** with read access to the `sovereign-pair` repository.
- A **Tailscale Auth Key** to join the instance to your Mesh network.

## Manual Execution Steps

Access the server via SSH and execute the following steps in order as the `ubuntu` user (or using `sudo`).

### 1. Fix APT Mirrors and Update
Oracle's default images often hardcode the APT mirrors to the region where the image was built (e.g., Ashburn `iad-ad-3`). This command makes the mirrors generic and updates the package lists.
```bash
sudo sed -E -i 's/[a-z0-9-]+\.clouds\.ports\.ubuntu\.com/ports.ubuntu.com/g' /etc/apt/sources.list
sudo apt-get update -y
```

### 2. Install Tailscale & Connect to Mesh
Replace `<SUA_AUTH_KEY_TAILSCALE>` with your valid Tailscale key.
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --authkey=<SUA_AUTH_KEY_TAILSCALE> --ssh --accept-dns=true
```

### 3. Install Ollama and Pre-load LLMs
Install the Ollama engine and pull the primary models in the background.
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama && sudo systemctl restart ollama
sudo runuser -l root -c "nohup ollama pull qwen2.5-coder:7b > /var/log/ollama_pull_coder.log 2>&1 &"
sudo runuser -l root -c "nohup ollama pull llama3.2:3b > /var/log/ollama_pull_doctor.log 2>&1 &"
```

### 4. Install Docker Engine
```bash
curl -fsSL https://get.docker.com | sudo sh
```

### 5. Clone the Repository
Replace `<SEU_PAT_GHCR>` with your GitHub Personal Access Token.
```bash
sudo git clone https://\<SEU_PAT_GHCR\>@github.com/Personal-Digital-Sovereignty/sovereign-pair.git /opt/sovereign-pair
cd /opt/sovereign-pair
```

### 6. Configure and Launch Services
Set up the environment and start the Docker Compose stack (including n8n and Core Services).
```bash
sudo cp .env.example .env
sudo mkdir -p ./data/vault
sudo docker compose -f docker-compose.yml -f docker-compose.n8n.yml up -d
```

## Validation
Once complete, you should be able to access the n8n interface and the FastAPI backend via the Tailscale IPs assigned to the instance. You can monitor the LLM downloads by tailing the logs:
```bash
tail -f /var/log/ollama_pull_coder.log
tail -f /var/log/ollama_pull_doctor.log
```

## Troubleshooting: "network declared as external, but could not be found"

If the Docker Compose stack fails to start with the following error:
```text
network sovereign-pair_sovereign-net declared as external, but could not be found
```

This usually happens when there's an issue with the pre-requisites (specifically Tailscale) preventing the Docker networks from being created properly, or if `docker-compose up` was run before the authentication finished.

**How to Fix:**

1. **Verify your Tailscale Authentication:** Ensure the node actually joined the Mesh. The command `tailscale status` must show the machine connected. If not, re-run step 2 with a valid Auth Key.
2. **Re-create Docker Networks:** Stop the broken stack and let Docker Compose re-evaluate the networking requirements.
```bash
# Tear down whatever was partially created
sudo docker compose -f docker-compose.yml -f docker-compose.n8n.yml down

# Run it again
sudo docker compose -f docker-compose.yml -f docker-compose.n8n.yml up -d
```

---

## Guia de Provisionamento Manual OCI (Fallback em Português)

Este documento descreve os passos manuais para provisionar o Server Node (The Coder / The Doctor) na Oracle Cloud Infrastructure (OCI) caso o `cloud-init` automático falhe durante a execução do Terraform.

### Pré-requisitos
- Acesso SSH à instância recém-criada.
- Um **Personal Access Token (PAT)** do GitHub com acesso de leitura ao repositório `sovereign-pair`.
- Uma **Auth Key do Tailscale** para adicionar a instância à sua rede Mesh.

### Passos para Execução Manual

Acesse o servidor via SSH e execute os seguintes passos em ordem utilizando o usuário `ubuntu` (com `sudo`).

#### 1. Corrigir Mirrors do APT e Atualizar
As imagens padrão da Oracle costumam fixar os mirrors do APT para a região em que a imagem foi construída (ex: `iad-ad-3` de Ashburn). Este comando torna os mirrors genéricos e atualiza as listas de pacotes.
```bash
sudo sed -E -i 's/[a-z0-9-]+\.clouds\.ports\.ubuntu\.com/ports.ubuntu.com/g' /etc/apt/sources.list
sudo apt-get update -y
```

#### 2. Instalar Tailscale e Conectar à Rede Mesh
Substitua `<SUA_AUTH_KEY_TAILSCALE>` pela sua chave do Tailscale válida.
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --authkey=<SUA_AUTH_KEY_TAILSCALE> --ssh --accept-dns=true
```

#### 3. Instalar Ollama e Pré-carregar LLMs
Instala o motor Ollama e inicia o download dos modelos em segundo plano.
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama && sudo systemctl restart ollama
sudo runuser -l root -c "nohup ollama pull qwen2.5-coder:7b > /var/log/ollama_pull_coder.log 2>&1 &"
sudo runuser -l root -c "nohup ollama pull llama3.2:3b > /var/log/ollama_pull_doctor.log 2>&1 &"
```

#### 4. Instalar Docker Engine
```bash
curl -fsSL https://get.docker.com | sudo sh
```

#### 5. Clonar o Repositório
Substitua `<SEU_PAT_GHCR>` pelo seu Personal Access Token do GitHub.
```bash
sudo git clone https://\<SEU_PAT_GHCR\>@github.com/Personal-Digital-Sovereignty/sovereign-pair.git /opt/sovereign-pair
cd /opt/sovereign-pair
```

#### 6. Configurar e Subir os Serviços
Configura o ambiente e inicia a stack do Docker Compose (incluindo o n8n e os Core Services).
```bash
sudo cp .env.example .env
sudo mkdir -p ./data/vault
sudo docker compose -f docker-compose.yml -f docker-compose.n8n.yml up -d
```

#### Resolução de Problemas (Troubleshooting)
Se o Docker Compose falhar com a mensagem:
`network sovereign-pair_sovereign-net declared as external, but could not be found`

Isso geralmente ocorre quando o Tailscale não se conectou com sucesso, impedindo o Docker de localizar as interfaces de rede necessárias, ou porque a stack subiu antes do Mesh estabelecer conexão.

**Como Corrigir:**
1. Valide a conexão executando `tailscale status`. Se não estiver conectado, repita o Passo 2.
2. Derrube e recrie a Stack do Docker:
```bash
sudo docker compose -f docker-compose.yml -f docker-compose.n8n.yml down
sudo docker compose -f docker-compose.yml -f docker-compose.n8n.yml up -d
```
