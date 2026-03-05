# Sovereign Pair - Testing Methodology and Scope (QA & SRE)

**Quality Matrix:** Release 3.3.0
**Frameworks:** Pytest, Playwright (E2E), Moto (Infra Mocking)
**SecOps Directive:** Zero-Bypass (No permission for Linters Bypass or Secret Leaks)

This treaty formalizes the Software Quality Assurance (QA) operations for the Sovereign Pair RAG Cibrid ecosystem. It is intended for core developers integrating the Python FastAPI meshes and the orchestrated Vue interface integrations.

---

## 1. Test Suite Topology (Test Hierarchy)

After the architectural re-engineering of Phase 42, the repository root was sanitized. Sovereign Pair does not allow standalone `test_*.py` scripts at the root of the project. Every functional test must strictly inherit the guidelines and allocations of one of the four underlying ontological layers of the `/tests` directory.

### 1.1 `tests/unit/` (Fast / Atomic Layer)
Dedicated exclusively to testing pure functions and algorithmic entities isolated from Network or Disk I/O.
- **Mandate:** *No Network, No Disk.* Mocks are mandatory for any call to `ChromaDB`, `Ollama`, or External APIs.
- **Covered Domain:** The Accountant's Calculation Engine, Ingestion Hash converters, and the structural semantic router (Without actual token dispatch).
- **Time Limit:** Must run in parallel via `pytest-xdist` in fractions of seconds.

### 1.2 `tests/integration/` (Subsystem Integration Layer)
Evaluates the symbiotic cohesion of two or multiple service meshes (e.g., FastAPI communicating with the SQLAlchemy Repository and Tailscale Auth).
- **Mandate:** Allows the transient instantiation of In-Memory mapped Relational Databases (`sqlite:///:memory:`) or temporary Docker Containers (Testcontainers).
- **Covered Domain:** `/v1/chat` API Routes, Header JWT verification, intentional failures (Chaos) against RAG infrastructure instability.

### 1.3 `tests/e2e/` (End-To-End / Playwright)
The final tip-of-the-spear layer. Spawns a hidden-profile WebKit/Chromium browser that effectively clicks buttons on the Vue Interfaces.
- **Mandate:** The system must be 100% up locally (`docker compose up`) on both the Client App and API fronts.
- **Covered Domain:** The complete flow where the RAG absorbs a physical local note and reflects its instantaneous read on the side UI while the SSE Engine squirts the predictive fill responses.

### 1.4 `tests/legacy/` (Dead Archive / Deep Storage)
A *Read-Only* asylum for tests conceived by engineers prior to the adoption of the rigid corporate TDD model of version 3.3.0.
- **Purpose:** Logical preservation of the software's evolution. Contains Proofs of Concept (PoCs) and original system *Smoke Tests*.
- **Attention:** The Github Actions CI pipeline purposefully ignores this branch. Developers must not alter the historical content deposited here.

---

## 2. CI/CD Restricted Execution (Zero-Bypass Policy)

Since the adoption of DevSecOps in Release 3.1.0, continuous Orchestration is based on a total-interdiction failure protocol.

### 2.1 Linting & Formatting (Ruff)
The C-based Linter formatter (Ruff) operates under standardized PEP-8 boundaries without leniency.
- The use of `# noqa` to bypass technical debt or bare `except:` clauses is blocked at the root.
- Absolute imports of underlying variables enforced the existence of the `/tests/conftest.py` file injecting the absolute root into `sys.path`. We demand impeccable formatting and correct Pydantic typing upon git submissions.

### 2.2 Secrets Shielding (Gitleaks)
No Push is dispatched to the matrix cloud without the scrutiny of the passwords and PII credentials detector.
- Mock Database `.py` test files forge altered cryptographic RSA headers to prevent False Positive scans from intercepting unreal keys (which previously broke The Action and impeded automatic AWS Deployments).

---

## 3. Local Ignition Instructions (Runbook)

The global invocation of the pipeline tests can be processed solely with the tools packaged in `requirements.txt`.

### 3.1 Unit Suite and Limited Integration
The execution of the purist base (excludes the Playwright Chrome browser) utilizes the parameterized root directives:
```bash
# At the root of your active repository
python -m pytest tests/unit/ tests/integration/ -v --tb=short
```

### 3.2 Singular Debug Execution (Verbose Log)
When engineering focuses strictly on resolving a node of the Ingestion module:
```bash
python -m pytest tests/unit/test_ingestion_logic.py -s -v --log-cli-level=DEBUG
```

### 3.3 Systemic Coverage Reports
To evaluate gaps and blind spots in the attached RAG codebase via `pytest-cov`:
```bash
python -m pytest --cov=src --cov-report=term-missing tests/unit/
```

---

**Referenced Technical Glossary:** See `docs/glossary.en-US.md`.