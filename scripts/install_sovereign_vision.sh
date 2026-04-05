#!/bin/bash
# Sovereign Pair - Multimodal Vision Engine Downloader (Bare-Metal)
# This script sets up a lightweight, zero-dependency stable-diffusion.cpp backend.
# It bypasses Heavy Python/CUDA dependencies and targets local Ryzen APU/CPU or Generic hardware.

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}  SOVEREIGN VISION: Txt2Img Local Engine Setup   ${NC}"
echo -e "${BLUE}=================================================${NC}"

BASE_DIR="$HOME/Sovereign_LLM/Vision"
MODEL_DIR="$BASE_DIR/models"

mkdir -p "$MODEL_DIR"
cd "$BASE_DIR"

echo -e "${YELLOW}[*] Baixando binário pré-compilado do stable-diffusion.cpp...${NC}"
# Bypassing the compile step to prevent missing dependencies. We fetch the latest stable Linux x64 binary.
wget -qO sd-master.zip https://github.com/leejet/stable-diffusion.cpp/releases/download/master-8686f05/sd-master-8686f05-bin-linux-avx2-openblas-x64.zip || {
    echo -e "${YELLOW}[!] Zip master indisponível. Tentando compilação nativa falha-segura...${NC}"
    if [ ! -d "stable-diffusion.cpp" ]; then
        git clone --recursive https://github.com/leejet/stable-diffusion.cpp
    fi
    cd stable-diffusion.cpp
    mkdir -p build && cd build
    cmake .. -DSD_BUILD_EXAMPLES=ON
    cmake --build . --config Release
    cd ../..
}

if [ -f "sd-master.zip" ]; then
    unzip -oq sd-master.zip -d sd_bin
    rm sd-master.zip
    chmod +x sd_bin/sd
fi

echo -e "${GREEN}[+] Motor sd.cpp (OpenBLAS/Vulkan) alocado localmente.${NC}"

echo -e "${YELLOW}[*] Baixando Peso Otimizado (SDXL Turbo GGUF de 4 Passos) para alta velocidade...${NC}"
wget -qcO "$MODEL_DIR/sdxl_turbo.gguf" "https://huggingface.co/leejet/sdxl-turbo-gguf/resolve/main/sdxl_turbo-Q8_0.gguf"

echo -e "${GREEN}[+] O Peso de Inteligência Visual (SDXL Turbo - Q8) foi arquivado com sucesso no Disco!${NC}"

echo -e "\n${BLUE}=================================================${NC}"
echo -e "${GREEN} 🚀 INTELIGÊNCIA VISUAL INSTALADA COM SUCESSO! 🚀 ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "O Sovereign Multimodal Engine está pronto. Para levantar o servidor,"
echo -e "execute este comando sempre que quiser desenhar via Chat Svelte:\n"

if [ -d "sd_bin" ]; then
    echo -e "${YELLOW}cd $BASE_DIR/sd_bin && ./sd-server --port 7860 -m $MODEL_DIR/sdxl_turbo.gguf${NC}\n"
else
    echo -e "${YELLOW}cd $BASE_DIR/stable-diffusion.cpp/build/bin && ./sd-server --port 7860 -m $MODEL_DIR/sdxl_turbo.gguf${NC}\n"
fi

echo -e "Pronto Comandante. Pode dar o /start na engine quando desejar."
