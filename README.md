# Sovereign Pair

Sovereign Pair e um sistema de Retrieval-Augmented Generation (RAG) com arquitetura desacoplada, projetado com foco em alta performance, privacidade de dados e seguranca Zero-Trust. O sistema suporta a execucao de modelos de linguagem localmente (via Ollama) ou por meio de provedores em nuvem, sendo orquestrado por um binario nativo em Rust que embute a interface SvelteKit.

## Visao Geral da Arquitetura

O sistema opera com base nos seguintes componentes principais:

1. Inferencia Local e Reflexiva (LLM)
   - Execucao local offline utilizando Ollama para gerenciamento de contexto alocado em VRAM.
   - Pipeline RAG implementada nativamente via motor Axum Local, permitindo iteracoes reflexivas e autocorrecao durante a inferencia.

2. Persistencia de Dados (SQLite)
   - O banco de dados vetorial legado foi substituido de forma a priorizar velocidade transacional O.S.
   - sovereign_memory.db: Banco associado e integrado via sqlite-vec ao Rust configurado com journal_mode=WAL, responsavel por gerenciar o historico de conversas, quadros Kanban e embeddings vetoriais de forma integrada.

3. Backend Master Engine (Rust Axum & Tokio)
   - Motor principal construido integralmente em Rust de ponta a ponta (Axum + Tokio), desenhado para I/O extremo e baixissima latencia.
   - **Enterprise RAG e Agentic Search Loop**: As pesquisas web agora sao dotadas de Lógica Soberana de Tool-Calling e *CDX Fallback Chain* descentralizada. 
   - **Cross-Encoder Local (FastEmbed)**: O processamento vetorial baseia-se na poda massiva de lixo da Web via *BGE-Reranker-Base* rodando lado-a-lado no Kernel do processo e devolvendo unicamente Top-Chunks. 
     - ⚠️ **Nota Importante:** Ao invés de trafegar tensores em VRAM, a infraestrutura FastEmbed nativa puxa autonomamente o Reranker da web (.ONNX) para cache físico da CPU no seu primeiro Boot. **NENHUM modelo do tipo `bge-reranker` deve ser instalado via Ollama**, evite poluir sua instalação Ollama.
   - **Epistemic Guard v2 (Deterministic SHA-256)**: O sistema de verificacao de proveniencia criptografica opera de forma **deterministicamente** pelo Motor Rust, re-hasheando arquivos fisicos em `/tmp/sovereign/` e comparando 1:1 com checksums originais. Nenhuma dependencia cognitiva do LLM para reproducao de hashes.
   - **TurboQuantMSE (Vector Quantization)**: Implementação nativa sob o Kernel Rust que compacta tensores (Embeddings) baseando-se em dicionários Lloyd-max de 4-bits. Corta em 10.6x o rastro de memória (Footprint) nas varreduras semânticas dentro do SQLite local.
   - **Sovereign Resilience Shield**: Trabalhadores Python são encapsulados em tolerância a falhas utilizando roteamento dinâmico *Exponential Backoff*, tornando o sistema resistente contra limites ou quedas instáveis de APIs de nuvem (Yfinance, Brapi, Banco Central).
   - **Deep Research Pipeline (Model-Agnostic)**: Motor de Pesquisa Profunda orquestrado via *Agentic Loop* com Tool Calling nativo, fusao de series temporais via Pandas (Pearson correlation matrix 6×6), e cadeia de formatacao Scribe→Auditor com *Sycophancy Breaker* cross-family. Validado em stress tests com modelos de 8B a 14B produzindo dados **bitwise identicos** (SHA-256). Detalhes em [`docs/case_study_v1.2_deep_research_stress_test.md`](docs/case_study_v1.2_deep_research_stress_test.md) e [`docs/reports/_strategy/deep_research_scribe_hardening_v1.2.7.md`](docs/reports/_strategy/deep_research_scribe_hardening_v1.2.7.md).

4. Dashboard Web (Svelte 5)
   - Interface Web (PWA) de painel unico que centraliza logs do sistema, monitoramento de recursos (RAM/VRAM) e navegacao interativa e controlada do repositorio fisico de documentos. 
   - Arquitetura Zero-VDOM baseada em Runes, embutida diretamente no binario Rust para entrega sem dependencias externas.

5. Arquitetura Distribuida P2P (Sovereign Mesh)
   - Nos locais sincronizam dados par-a-par atraves de tuneis SSH dinamicos. A engine garante transmissividade de metadados, configuracoes de usuario (.cybrid) e vetores de embeddings em topologias distribuidas.

## Padrão Arquitetural: Monorepo Híbrido

O Sovereign Pair não é um monolito estrito, mas sim um **Monorepo Híbrido** com uma arquitetura de microsserviços fortemente acoplados de forma lógica, mas desacoplados fisicamente. Do ponto de vista arquitetônico:

- **Monorepo (Repositório Único)**: Todo o ecossistema habita no mesmo repositório do Git para garantir consistência de versão e facilidade na sincronia de código. Isso inclui o backend Rust (`/core`), o frontend Desktop (`/svelte-ui`), infraestrutura (`/infra`) e os workers autônomos.
- **Microsserviços e Sidecars (Não Monolítico)**: 
  - O aplicativo nativo de mesa (Tauri) compila um cliente visual hermético (Svelte). 
  - O Rust (`core`) pode ser iniciado independente da interface gráfica como um servidor puro de API rodando na porta `38001`. Em nuvem (Cloud), instala-se apenas o `/core`.
  - Para usuários Desktop operando localmente, o processo principal (Svelte/Tauri) invoca invisivelmente o backend ativando-o como um sidecar integrado em segundo plano.
- **Fator "Sandboxed" Externo (Workers Desacoplados)**: A lógica pesada do pipeline financeiro e de pesquisa não está compilada diretamente na biblioteca estrita do Rust. O `core` comanda um exército externo de binários e scripts em uma Sandbox Python auto providenciada e lançando-os em processos isolados. Em falhas por estouro de memória ou crashes, apenas o processo instanciado (Worker/Python) falha, protegendo a interface e o Processo Mestre. A soberania continua ativa.

## Instalacao

Consulte o documento de [Guia de Instalacao](docs/install_guide.md) para instrucoes detalhadas de execucao do binario pre-compilado em ambientes Windows, Linux ou MacOS.

## Roadmap Técnico

Para acompanhar a evolução do projeto e as próximas grandes funcionalidades planejadas (como integrações com OpenRouter, Alibaba e NVIDIA, além do novo Ecossistema Coder), consulte o nosso [ROADMAP.md](ROADMAP.md).

## Mapas Arquiteturais dos Repositorios

- core/ - Contratos tecnicos de processamento modular Rust e Retriever Vetorial O.S.
- svelte-ui/ - Camada Svelte 5 para visualizacoes gerenciais.
- docs/ - Acondiciona manifestos tecnicos da construcao da aplicacao.
- _strategy/ - Artigos tecnicos internos, case studies e analises arquiteturais.
- infra/ - Assets Terraform e shell-scripts cloud-inits.

---

## Licenciamento de Software

O codigo fonte restritivo encontra-se sob regimento validado da PolyForm Noncommercial License 1.0.0.

- Limites de Aplicacao Nao Comercial: De uso garantidamente liberado sem pagamento para finalidades particulares, estudo algoritmico academico, sem fins lucrativos ou topologia de laboratorios domesticos (HomeLabs isolados). O codigo e os seus dados processados localmente mantem-se protegidos de invasao corporativa.
- Implementacao Comercial Restrita: Nulamente permitido derivar o core vetorial e seu back-end, criar wrappers sob o fluxo, ou encapsular e alienar solucoes pagas originarias ou parciais desta base para clientes B2C/B2B sem que obtenha-se documentada e assinada a vertente comercial de uma Autorizacao Proprietaria do titular.

Para alinhamentos voltados a implantacoes empresariais de software robusto, acione corporativamente via: jefersonlopes@proton.me.
