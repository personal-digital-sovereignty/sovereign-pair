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

echo "=> All standalone binaries generated in 'core/target/release/'. Standalone process complete."
