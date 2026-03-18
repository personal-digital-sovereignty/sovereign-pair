#!/bin/bash
set -e

echo "=> Building Sovereign Pair Standalone Binaries..."

echo "0. Building Web UI (Vue 3)..."
cd web-ui
npm install
npm run build
cd ..

echo "1. Building Rust Core..."
cd core
cargo build --release
cd ..
echo "[OK] Rust Core built."

echo "2. Installing PyInstaller (via venv)..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
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

deactivate
echo "[OK] Python API compiled."

echo "=> All standalone binaries generated in 'dist/' and 'core/target/release/'"
