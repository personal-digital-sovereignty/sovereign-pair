# Guia de Provisionamento Manual OCI (Fallback)

Este documento descreve os passos manuais para provisionar o Server Node (The Coder / The Doctor) na Oracle Cloud Infrastructure (OCI) caso o `cloud-init` automático falhe durante a execução do script primário do Terraform.

## Pré-requisitos
- Acesso SSH à instância recém-criada.
- Um **Personal Access Token (PAT)** do GitHub com acesso de leitura ao repositório `sovereign-pair`.
- Uma **Auth Key do Tailscale** para adicionar a instância à rede de serviço.

## Passos para Execução Manual

Acesse o servidor via SSH e execute os seguintes passos em ordem utilizando o usuário `ubuntu` (através de `sudo`).

### 1. Corrigir Mirrors do APT e Atualizar
As imagens base da Oracle OCI frequentemente configuram os mirrors do APT para a região técnica da compilação (ex: `iad-ad-3`). O comando a seguir ajusta os mirrors para os endpoints globais genéricos e atualiza as listas de indexação:
```bash
sudo sed -E -i 's/[a-z0-9-]+\.clouds\.ports\.ubuntu\.com/ports.ubuntu.com/g' /etc/apt/sources.list
sudo apt-get update -y
```

### 2. Instalar Tailscale e Conectar à Rede Mesh
Substitua `<SUA_AUTH_KEY_TAILSCALE>` pela chave correspondente operante.
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --authkey=<SUA_AUTH_KEY_TAILSCALE> --ssh --accept-dns=true
```

### 3. Instalar Ollama e Pré-carregar LLMs
Instala o serviço Ollama e inicia o download assíncrono dos modelos LLM requeridos em segundo plano.
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama && sudo systemctl restart ollama
sudo runuser -l root -c "nohup ollama pull qwen2.5-coder:7b > /var/log/ollama_pull_coder.log 2>&1 &"
sudo runuser -l root -c "nohup ollama pull llama3.2:3b > /var/log/ollama_pull_doctor.log 2>&1 &"
```

### 4. Instalar Docker Engine
```bash
curl -fsSL https://get.docker.com | sudo sh
```

### 5. Clonar o Repositório
Substitua `<SEU_PAT_GHCR>` pelo seu Token de Acesso Pessoal (PAT).
```bash
sudo git clone https://\<SEU_PAT_GHCR\>@github.com/Personal-Digital-Sovereignty/sovereign-pair.git /opt/sovereign-pair
cd /opt/sovereign-pair
```

### 6. Configurar e Iniciar os Serviços
Configura o arquivo de variáveis, injeta a chave da rede privada virtual no arquivo `.env` e inicializa as pilhas do Docker Compose.
```bash
sudo cp .env.example .env
sudo sed -i "s/TS_AUTHKEY=tskey-auth-xxxxxxxxx/TS_AUTHKEY=<SUA_AUTH_KEY_TAILSCALE>/g" .env
sudo mkdir -p ./data/vault
sudo docker compose -f docker-compose.yml -f docker-compose.n8n.yml up -d
```

## Validação de Instância
Após a conclusão, a interface N8N e o backend FastAPI via IPs do Tailscale designados à instância deverão estar acessíveis. Para inspecionar os logs de modelagem:
```bash
tail -f /var/log/ollama_pull_coder.log
tail -f /var/log/ollama_pull_doctor.log
```

## Resolução de Problemas: Erro em "network external"
Caso as instâncias Docker Compose retornem a seguinte exceção durante a iniciação:
`network sovereign-pair_sovereign-net declared as external, but could not be found`

Isso ocorre regularmente quando o nó Tailscale não autentica em tempo hábil com a interface de rede, impedindo o Docker de realizar alocação.

**Como Corrigir:**
1. Valide a conexão de malha executando `tailscale status`. Se o host não estiver listado, repita a execução técnica do Passo 2.
2. Remova e recrie as validações no Docker:
```bash
sudo docker compose -f docker-compose.yml -f docker-compose.n8n.yml down
sudo docker compose -f docker-compose.yml -f docker-compose.n8n.yml up -d
```
