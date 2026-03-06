#!/bin/bash
# Sovereign Pair - Master Regression Tester
# Validate all structural tiers before branching or merging.

set -e

echo "================================================="
echo "🛡️ SOVEREIGN PAIR V4 - REGRESSION TEST SUITE 🛡️"
echo "================================================="

echo -e "\n[1/2] Validating Backend Engine, AI Agents & Routes (Pytest) 🚀"
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual Environment (.venv) not found. Please activate it first."
    exit 1
fi
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v

echo -e "\n[2/2] Validating Web-UI Dom (Vue 3 Playwright) 🌐"
cd web-ui
npm run test:e2e
cd ..

echo -e "\n✅ ALL TACTICAL CORTEX REGRESSIONS PASSED SUCCESSFULLY."
echo "================================================="
