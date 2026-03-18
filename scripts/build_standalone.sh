#!/bin/bash
set -e

echo "=> Building Sovereign Pair Standalone Binaries..."

echo "1. Building Rust Core..."
cd core
cargo build --release
cd ..
echo "[OK] Rust Core built."

echo "2. Installing PyInstaller..."
pip install pyinstaller

echo "3. Compiling Python API natively..."
pyinstaller --name sovereign-api --clean --onefile \
  --hidden-import=llama_index \
  --hidden-import=sqlalchemy \
  --hidden-import=pydantic \
  --hidden-import=uvicorn \
  --hidden-import=fastapi \
  --paths=src \
  src/api/main.py
echo "[OK] Python API compiled."

echo "=> All standalone binaries generated in 'dist/' and 'core/target/release/'"
