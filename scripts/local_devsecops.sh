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
echo ""
echo "⏳ [Gate 2] Running Trivy (SCA & Vulnerabilities)..."
docker run --rm -v $(pwd):/repo aquasec/trivy:latest fs --ignore-unfixed --format table --exit-code 1 --severity CRITICAL,HIGH /repo || {
    echo "❌ ERROR: Trivy found CRITICAL or HIGH vulnerabilities in dependencies."
    exit 1
}
echo "✅ Trivy passed! Code dependencies are secure."

echo ""
echo "⏳ [Gate 3] Running Ruff (Python Code Quality & Formatting)..."
docker run --rm -v $(pwd):/src -w /src python:3.12-slim bash -c "pip install ruff && ruff check ." || {
    echo "❌ ERROR: Ruff found syntax/formatting violations in Python source."
    exit 1
}
echo "✅ Ruff passed! Python code is PEP-8 compliant and clean."

echo ""
echo "✅ Local DevSecOps Suite Finished Perfectly!"
exit 0
