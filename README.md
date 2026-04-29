# Sovereign Pair v1.3.2 (The Multi-Arch Core)

Sovereign Pair e um sistema de Retrieval-Augmented Generation (RAG) com arquitetura desacoplada, projetado com foco em alta performance, privacidade de dados e seguranca Zero-Trust. O sistema suporta a execucao de modelos de linguagem localmente (via Ollama) ou por meio de provedores em nuvem, sendo orquestrado por um binario nativo em Rust que embute a interface SvelteKit.

Esta versão **v1.3.2** introduz suporte oficial para **macOS Intel (x86_64)**, unifica o gerenciamento de credenciais no **SecOps Vault** e aprimora drasticamente o suporte a modelos da série **Qwen 3.5** e **Phi-4**.

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
   - **Multi-Arch Native Support**: Binários otimizados para Apple Silicon (arm64) e Intel (x64), garantindo performance máxima em qualquer Mac.
   - **Cross-Encoder Local (FastEmbed)**: O processamento vetorial baseia-se na poda massiva de lixo da Web via *BGE-Reranker-Base* rodando lado-a-lado no Kernel do processo e devolvendo unicamente Top-Chunks. 
   - **Epistemic Guard v2 (Deterministic SHA-256)**: O sistema de verificacao de proveniencia criptografica opera de forma **deterministicamente** pelo Motor Rust, re-hasheando arquivos fisicos em `/tmp/sovereign/` e comparando 1:1 com checksums originais. 
   - **TurboQuantMSE (Vector Quantization)**: Implementação nativa sob o Kernel Rust que compacta tensores (Embeddings) baseando-se em dicionários Lloyd-max de 4-bits. 
   - **Sovereign Resilience Shield**: Trabalhadores Python são encapsulados em tolerância a falhas utilizando roteamento dinâmico *Exponential Backoff*.
   - **Deep Research Pipeline (Model-Agnostic)**: Motor de Pesquisa Profunda orquestrado via *Agentic Loop* com Tool Calling nativo, fusao de series temporais via Pandas, e cadeia de formatacao Scribe→Auditor.

4. Dashboard Web (Svelte 5)
   - Interface Web (PWA) de painel unico que centraliza logs do sistema, monitoramento de recursos (RAM/VRAM) e navegacao interativa e controlada do repositorio fisico de documentos. 
   - Arquitetura Zero-VDOM baseada em Runes, embutida diretamente no binario Rust para entrega sem dependencias externas.

5. Arquitetura Distribuida P2P (Sovereign Mesh)
   - Nos locais sincronizam dados par-a-par atraves de tuneis SSH dinamicos. A engine garante transmissividade de metadados, configuracoes de usuario (.cybrid) e vetores de embeddings em topologias distribuidas.

## Instalacao

Consulte o documento de [Guia de Instalacao](docs/install_guide.md) para instrucoes detalhadas de execucao do binario pre-compilado em ambientes Windows, Linux ou MacOS.

## Licenciamento de Software

O codigo fonte restritivo encontra-se sob regimento validado da PolyForm Noncommercial License 1.0.0.

- Limites de Aplicacao Nao Comercial: De uso garantidamente liberado sem pagamento para finalidades particulares, estudo algoritmico academico, sem fins lucrativos ou topologia de laboratorios domesticos (HomeLabs isolados).
- Implementacao Comercial Restrita: Nulamente permitido derivar o core vetorial e seu back-end, criar wrappers sob o fluxo, ou encapsular e alienar solucoes pagas originarias ou parciais desta base.

Para alinhamentos voltados a implantacoes empresariais de software robusto, acione corporativamente via: jefersonlopes@proton.me.
