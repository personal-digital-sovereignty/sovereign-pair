# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [4.0.0] - 2026-03-14

### 🦀 Major Release - The Rust Paradigm Shift & OCI Cibrid Architecture

Esta versão marca a maior transição arquitetural do Sovereign Pair, expurgando as limitações do framework original em Python e abraçando a extrema soberania e performance da linguagem Rust. A mudança não se escora apenas em performance, mas na nossa descoberta de vazamentos silenciosos de telemetria ("Data Leaks") e fallback para conectores OpenAI presentes nas profundezas do código do LlamaIndex, contrariando filosoficamente nosso manifesto "Sovereignty First".

### Adicionado
- **Native Rust Engine (Axum)**: Desenvolvemos do zero o nosso próprio motor preditivo e indexador vetorial em Rust. Abandonamos o LlamaIndex (Python) para reconquistar controle absoluto sobre a malha de dados, mitigando dependências inseguras e black-boxes que feriam o rigor da privacidade.
- **Oracle BYOC (Bring Your Own Compute)**: Nova documentação e script (`manual_cloud_init.sh`) homologando totalmente a arquitetura de nó remoto na Oracle Cloud. O Hub Lógico distribui inferências complexas (Qwen/Llama 3.2) para instâncias ARM remotas (A1 OCI) via malha VPN Mesh Tailscale.
- **Global Workspace Architecture**: O novo motor Cíbrido agora varre diretórios arbitrários (multi-tenant) no nível de Sistema Operacional em vez de apenas um "Vault" singular, orquestrando dezenas de pastas com concorrência limpa em Rust.
- **Standalone Containerized AI**: Refatoramos o modelo de proxy da UI para internalizar integralmente o daemon do Ollama dentro de clusters fechados estruturais no Docker Compose (`infra/docker`), sepultando o acoplamento do sistema hospedeiro.

### Modificado
- **Clean Root & Docker Isolation**: Remoção massiva de poluição do ambiente na raiz. Os arquivos de orquestração `.yml`, `Nginx` e `Caddy` ganharam sub-espaços na pasta `/infra/docker/`. 
- **Modernização Absoluta da Web-UI**: Refatoração brutal dos painéis frontais geométricos (Vue 3 + Vite). Centralização end-to-end do layout Kanban e estabilização gráfica das dependências assíncronas SVG dos ícones (Phosphor bugs resolvidos).
- **Telemetry Mesh Hub**: Adição nativa do painel de telemetria em tempo real para escutar assincronamente o streaming P2P RPC e as requisições ativas.

### Segurança (Security)
- **Intercepção Definitiva de Leak**: Eliminação do RAG Python original blindou o vazamento acidental (via LlamaIndex) garantindo que tokens da infra corporativa não pinguem na web civil americana.
- **Hardening OCI Docker Unix Socket**: Adição de fix de permissionamento de soquetes daemon (`chmod/gpasswd`) aos compêndios corporativos (`10_guide_byoc_oracle_cloud.pt-BR.md`), blindando falhas nas pipelines não-privilegiadas.

---

## [3.1.2] - 2026-03-08

### 🤖 The Coder & OpenCode Integration (Pair Programming)

### Adicionado
- **OpenAI-Compatible Proxy API**: Construção de um endpoint dedicado (`/v1/opencode/chat/completions`) isolado do middleware de autenticação transacional para suportar nativamente plugins e IDEs como OpenCode/Cursor.
- **Oracle OCI Bypass (The Coder)**: Adicionado roteamento dinâmico inteligente no `engine_builder.py`. Quando models nomeados como `coder` são requisitados pela IDE, o proxy descarta o Ollama local e transparente injeta o modelo pesado `qwen2.5-coder:7b` conectando via tunelamento mTLS Tailscale diretamente ao nó isolado The Coder na Oracle Cloud.
- **Server-Sent Events (SSE)**: Pleno suporte ao stream token a token em requisições assíncronas assincronamente da Oracle para a interface do editor local, reduzindo a sensação de latência de cold start.

### 🕸️ Arquitetura de Rede & Resolvibilidade VPN Isolada

### Corrigido
- **Tailscale Sidecar Collision**: Renomeado o container VPN interno (`sovereign-tailscale`) de `sovereign-rag-cloud` para `sovereign-cloud-api` no `docker-compose.yml`. Isso mitigou uma colisão severa na malha que gerava a dupla recusa de pacotes (`Connection Refused`) e o engasgo subjacente por sinkholes de DNS locais (como Pi-Hole e NextDNS retornando `Great, localhost is not blocked anymore`).
- **IPv6 Blackholing na OCI**: Injetado bloqueio mandatário das rotas IPv6 diretamente no Kernel (via `sysctl`) dentro do `cloud-init.yaml`. Isso previne definitivamente as travas de "network is unreachable" desencadeadas quando a Docker Engine tenta dar poll do registro de imagens em subredes dual-stack nuas da Oracle.
- **Docker Mount Permissions**: Remediado o *Crash Loop* na subida inaugural da `sovereign-api` originada pelos privilégios restritos do volume bindado assincronamente `/app/data/raw_docs`.

---

## [3.1.1] - 2026-03-07

### 🌐 Resiliência Local-First & Infraestrutura Cibrid Automática

### Adicionado
- **Restricted Mode (Degradação Graciosa)**: Implementação de fallback inteligente no backend FastAPI. Quando o *The Doctor* (Oracle) ou o webhook N8N perdem conectividade, a pipeline de RAG desvia graciosamente a inferência para a *The Nurse* (SLM Local), evitando Timeouts na interface e reportando o status local via o novo endpoint `/health/cluster` (`degraded`).
- **Toggle Remoto Dinâmico**: Adicionado controlador lógico de bypass remoto (`POST /settings/remote-toggle`) mitigando no código-fonte a dependência forçada de rede com a núvem (OCI).

### Corrigido
- **Docker Mount Point Crítico**: Sanado o crash-loop (Read-Only Filesystem) que abatia o ChromaDB devido à flag rígida de segurança `read_only: true`. Roteamento mapeado do volume para `/data`.

### Infraestrutura & DevSecOps
- **Pipeline Segura contra Injeção (Semgrep SAST)**: Erradicada falha pontiaguda de *Shell Injection* na action de Deploy OCI (`deploy-oci.yml`), repassando o event bus do GitHub com segurança por contexto em bash env.
- **Automação OCI e Cloud-Init**:
  - Extirpado o hostname default confuso `primaryvnic` mapeando assincronamente a label nativa de VNIC `sovereign-coder` da Terraform.
  - Abordado falha silenciosa do daemon instalador da Docker (`Failure writing output to destination`) no bootstrap inicial via piping ramificado (`curl | sh`).
- **Zizmor Audit & Ruff Compliance**: Varredura limpando formatação quebrada obsoleto da codificação py (strings F vazias). Inseridos rótulos seletivos da ferramenta de inspeção Zizmor no release do Sensus Vault.

## [3.1.0] - 2026-02-27

### 🛡️ DevSecOps & Security Hardening (FOSS Enterprise)

### Segurança
- **Esteira DevSecOps (Gate 0 a 4)**: Implementação e fixação de pipeline estrito no GitHub Actions (`devsecops.yml`) validando integridade com `Actionlint`, `Zizmor`, `Gitleaks`, `Semgrep`, `Trivy` e `Ruff`.
- **Zero-Warning SAST Compliance**:
  - Eliminação de vulnerabilidades XSS no frontend Vue utilizando sanitização via `DOMPurify` e encapsulamento em diretiva customizada `v-safe-html`.
  - Correção de injeção DOM-XSS crítica no Sensus Vault Plugin, migrando de `innerHTML` para construção segura DOM (`setText()`, `createEl()`).
- **Hardening de Infraestrutura Docker**:
  - Aplicação de RootFS imutável (`read_only: true`) em todos os containers, com montagens seguras voláteis (`tmpfs`) no Caddy, PostgreSQL, ChromaDB e Tailscale.
  - Mitigação de escape de containers negando escalação em executáveis `setuid/setgid` (`no-new-privileges:true`).
- **Sanitização de Dívida Técnica (SCA/Lint)**:
  - Resolução da vulnerabilidade `CVE-2026-25990` com atualização forçada da dependência `pillow` v12.1.1 (apontada pelo Trivy).
  - Conformidade restrita `PEP-8` na engine backend (`Ruff`), ajustando ordem de execução e imports ociosos sem quebrar inicializadores nativos.
  - Eliminação de Token JWT transacional de testes listado nos rastros do `Gitleaks`.

## [3.0.0] - 2026-02-26

### 🚀 Major Release - UX Revolucionária, Concorrência e Integração Sensus Vault 3.0

### Adicionado
- **Arquitetura de Pastas (Chat Folders)**: Hierarquia nativa de diretórios para as sessões de RAG. Criação, renomeio e deleção dinâmica via Web UI e API (`PATCH/DELETE v1/sessions`).
- **Sovereign Profile Injection**: Novo sistema de injeção biográfica. Acesso e persistência profunda de `OWNER_NICKNAME`, `LANGUAGE`, `GEOLOCATION`, `OCCUPATION` e `ABOUT_USER` nos prompts do sistema e na memória da IA (`v1/settings`).
- **Terminal Rápido (CLI Chat)**: Comando exclusivo `python src/cli.py chat` que inicia o modo Reativo do Terminal, dispensando a necessidade de iniciar o FastAPI para conversas secas com o RAG e a Web.
- **Wizard Setup Interativo**: Comando `python src/cli.py setup` completamente redesenhado para guiar o acolhimento do usuário e criar o `sovereign.conf`.
- **App Vue3 Modernizado**: Web UI reconstruída com suporte responsivo a `Dark Mode / Light Mode`, Barra Lateral Redimensionável (persistente via Session Storage) e design Cyber-Minimalista polido.
- **Avatar Dinâmico da IA**: Nova direção de arte substituindo emojis por Avatares Vetoriais generativos e ícones customizados no fluxo da conversa.

### Integração Sensus Vault (3.0)
- **Três Perfis de Visualização Inéditos**:
  - `Mini-Web`: Experiência rica 1:1 renderizada idêntica à janela do Web UI moderno na barra direita.
  - `Minimalist Chat`: Chat enxuto e estrito focando na densidade do texto.
  - `Spotlight Modal`: Novo pop-up gigante central imersivo para invocar o RAG diretamente sob os holofotes do fluxo de pensamento.

### Otimizado e Alta Performance
- **Asynchronous LLM Processing (Concurrency)**: Remoção das amarras `asyncio.to_thread`. Refatoração maciça na API `/v1/chat` e Web-Search em FastAPI migrando para o paradigma de *Corroutines Mistas Nativas* do LlamaIndex (`astream_chat` e `achat`), habilitando *High-Throughput e Max-Concurrency* via conexões simultâneas do Uvicorn e batidas diretas no Ollama.

---

## [2.2.0] - 2026-02-24

###  Major Release - Backend API, Citações e Modularidade

### Adicionado
- **Provedores LLM Modulares**: Refatoração profunda no núcleo (`config.py` e `llm_factory.py`) para permitir plugar facilmente `openai`, `anthropic`, `groq`, `gemini`, mantendo o `ollama` como a escolha local padrão e blindando a soberania digital.
- **FastAPI e Server-Sent Events (SSE)**: Desacoplamento do motor LlamaIndex do CLI. Adicionados endpoints RESTful em `src/api` rodando em portas dedicadas (`uvicorn`) com streaming de respostas em tempo real para conectar frontends (Chat UIs, Sensus Vault, WhatsApp).
- **Extração Formal de Citações e Fontes**: O RAG agora retorna proativamente ao usuário os arquivos locais ` caminho/do/arquivo.md` ou URLs ` url` usados na inferência, inserindo-os no final de cada streaming.
- **Auto-pull Inteligente do Ollama**: O CLI deteta a falta de modelos vitais no Ollama e proativamente força o download transparente ao invés de abortar o terminal secamente.
- **Tipagem Forte e Testes Modernos**: Atualização completa na validação da base convertendo testes estáticos ao ecossistema `pytest`, utilizando `fixtures` puras e o isolamento seguro vía `pytest-mock` e `MagicMock`, blindando regressões na pipeline de ingestão.
- **Compatibilidade do Ambiente**: Reconfigurado o ambiente local de testes do ChromaDB para rodar suave e estavelmente apenas com versões do Python `3.12` a `3.13`, contornando problemas no ecossistema `Pydantic V1`.

---

## [2.1.0] - 2026-02-17

### Adicionado
- **Busca Híbrida (Hybrid Search)**: Implementação de recuperação combinada usando `Vector Store` (ChromaDB) e `BM25` (rank-bm25).
- **Recuperação de Datas e Termos Exatos**: O agente agora encontra documentos por datas específicas (ex: "18/10/2007") e palavras-chave que a busca semântica perdia.
- **Carregamento Robusto**: Fallback para carregar documentos diretamente do ChromaDB se o docstore local estiver vazio.
- **Streaming de Respostas**: Respostas são exibidas token a token (streaming), eliminando a percepção de travamento em modelos locais lentos.

### Corrigido
- **Bug de Inicialização**: Correção na carga de nós para o índice BM25 quando o sistema reinicia.
- **Timeout em Respostas Longas**: `REQUEST_TIMEOUT` aumentado de 120s para 300s no `.env` para modelos locais CPU-bound.

### Otimizado
- **Top-K Conservador**: Redução do Top-K de fusão (15→3) e dos retrievers individuais (20→5) para diminuir drasticamente o tempo de processamento do LLM local, eliminando timeouts.

---

## [2.0.0] - 2026-02-16

###  Major Release - MVP Completo com Otimizações

**Commit**: `81406a3`

### Added
- **Fase 3**: Refatoração 100% incremental
  - `ingest_data()` aceita documentos opcionais
  - Modo incremental não recarrega arquivos desnecessariamente
- **Fase 4**: Testes end-to-end completos
  - `tests/manual_e2e_tests.md` - Guia com 5 cenários
  - `tests/validate_state.py` - Validação automática
  - `tests/README.md` - Documentação de testes
- **Fase 5.1**: Otimizações de performance
  - `hash_utils.py` v2.0 com paralelização (ThreadPoolExecutor)
  - Cache LRU de hashes (functools.lru_cache)
  - `ux.py` - Logs coloridos (colorama)
  - Barras de progresso (tqdm)
  - Estatísticas detalhadas de processamento
- **Fase 5.2**: Documentação completa
  - `docs/USER_GUIDE.md` (366 linhas)
  - `docs/API.md` (503 linhas)
  - `docs/FAQ.md` (434 linhas)
  - `README.md` atualizado e completo

### Changed
- `ingest_data()` refatorado para aceitar `documents: Optional[list]`
- `diff.py` usa `compute_hashes_parallel()` para detecção mais rápida
- `hash_utils.py` completamente reescrito (v2.0)

### Performance
-  **95%+ mais rápido** em modo incremental vs full
-  **3-4x mais rápido** no cálculo de hashes (paralelização)
-  Cache LRU reduz recálculo desnecessário
-  Estatísticas detalhadas de performance

### Documentation
-  **1303 linhas** de documentação nova
-  Guia do usuário completo
-  API documentada
-  FAQ abrangente

---

## [1.1.0] - 2026-02-16

###  Minor Release - Ingestão Incremental (Fases 1 e 2)

**Commits**: `5d9435c` até `f9dd82e`

### Added
- **Fase 1**: Detecção de novos arquivos
  - `history.py` - Gerenciamento de histórico de ingestão
  - `diff.py` - Detecção de mudanças
  - Integração com `ingest.py`
- **Fase 2**: Detecção completa + limpeza
  - `hash_utils.py` - Cálculo de hashes SHA256
  - Histórico v1.1 com campo `content_hash`
  - Detecção de arquivos modificados (via hash)
  - Detecção de arquivos deletados
  - `cleanup.py` - Limpeza automática de chunks obsoletos
  - `interactive.py` - Interface interativa (full/incremental/skip/cancel)

### Changed
- Histórico migrado de v1.0 para v1.1 (adição de `content_hash`)
- `ingest.py` integrado com sistema incremental

### Performance
-  Processa apenas arquivos novos ou modificados
-  Limpeza automática de chunks obsoletos
-  Detecção precisa via hash SHA256

---

## [1.0.0] - 2026-02-16

###  Major Release - Primeira Versão Estável

**Commit**: `9d64dbf`

### Added
- Sistema RAG básico funcional
- Ingestão de documentos (PDF, Markdown, DOCX, CSV, etc.)
- Busca vetorial com ChromaDB
- Agente ReAct com ferramentas
- Configuração via `.env`
- Tratamento robusto de erros
- Logging estruturado

### Changed
- `src/agent.py` - Melhorias significativas (+314 linhas)
- `src/config.py` - Configuração robusta (+191 linhas)
- `src/ingest.py` - Ingestão otimizada (+175 linhas)

### Fixed
- Diversos tratamentos de erros
- Validações de configuração
- Robustez geral do sistema

---

## Tipos de Mudanças

- `Added` - Novas funcionalidades
- `Changed` - Mudanças em funcionalidades existentes
- `Deprecated` - Funcionalidades que serão removidas
- `Removed` - Funcionalidades removidas
- `Fixed` - Correções de bugs
- `Security` - Correções de vulnerabilidades
- `Performance` - Melhorias de performance
- `Documentation` - Mudanças na documentação

---

## Links

| Version | URL |
|---------|-----|
| [2.0.0](https://github.com/Personal-Digital-Sovereignty/sovereign-pair/commit/2d97e65) | https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/tag/v2.0.0 |
| [1.1.0](https://github.com/Personal-Digital-Sovereignty/sovereign-pair/commit/8a3046d) | https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/tag/v1.1.0 |
| [1.0.0](https://github.com/Personal-Digital-Sovereignty/sovereign-pair/commit/9d64dbf) | https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/tag/v1.0.0 |

---

**Autor**: Jeferson Lopes
**Assistência**: Antigravity (Advanced Agentic Coding) & Deepmind Systems
**Data**: 2026-03-14
**Versão**: 4.0.0
