#!/bin/bash

# ==============================================================================
# Sovereign Pair - Local CI/CD Pre-Push Gateway (Phase 30)
# ==============================================================================
# This hook runs locally before `git push`.
# It guarantees that no broken code is ever pushed to the GitHub origin by
# executing the exact same test suites as the remote GitHub Actions pipeline.
#
# If any of the steps below fail (exit code != 0), the push is aborted.

echo "==========================================================="
echo "🛡️  Sovereign Pair Pre-Push Gateway Initiated"
echo "==========================================================="

# 1. Python Backend Tests (pytest)
echo ""
echo "⏳ Running Python Backend Tests (pytest)..."
# Using the local `.venv` or system python depending on how the Dev runs it.
# We explicitly activate the local .venv to ensure GUI Git clients (VSCode/Kraken) resolve dependencies.
if [ -d ".venv" ]; then
    echo "   [Context] Activating local .venv..."
    source .venv/bin/activate
fi

python3 -m pytest tests/ || {
    echo "❌ ERROR: Python backend tests failed. Aborting push."
    echo "Please fix the failing tests before pushing your code."
    exit 1
}
echo "✅ Backend tests passed."

# 2. Vue Frontend Tests & Linting
echo ""
echo "⏳ Running Vue Frontend Builder & Type Checking..."
cd web-ui || {
    echo "❌ ERROR: Directory 'web-ui' not found. Aborting push."
    exit 1
}

# Run the TypeScript build checker (vue-tsc)
npm run build || {
    echo "❌ ERROR: Vue frontend build or TypeScript check failed. Aborting push."
    echo "Please run 'npm run build' inside web-ui to see the exact errors."
    exit 1
}
echo "✅ Frontend build passed."
cd ..

# 3. Gitleaks Secret Scanning (Docker Native)
echo ""
echo "⏳ Running Gitleaks Secret Scanner..."
docker pull zricethezav/gitleaks:latest -q

GITLEAKS_ENV=""
if [ -f ".gitleaks.key" ]; then
    echo "   [Context] Custom .gitleaks.key found! Injecting enterprise license..."
    GITLEAKS_ENV="-e GITLEAKS_LICENSE=$(cat .gitleaks.key)"
fi

docker run --rm $GITLEAKS_ENV -v $(pwd):/path zricethezav/gitleaks:latest detect --source="/path" -v || {
    echo "❌ ERROR: Gitleaks detected secrets! Aborting push to protect repository."
    echo "Check the report above to remove leaked credentials."
    exit 1
}
echo "✅ Secret Scan passed. No active leaks detected."

# 4. Success & Continuous Deployment (Local OCI Rebuild)
echo ""
echo "==========================================================="
echo "🟢 All clear! Gateway approved the push."
echo "==========================================================="

echo "⏳ Triggering Local OCI Fast-Rebuild (Phase 32 Automaton)..."
if [ -x "scripts/rebuild-sensus.sh" ]; then
   ./scripts/rebuild-sensus.sh
else
   echo "⚠️ Warning: scripts/rebuild-sensus.sh not found or not executable. Skipping hot-reload."
fi

exit 0
