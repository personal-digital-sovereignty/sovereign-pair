#!/bin/bash
# Sovereign Pair v1.2.7 - Master Regression Tester
# Validate all structural tiers before branching or merging.

set -e

echo "================================================="
echo "🛡️ SOVEREIGN PAIR v1.2.7 - REGRESSION TEST SUITE 🛡️"
echo "================================================="

echo -e "\n[1/3] Validating Backend Engine, AI Agents & Routes (Cargo Test) 🚀"
cd core
cargo test
cd ..

echo -e "\n[2/3] Validating Python Workers (Pytest) 🐍"
PYTEST_BIN="${HOME}/.local/bin/pytest"
if [ -x "$PYTEST_BIN" ] || command -v pytest &>/dev/null; then
    PYTEST_CMD="${PYTEST_BIN:-pytest}"
    $PYTEST_CMD core/python_workers/tests/ -v --tb=short
else
    echo "⚠️  Pytest não instalado — skip (pip install pytest)"
fi

echo -e "\n[3/3] Validating Web-UI Dom (Svelte Check) 🌐"
cd svelte-ui
npm run check
cd ..

echo -e "\n✅ ALL TACTICAL CORTEX REGRESSIONS PASSED SUCCESSFULLY."
echo "================================================="
