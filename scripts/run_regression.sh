#!/bin/bash
# Sovereign Pair - Master Regression Tester
# Validate all structural tiers before branching or merging.

set -e

echo "================================================="
echo "🛡️ SOVEREIGN PAIR V4 - REGRESSION TEST SUITE 🛡️"
echo "================================================="

echo -e "\n[1/3] Validating Backend Engine (FastAPI & Models) 🚀"
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual Environment (.venv) not found. Please activate it first."
    exit 1
fi
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v

echo -e "\n[2/3] Validating Sovereign Agents (Logic & RAG) 🧠"
PYTHONPATH=. pytest tests/test_agents.py -v

echo -e "\n[3/3] Validating Web-UI Dom (Vue 3 Playwright) 🌐"
cd web-ui
npm run test:e2e
cd ..

echo -e "\n✅ ALL TACTICAL CORTEX REGRESSIONS PASSED SUCCESSFULLY."
echo "================================================="
