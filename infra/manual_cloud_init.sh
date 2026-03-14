#!/bin/bash
set -e

echo "=========================================================="
echo "🛡️ Sovereign Pair - Manual Cloud-Init Fallback Recovery"
echo "=========================================================="

export DEBIAN_FRONTEND=noninteractive

# 1. Oracle APT Fix
sudo sed -E -i 's/[a-z0-9-]+\.clouds\.ports\.ubuntu\.com/ports.ubuntu.com/g' /etc/apt/sources.list

# 2. System Packages
echo "[1/7] Updating apt and installing core packages..."
sudo -E apt-get update -y
sudo -E apt-get upgrade -y
sudo -E apt-get install -y curl wget git zram-tools sqlite3

# 3. ZRAM
echo "[2/7] Configuring ZRAM..."
sudo systemctl enable --now zramswap || echo "Warning: ZRAM enable failed"
sudo systemctl restart zramswap || echo "Warning: ZRAM restart failed"

# 4. Tailscale
echo "[3/7] Installing Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sudo sh || echo "Tailscale already installed"

# 5. Ollama
echo "[4/7] Installing Ollama Engine..."
curl -fsSL https://ollama.com/install.sh | sudo sh || echo "Ollama already installed"
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl restart ollama

echo "[5/7] Pulling LLMs in background..."
sudo bash -c "nohup ollama pull qwen2.5-coder:7b > /var/log/ollama_pull_coder_fallback.log 2>&1 &"
sudo bash -c "nohup ollama pull llama3.2:3b > /var/log/ollama_pull_doctor_fallback.log 2>&1 &"

# 6. Docker Engine
echo "[6/7] Installing Docker..."
curl -fsSL https://get.docker.com | sudo sh || echo "Docker already installed"
sudo systemctl enable docker
sudo systemctl start docker

# 7. Network Fixes
echo "[7/7] Applying network patches..."
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1
sudo sysctl -w net.ipv6.conf.lo.disable_ipv6=1

# 8. Cloning Repo
if [ ! -d "/opt/sovereign-pair" ]; then
    echo "Cloning Sovereign Pair..."
    sudo git clone https://github.com/Personal-Digital-Sovereignty/sovereign-pair.git /opt/sovereign-pair
else
    echo "Repository already path exists. Skipping clone."
fi

cd /opt/sovereign-pair
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    sudo cp .env.example .env
fi
sudo mkdir -p ./data/vault

echo "=========================================================="
echo "✅ Manual Setup Completed Successfully! "
echo "Next steps:"
echo "1. Validate your .env file in /opt/sovereign-pair/.env (Add Tailscale Auth Key)"
echo "2. Run 'sudo tailscale up --ssh'"
echo "3. Run 'docker compose up -d' in infra/docker/"
echo "=========================================================="
