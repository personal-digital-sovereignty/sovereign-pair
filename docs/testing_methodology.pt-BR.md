# Sovereign Pair - Metodologia e Escopo de Testes (QA & SRE)

**Matriz de Qualidade:** Release 3.3.0
**Frameworks:** Pytest, Playwright (E2E), Moto (Infra Mocking)
**Diretiva SecOps:** Zero-Bypass (Sem permissão para Linters Bypass ou Secret Leaks)

Este tratado formaliza as operações de garantia da qualidade de software (QA) para o ecossistema Cíbrido do Sovereign Pair RAG. Destina-se aos desenvolvedores do núcleo que integram as malhas Python do FastAPI e as integrações orquestradas da interface Vue.

---

## 1. Topologia da Suíte de Testes (Test Hierarchy)

Após a reengenharia arquitetural da Fase 42, a raiz do repositório foi higienizada. O Sovereign Pair não admite scripts `test_*.py` avulsos na raiz do projeto. Todo teste funcional deve estritamente herdar as diretrizes e alocações de uma das quatro camadas ontológicas subjacentes do diretório `/tests`.

### 1.1 `tests/unit/` (Camada Rápida / Atômica)
Dedicada exclusivamente ao teste de funções puras e entidades algorítmicas isoladas de I/O de rede ou disco.
- **Mandato:** *No Network, No Disk.* Mocks são obrigatórios para qualquer chamada ao `ChromaDB`, `Ollama`, ou APIs Externas.
- **Domínio Coberto:** O Engine de Cálculo do Accountant, conversores Hash de Ingestão e o roteador semântico estrutural (Sem envio real de token).
- **Tempo Limite:** Deve rodar paralelamente via `pytest-xdist` em frações de segundos.

### 1.2 `tests/integration/` (Camada de Integração de Subsistemas)
Avalia a coesão simbiótica de duas ou múltiplas malhas de serviço (Ex: FastAPI comunicando com o Repositório SQLAlchemy e o Tailscale Auth).
- **Mandato:** Permite o instanciamento transitório de Bancos Relacionais mapeados em Memória (`sqlite:///:memory:`) ou Containers Docker temporários (Testcontainers).
- **Domínio Coberto:** Rotas API `/v1/chat`, verificação JWT de Header, falhas intencionais (Chaos) contra a instabilidade da infraestrutura RAG.

### 1.3 `tests/e2e/` (End-To-End / Playwright)
Camada final da ponta de Lança. Aciona um navegador WebKit/Chromium de perfil oculto que efetivamente aperta os botões nas Interfaces do Vue.
- **Mandato:** Sistema precisa estar 100% de pé localmente (`docker compose up`) nas frentes de Client App e API.
- **Domínio Coberto:** O fluxo total onde o RAG absorve uma nota física local e reflete sua leitura instantânea na UI lateral enquanto o Motor SSE espirra as respostas de preenchimento preditivo.

### 1.4 `tests/legacy/` (Arquivo Morto / Deep Storage)
Um asilo *Read-Only* de testes concebidos por engenheiros anteriores à adoção do modelo corporativo TDD rígido da versão 3.3.0.
- **Propósito:** Preservação lógica da evolução do software. Contém provas conceituais (PoCs) e *Smoke Tests* do sistema original.
- **Atenção:** Pipeline CI do Github Actions ignora propositalmente esta ramificação. Desenvolvedores não devem alterar o conteúdo histórico depositado aqui.

---

## 2. CI/CD Execução Restrita (Zero-Bypass Policy)

A partir da adoção do DevSecOps na Release 3.1.0, a Orquestração contínua baseia-se num protocolo de falhas por interdição total.

### 2.1 Linting & Formatting (Ruff)
O formatador em C do Linter (Ruff) opera sob os limites PEP-8 padronizados sem condescendência.
- O uso de `# noqa` para contornar dívidas técnicas ou exceções bare `except:` é bloqueado na raiz.
- Imports absolutos de variáveis subjacentes forçaram a existência do arquivo `/tests/conftest.py` injetando a raíz absoluta no `sys.path`. Exigimos formatação impecável e tipificação Pydantic correta perante submissões no git.

### 2.2 Blindagem de Segredos (Gitleaks)
Nenhum Push é despachado para a nuvem matriz sem o crivo do detector de senhas e credenciais PII.
- Arquivos de teste da Mock Database em `.py` forjam cabeçalhos RSA criptográficos alterados para impossibilitar escaneamentos Falsos Positivos de interceptarem chaves irreais (que antes quebravam The Action e impediam Deploys automáticos AWS).

---

## 3. Instruções de Ignição Local (Runbook)

A invocação global dos testes da esteira pode ser processada unicamente com as ferramentas empacotadas no `requirements.txt`.

### 3.1 Suite Unitária e Integração Limitada
A execução da base purista (exclui o browser Chrome do Playwright) utiliza as diretivas parametrizadas do root:
```bash
# Na raiz do seu repositório ativo
python -m pytest tests/unit/ tests/integration/ -v --tb=short
```

### 3.2 Execução Singular Debug (Log Verbose)
Quando a engenharia foca estritamente na resolução de um nó do módulo de Ingestão:
```bash
python -m pytest tests/unit/test_ingestion_logic.py -s -v --log-cli-level=DEBUG
```

### 3.3 Relatórios de Cobertura Sistêmica
Para avaliar os gaps e cegueiras na base de código RAG atrelado via `pytest-cov`:
```bash
python -m pytest --cov=src --cov-report=term-missing tests/unit/
```

---

**Glossário Técnico Referenciado:** Vide `docs/glossary.pt-BR.md`.
