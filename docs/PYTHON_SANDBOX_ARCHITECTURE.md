# Sovereign Python Sandbox — Zero-Dependency Self-Provisioning Architecture

> **Epic:** Sovereign Sandbox Self-Provisioning (v1.2.11)  
> **Author:** Jeferson Lopes  
> **Date:** 2026-04-18  
> **Status:** ✅ Implemented

## 1. Motivação

O Sovereign Pair foi projetado como um aplicativo **100% autocontido e soberano** — sem dependências externas obrigatórias para funcionar. No entanto, até a v1.2.10, o pipeline de Deep Research (tools: `fetch_financial_ticker`, `fetch_macroeconomy`, `execute_python_code`) dependia de um Python **pré-instalado no sistema operacional** para:

1. Criar um `venv` hermético na primeira execução
2. Executar workers Python (yfinance, Pandas, DuckDB, etc.)

Em um **Mac novo sem Xcode CLI Tools ou Homebrew**, nenhum Python está disponível. Resultado: `System execution error: No such file or directory (os error 2)` — e **todo o pipeline de pesquisa morre silenciosamente**.

## 2. Solução: Auto-Provisioning via python-build-standalone

### O que é python-build-standalone?

O projeto [python-build-standalone](https://github.com/astral-sh/python-build-standalone) (mantido pela [Astral](https://astral.sh), criadores do `uv` e `rye`) fornece **distribuições CPython pré-compiladas e autocontidas** para todos os OS/arch principais. São builds oficiais, reproduzíveis, e não dependem de nenhuma biblioteca do sistema.

- **Tamanho:** ~24MB comprimido (stripped)
- **Plataformas:** macOS ARM/Intel, Linux x86_64/aarch64, Windows x86_64
- **Licença:** PSF (Python Software Foundation) — totalmente FOSS

### Fluxo de Provisioning

```
┌──────────────────────────────────────────────────────────┐
│                  setup_python_sandbox()                   │
│                    (sandbox.rs — Boot)                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Venv já existe?                                      │
│     └─ SIM → return true (hot path, ~0ms)                │
│                                                          │
│  2. Python no sistema? (find_system_python)               │
│     ├─ Caminhos absolutos conhecidos:                    │
│     │   macOS: /opt/homebrew/bin/python3                  │
│     │          /usr/local/bin/python3                     │
│     │          /Library/Frameworks/.../python3            │
│     │          /usr/bin/python3                           │
│     │   Linux: /usr/bin/python3, /usr/local/bin/python3   │
│     │   Win:   C:\Python312\python.exe, etc.             │
│     └─ `which python3` / `where python`                  │
│     └─ SIM → usa para criar venv                         │
│                                                          │
│  3. Python standalone já baixado?                        │
│     └─ SIM → usa para criar venv                         │
│                                                          │
│  4. Auto-download (provision_standalone_python)           │
│     ├─ Detecta OS + arch (cfg! compile-time)             │
│     ├─ Monta URL: github.com/astral-sh/python-build-     │
│     │   standalone/releases/.../cpython-3.12.13+...      │
│     │   ...-install_only_stripped.tar.gz (~24MB)          │
│     ├─ Download via reqwest (timeout 5min)               │
│     ├─ Extrai via `tar -xzf` nativo                     │
│     └─ Resultado: ~/Library/Application Support/         │
│         sovereign-pair/sandbox/python/bin/python3         │
│                                                          │
│  5. Criar venv com o Python encontrado/baixado            │
│     ├─ python3 -m venv sandbox/venv/                     │
│     └─ Fallback: --without-pip + ensurepip               │
│                                                          │
│  6. Instalar pacotes analíticos                          │
│     └─ pip install pandas numpy yfinance requests         │
│        duckduckgo-search duckdb                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## 3. Estrutura no Disco

```
~/Library/Application Support/sovereign-pair/sandbox/
├── python/                  ← CPython standalone (auto-baixado)
│   ├── bin/
│   │   ├── python3          ← Binário principal
│   │   └── pip3
│   ├── lib/
│   │   └── python3.12/      ← stdlib completa
│   └── include/
├── venv/                    ← Venv hermético (criado a partir do standalone)
│   ├── bin/
│   │   ├── python3          ← Symlink para o standalone
│   │   └── pip
│   └── lib/
│       └── python3.12/
│           └── site-packages/
│               ├── pandas/
│               ├── numpy/
│               ├── yfinance/
│               └── ...
└── cpython-standalone.tar.gz ← Apagado após extração
```

## 4. Cadeia de Resolução do Python (`resolve_venv_python`)

O módulo `api_trainer.rs` usa a seguinte cadeia para encontrar o Python em tempo de execução (tool calling):

| Prioridade | Fonte | Quando |
|---|---|---|
| 1 | Venv Hermético (`sandbox/venv/bin/python3`) | Sempre (se existir) |
| 2 | Caminhos absolutos do sistema | macOS Homebrew, Xcode CLT, APT |
| 3 | `which python3` / `where python` | PATH do shell pai |
| 3.5 | Standalone root (`sandbox/python/bin/python3`) | Auto-provisionado |
| 4 | Bare `python3` (último recurso) | + `tracing::error!` acionável |

## 5. Ticker Resolver Dinâmico (`sovereign_matrix.py`)

O mapeamento de tickers no `sovereign_matrix.py` foi expandido de um dicionário hardcoded de ~8 entradas para **30+ mapeamentos de ativos brasileiros** com fallback dinâmico:

### Fase 1: Mapeamento Semântico Estático
Cobre nomes populares → tickers Yahoo Finance:

| Input do LLM | Ticker Resolvido | Descrição |
|---|---|---|
| `NUBANK`, `NU` | `NU` (NYSE) | Ações NuBank |
| `BRADESCO` | `BBDC4.SA` | Bradesco PN |
| `PETROBRAS` | `PETR4.SA` | Petrobras PN |
| `VALE`, `VALE3` | `VALE3.SA` | Vale ON |
| `ITAU`, `ITAÚ` | `ITUB4.SA` | Itaú Unibanco |
| `BB`, `BANCO_DO_BRASIL` | `BBAS3.SA` | Banco do Brasil |
| `WEG`, `MAGALU`, `JBS`, ... | Respectivos `.SA` | Top 20+ B3 |
| `BRENT`, `WTI`, `GOLD` | Futuros (BZ=F, CL=F, GC=F) | Commodities |
| `DOLAR`, `USD` | `BRL=X` | Câmbio USD/BRL |

### Fase 2: Fallback Dinâmico
Se o ticker não está no mapa estático:
1. Tenta `{TICKER}.SA` (B3) via `yfinance.Ticker().history(period="5d")`
2. Tenta `{TICKER}` puro (NYSE/NASDAQ)
3. Se ambos falharem → erro com mensagem acionável

## 6. Prevenção de Prompt Poisoning (`registry.json`)

As descrições das tools `fetch_financial_ticker` e `fetch_macroeconomy` foram re-escritas para:
- **Remover** exemplos hardcoded mencionando PETROBRAS/DOLAR que causavam associação semântica parasítica
- **Ensinar** ao LLM que o motor resolve nomes populares automaticamente
- **Limitar** a regra de DOLAR a contextos onde o ativo é cotado em USD (sem forçar inclusão obrigatória)

## 7. Referências

- [python-build-standalone](https://github.com/astral-sh/python-build-standalone) — Astral (Gregory Szorc)
- [PEP 711 — PyBI (Python Binary Interface)](https://peps.python.org/pep-0711/) — Proposta para padronização de distribuições Python standalone
- Sovereign Pair v1.2.10 Stress Test — Case study documentando as falhas corrigidas
