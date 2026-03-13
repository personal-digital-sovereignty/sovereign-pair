#!/bin/bash
# ==============================================================================
# Sovereign Pair - OCI Blue Collar Node Bootstrap Script
# Target: Oracle Cloud Infrastructure - A1 (ARM64) - Ubuntu 22.04 / 24.04
# Description: Installs Docker, Tailscale, and Native Ollama C++ for max TPS
# ==============================================================================

set -e

echo "[1/4] Atualizando pacotes de Sistema O.S..."
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y curl wget git jq htop vim ufw python3-pip python3-venv sqlite3

echo "[2/4] Instalando Tailscale (Sovereign Mesh VPN)..."
if ! command -v tailscale &> /dev/null; then
  curl -fsSL https://tailscale.com/install.sh | sh
  echo ">>> Tailscale instalado. Por favor, rode manualmente após script: 'sudo tailscale up' <<<"
else
  echo "Tailscale já instalado."
fi

echo "[3/4] Instalando Docker Engine Oficial (Orquestrador Blue Collar Worker)..."
if ! command -v docker &> /dev/null; then
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker $USER
  rm get-docker.sh
else
  echo "Docker já instalado."
fi

echo "[4/4] Instalando Ollama Engine Nativamente no Host (C++ Native para ARM64)..."
# Usamos nativo host-OS Ollama em vez de Docker para evitar overheads de Virtualização
# de Memory Bus, maximizando o T/s da Cota A1 gratuita da Oracle.
if ! command -v ollama &> /dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh
  
  echo "Configurando Ollama para escutar na porta Tailscale 100.x e localhost..."
  # Ajuste do systemd para bind global nas interfaces (UFW bloqueará rede pública)
  sudo mkdir -p /etc/systemd/system/ollama.service.d
  cat <<EOF | sudo tee /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"
EOF
  sudo systemctl daemon-reload
  sudo systemctl restart ollama
else
  echo "Ollama já instalado."
fi

echo "=============================================================================="
echo "🎯 SOVEREIGN NODE PROVISIONADO COM SUCESSO!"
echo "Próximos passos (Ação Mestra):"
echo "1. Rode 'sudo tailscale up' para juntar este servidor à God Mode Subnet."
echo "2. Feche a porta 11434 no firewall externo (Oracle Console) caso aberta."
echo "3. Execute 'docker compose up -d' no diretório infra/oci para subir a Spider."
echo "=============================================================================="
