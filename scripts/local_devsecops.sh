#!/bin/bash

# ==============================================================================
# Sovereign Pair - Local DevSecOps Gauntlet
# ==============================================================================
# Instantiates containerized parsers locally to mirror the exact tools 
# validated by the GitHub Actions `devsecops.yml` runner (ActionLint, Semgrep).

set -e

echo "==========================================================="
echo "🛡️  Sovereign Pair Local DevSecOps Extractor 🛡️"
echo "==========================================================="

echo ""
echo "⏳ [Gate 0] Running ActionLint (GitHub Actions YAML Validation)..."
docker run --rm -v $(pwd):/repo --workdir /repo rhysd/actionlint:latest || {
    echo "❌ ERROR: ActionLint found syntax violations in .github/workflows/"
    exit 1
}
echo "✅ ActionLint Passed! Workflow scripts are verified."

echo ""
echo "⏳ [Gate 1] Running Semgrep SAST Scanner..."
# Fetches local python/javascript issues avoiding unauthenticated pulls
docker run --rm -v $(pwd):/src -w /src returntocorp/semgrep semgrep scan --config auto || {
    echo "❌ ERROR: Semgrep Security Scan caught vulnerabilities."
    exit 1
}
echo "✅ Semgrep passed! Static analysis returned clean."

echo ""
echo "✅ Local DevSecOps Suite Finished Perfectly!"
exit 0
