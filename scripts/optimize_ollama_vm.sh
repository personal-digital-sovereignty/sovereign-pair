#!/bin/bash

# =========================================================================
# Sovereign Pair - VM Ollama Optimization (4 vCPUs / 8GB RAM)
# Phase 0.01 Constrained Environment Tuning
# =========================================================================
# This script configures the llama.cpp backend used by Ollama to optimally
# allocate 4 virtual cores and restrict RAM usage to prevent Native OS
# Out-of-Memory (OOM) kills on an 8GB RAM constraint.
# =========================================================================

echo "🔥 Iniciando Otimização do Ollama para Virtual Machine (4 vCPU / 8GB RAM)"
echo "------------------------------------------------------------------------"

# 1. Verificar privilégios de ROOT para o Systemd e SysFS
if [ "$EUID" -ne 0 ]; then
  echo "❌ ERRO: Por favor, execute este script como root (sudo ./optimize_ollama_vm.sh)"
  exit 1
fi

# 2. Criar Override SystemD para o serviço do Ollama
echo ">> [1/4] Configurando Variáveis de Ambiente Restritas (Systemd Override)..."

# Detectar se o Ollama está rodando como serviço do sistema ou usuário local
SYSTEMD_DIR="/etc/systemd/system/ollama.service.d"
mkdir -p "$SYSTEMD_DIR"

cat > "$SYSTEMD_DIR/override.conf" << 'CONF'
[Service]
# Threads limitados ao número de vCPUs disponíveis
Environment="OLLAMA_NUM_THREADS=4"
# Paralelização NULA para poupar RAM restrita (Processa 1 request por vez)
# NOTA: Diferente da máquina Ryzen local (OLLAMA_NUM_PARALLEL=3) — aqui mantemos em 1
# propositalmente pois 8GB RAM não suporta múltiplas inferências simultâneas sem OOM.
# Para escalar, use o nó Oracle Cloud (OLLAMA_NUM_PARALLEL=4) ou atualize a RAM da VM.
Environment="OLLAMA_NUM_PARALLEL=1"
# Estritamente 1 ÚNICO modelo na RAM simultaneamente para não estourar os 8GB
Environment="OLLAMA_MAX_LOADED_MODELS=1"

# Aceleração matemática limitando as threads para evitar context switching overhead
Environment="OPENBLAS_NUM_THREADS=4"
Environment="OMP_NUM_THREADS=4"

# Afinidade de CPU (Force uso dos núcleos 0 a 3)
Environment="GOMP_CPU_AFFINITY=0-3"

# Tuning de Memória Global Restrita (8GB RAM Base)
# Limite rígido da fila do Context Length
Environment="OLLAMA_MAX_QUEUE=128"
# Expulsar o modelo da RAM rapidamente (2 minutos) se ocioso, devolvendo a RAM para o Ubuntu
Environment="OLLAMA_KEEP_ALIVE=2m"

# Host Binding (Permitir acesso Docker/Sovereign Pair dentro da VM)
Environment="OLLAMA_HOST=0.0.0.0:11434"
CONF

echo "   [OK] Arquivo systemd override restrito criado."

# 3. CPU Governor para Performance
echo ">> [2/4] Modificando CPU Scaling Governor para 'performance'..."
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    if [ -f "$cpu" ]; then
        echo "performance" > "$cpu"
    fi
done
echo "   [OK] Núcleos forçados em modo performance (se suportado pelo Hypervisor)."

# 4. HUGEPAGES (Acesso massivo à RAM para LLM)
# 8GB = ~8000MB. Reservando 1.5GB em HugePages para os tensores do Ollama
echo ">> [3/4] Habilitando HugePages Conservador (1.5GB) para acelerar busca..."
echo "vm.nr_hugepages = 768" > /etc/sysctl.d/99-hugepages-ollama.conf
sysctl -p /etc/sysctl.d/99-hugepages-ollama.conf > /dev/null 2>&1
echo "   [OK] HugePages Kernel Tuned para contenção de 8GB."

# 5. Reiniciar o serviço do Ollama
echo ">> [4/4] Recarregando o Daemon e o Serviço do Ollama..."
systemctl daemon-reload
systemctl restart ollama
echo "   [OK] Ollama reiniciado com as flags de Racionamento e Força Bruta!"
echo "------------------------------------------------------------------------"

echo "✅ SUCESSO! A VM está tunada para RAG Local In-Memory."
echo "➡️ DICA: Em máquinas com 8GB, evite carregar modelos acima de 4B (Use Llama-3.2:3b ou Qwen2.5:3b q4_K_M)."
echo "------------------------------------------------------------------------"
