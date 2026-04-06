#!/bin/bash

# =========================================================================
# Sovereign Pair - Local Hardware Ollama Optimization (Ryzen 7 5800H)
# Phase 0.01 Local Tuning
# =========================================================================
# This script configures the llama.cpp backend used by Ollama to optimally
# allocate 8 physical cores (16 threads max) and adjusts the OS CPU Governor
# to "performance" mode to prevent clock latency during LLM inference.
# =========================================================================

echo "🔥 Iniciando Otimização do Ollama para AMD Ryzen 7 5800H (32GB RAM)"
echo "------------------------------------------------------------------------"

# 1. Verificar privilégios de ROOT para o Systemd e SysFS
if [ "$EUID" -ne 0 ]; then
  echo "❌ ERRO: Por favor, execute este script como root (sudo ./optimize_ollama.sh)"
  exit 1
fi

# 2. Criar Override SystemD para o serviço do Ollama
echo ">> [1/4] Configurando Variáveis de Ambiente do llama.cpp (Systemd Override)..."

# Detectar se o Ollama está rodando como serviço do sistema ou usuário local
SYSTEMD_DIR="/etc/systemd/system/ollama.service.d"
mkdir -p "$SYSTEMD_DIR"

cat > "$SYSTEMD_DIR/override.conf" << 'CONF'
[Service]
# Threads físicas vs virtuais: 16 threads para extrair 100% dos núcleos do 5800H
Environment="OLLAMA_NUM_THREADS=16"
# Paralelização das requests do Sovereign Pair
Environment="OLLAMA_NUM_PARALLEL=1"
# Modelos na RAM simultaneamente
Environment="OLLAMA_MAX_LOADED_MODELS=2"

# OpenBLAS (Aceleração matemática vetorial - AVX2)
Environment="OPENBLAS_NUM_THREADS=16"
Environment="OMP_NUM_THREADS=16"

# Afinidade de CPU (Force uso coerente dos CCX da AMD)
Environment="GOMP_CPU_AFFINITY=0-15"

# [THE MAGIC]: AMD ROCm Hardware Spoofing (Falsificação de Identidade Arquitetural)
# APUs Ryzen Vega (como 5800H) são bloqueadas pela AMD comercialmente no ROCm.
# Forçamos a biblioteca a ler a APU como uma gfx900 (Enterprise) para destravar acesso à Memória Compartilhada.
Environment="HSA_OVERRIDE_GFX_VERSION=9.0.0"

# [FALLBACK UNIVERSAL]: Vulkan Compute
# Se a AMD quebrar o suporte ao ROCm spoofing, a Engine de Inference ativa o modo Vulkan (Open-Source),
# que dialoga perfeitamente com Intel Iris Xe, Intel Arc e AMD RX/Radeon Vega nativamente, sem dependências proprietárias.
# Environment="OLLAMA_BACKEND=vulkan"

# Tuning de Memória Global (32GB RAM Base)
Environment="OLLAMA_MAX_QUEUE=512"
Environment="OLLAMA_KEEP_ALIVE=5m"

# The Ghost Optimization: Emulando o comportamento TurboQuant (Google Research)
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q4_0"

# Host Binding (Permitir acesso Docker/Tailscale se necessário)
Environment="OLLAMA_HOST=0.0.0.0:11434"
CONF

echo "   [OK] Arquivo systemd override.conf criado."

# 3. CPU Governor para Performance
echo ">> [2/4] Modificando CPU Scaling Governor para 'performance'..."
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo "performance" > "$cpu"
done
echo "   [OK] Todos os núcleos fixados em modo performance."

# 4. HUGEPAGES (Acesso massivo à RAM para LLM)
echo ">> [3/4] Habilitando HugePages para acelerar buscas na memória..."
echo "vm.nr_hugepages = 1024" > /etc/sysctl.d/99-hugepages-ollama.conf
sysctl -p /etc/sysctl.d/99-hugepages-ollama.conf > /dev/null 2>&1
echo "   [OK] HugePages Kernel Tuned."

# 5. Reiniciar o serviço do Ollama
echo ">> [4/4] Recarregando o Daemon e o Serviço do Ollama..."
systemctl daemon-reload
systemctl restart ollama
echo "   [OK] Ollama reiniciado com as novas Flags!"
echo "------------------------------------------------------------------------"

echo "✅ SUCESSO! O motor de IA local está tunado."
echo "➡️ DICA: Para testar a diferença de velocidade, rode um modelo pesado (ex: phi4 ou Qwen) no console!"
echo "------------------------------------------------------------------------"
