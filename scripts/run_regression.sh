#!/bin/bash
# Sovereign Pair - Master Regression Tester
# Validate all structural tiers before branching or merging.

set -e

echo "================================================="
echo "🛡️ SOVEREIGN PAIR V4 - REGRESSION TEST SUITE 🛡️"
echo "================================================="

echo -e "\n[1/2] Validating Backend Engine, AI Agents & Routes (Cargo Test) 🚀"
cd core
cargo test
cd ..

echo -e "\n[2/2] Validating Web-UI Dom (Svelte Check) 🌐"
cd svelte-ui
npm run check
cd ..

echo -e "\n✅ ALL TACTICAL CORTEX REGRESSIONS PASSED SUCCESSFULLY."
echo "================================================="
