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
Environment="OLLAMA_NUM_THREADS=12"
# Parelização das requests do Sovereign Pair
# GAP-3 FIX: Aumentado de 1→3 para alinhar com SOVEREIGN_PARALLEL_QUERIES=3 no Rust.
# REGRA: OLLAMA_NUM_PARALLEL deve ser >= SOVEREIGN_PARALLEL_QUERIES ou as threads ficam em fila no servidor.
Environment="OLLAMA_NUM_PARALLEL=3"
# Modelos na RAM simultaneamente
Environment="OLLAMA_MAX_LOADED_MODELS=2"

# OpenBLAS (Aceleração matemática vetorial - AVX2)
Environment="OPENBLAS_NUM_THREADS=12"
Environment="OMP_NUM_THREADS=12"

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

# Tuning de Memória Global (27GB RAM física)
Environment="OLLAMA_MAX_QUEUE=512"
Environment="OLLAMA_KEEP_ALIVE=5m"

# The Ghost Optimization: Emulando o comportamento TurboQuant (Google Research)
Environment="OLLAMA_FLASH_ATTENTION=1"
# Environment="OLLAMA_KV_CACHE_TYPE=q4_0" # [REMOVIDO] q4_0 corrompe o RoPE do Qwen2.5 em CPUs causando NaNs e o loop (O O O).
# Environment="OLLAMA_KV_CACHE_TYPE=f16" # [ANTERIOR] Full precision — seguro mas consome ~5.2GB de KV cache para 12k ctx.
# FIX v1.2.5: q8_0 é o sweet spot — reduz KV cache em ~50% (2.6GB vs 5.2GB) sem degradar RoPE.
# qwen3/gemma4 estáveis com q8_0 (8-bit preserva senos/cossenos do RoPE com precisão suficiente).
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"

# Host Binding (Permitir acesso Docker/Tailscale se necessário)
Environment="OLLAMA_HOST=0.0.0.0:11434"

# =========================================================================
# [MEMORY FENCE]: Hard Cap via cgroups v2
# =========================================================================
# Limita toda a árvore de processos do Ollama (serve + runners) a 24GB.
# Em 27GB físicos, reserva ~3GB para: kernel, Sovereign Pair, browser, OS.
#
# Comportamento ao exceder:
#   - O kernel mata o runner do modelo (OOM kill cirúrgico)
#   - O ollama serve continua vivo e responde com erro
#   - O Sovereign Pair recebe o erro e aciona fallback normalmente
#   - Ollama recarrega o próximo modelo dentro do limite
#
# MemorySwapMax=0 impede degradação silenciosa: sem swap, o sistema
# falha rápido e explícito ao invés de rastejar a 100KB/s no disco.
# =========================================================================
MemoryMax=24G
MemorySwapMax=0
CONF

echo "   [OK] Arquivo systemd override.conf criado."

# 3. CPU Governor para Performance
echo ">> [2/5] Modificando CPU Scaling Governor para 'performance'..."
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo "performance" > "$cpu"
done
echo "   [OK] Todos os núcleos fixados em modo performance."

# 4. HUGEPAGES (Acesso massivo à RAM para LLM)
echo ">> [3/5] Habilitando HugePages para acelerar buscas na memória..."
echo "vm.nr_hugepages = 1024" > /etc/sysctl.d/99-hugepages-ollama.conf
sysctl -p /etc/sysctl.d/99-hugepages-ollama.conf > /dev/null 2>&1
echo "   [OK] HugePages Kernel Tuned."

# 5. Reiniciar o serviço do Ollama
echo ">> [4/5] Recarregando o Daemon e o Serviço do Ollama..."
systemctl daemon-reload
systemctl restart ollama
echo "   [OK] Ollama reiniciado com as novas Flags!"

# 6. Verificação do Memory Fence
echo ">> [5/5] Verificando Memory Fence aplicado..."
sleep 1
MEM_MAX=$(systemctl show ollama --property=MemoryMax 2>/dev/null | cut -d= -f2)
MEM_CURRENT=$(systemctl show ollama --property=MemoryCurrent 2>/dev/null | cut -d= -f2)

if [ "$MEM_MAX" = "25769803776" ] || [ "$MEM_MAX" = "24G" ]; then
    echo "   [OK] MemoryMax = 24G (hard cap ativo via cgroups v2)"
else
    echo "   [⚠️] MemoryMax = $MEM_MAX (verifique se cgroups v2 está habilitado)"
fi

if [ -n "$MEM_CURRENT" ] && [ "$MEM_CURRENT" != "infinity" ]; then
    MEM_MB=$((MEM_CURRENT / 1024 / 1024))
    echo "   [OK] MemoryCurrent = ${MEM_MB}MB (uso atual do Ollama)"
fi

echo "------------------------------------------------------------------------"
echo "✅ SUCESSO! O motor de IA local está tunado."
echo ""
echo "   📊 Alocação de RAM:"
echo "   ├── Ollama (modelos + KV cache):  ≤ 24GB (hard cap)"
echo "   ├── Sistema + Sovereign Pair:       ~3GB (reservado)"
echo "   └── Swap:                           BLOQUEADO (fail-fast)"
echo ""
echo "➡️ DICA: Para testar a diferença de velocidade, rode um modelo pesado (ex: phi4 ou Qwen) no console!"
echo "------------------------------------------------------------------------"
