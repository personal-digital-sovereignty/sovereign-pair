#!/bin/bash
# ==============================================================================
# Sovereign Pair - Desktop Application Builder (Tauri Sidecar Injector)
# ==============================================================================

set -e

echo "🚀 Iniciando Build do Sovereign Pair Desktop (macOS/Windows/Linux) com Sidecar..."

# 1. Compilar o Rust Core Native (O Cérebro)
echo "🧠 Compilando o Rust Backend em Release Mode..."
cd core
cargo build --release
cd ..

# 2. Preparar a Área de Sidecars
echo "📦 Preparando a pasta de Binários da Interface Tauri..."
mkdir -p svelte-ui/src-tauri/binaries/

# 3. Identificar o Host Triplet para o Tauri-Plugin-Shell
OS_TYPE=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH_TYPE=$(uname -m)
TAURI_TARGET=""

if [ "$OS_TYPE" = "darwin" ]; then
    if [ "$ARCH_TYPE" = "arm64" ]; then
        TAURI_TARGET="aarch64-apple-darwin"
    else
        TAURI_TARGET="x86_64-apple-darwin"
    fi
    cp core/target/release/sovereign-core svelte-ui/src-tauri/binaries/sovereign-core-$TAURI_TARGET
elif [[ "$OS_TYPE" == *"msys"* ]] || [[ "$OS_TYPE" == *"mingw"* ]] || [[ "$OS_TYPE" == *"cygwin"* ]]; then
    TAURI_TARGET="x86_64-pc-windows-msvc"
    cp core/target/release/sovereign-core.exe svelte-ui/src-tauri/binaries/sovereign-core-$TAURI_TARGET.exe
else
    # Linux
    TAURI_TARGET="x86_64-unknown-linux-gnu"
    cp core/target/release/sovereign-core svelte-ui/src-tauri/binaries/sovereign-core-$TAURI_TARGET
fi

echo "✅ Core ejetado para o formato Tauri Sidecar: binaries/sovereign-core-$TAURI_TARGET"

# 4. Acionar o Build Svelte + Tauri (.dmg, .exe, .AppImage)
echo "🎨 Compilando Svelte UI e Forjando Binário Mestre..."
cd svelte-ui
npm install
npm run build
npm run tauri build

echo "🎉 Build Concluído! Verifique a pasta svelte-ui/src-tauri/target/release/bundle/"
