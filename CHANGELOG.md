# Changelog

All notable changes to the Sovereign Pair project will be documented in this file.

> **⚠️ NOTA HISTÓRICA DE REGRESSÃO SEMÂNTICA (Semantic Versioning Collapse):**
> Durante os primeiros ciclos ágeis deste projeto, o versionamento foi inflacionado inadvertidamente a saltos drásticos (registrando passagens como `v2.2.0`, `v3.0.0` e `v4.0.0` no histórico fossilizado de commits e merges). Contudo, após uma avaliação sincera sobre a maturidade do código, a complexa reformulação arquitetural (do LlamaIndex/Python puro para o Motor Híbrido em Rust/Svelte) e as diretrizes FOSS, **decidimos regredir cirurgicamente toda a árvore hierárquica para a série de pré-lançamento estrita `0.x.x`**. A série 1.0.0 será ativada unicamente quando o núcleo do ecossistema Sovereign Bare Main atingir maturidade e estabilidade arquitetural plenas.

## [0.9.9] - 2026-04-01

### 🚀 Sovereign Multimodal Hybrid Architecture
- **Ultra-lightweight Python Nodes**: Pivotamos a arquitetura de processamento visual e auditivo para fora da monolitização pesada em C++. Criamos e isolamos micro-scripts em Python estrito (`audio_transcriber.py`, `vision_ocr.py`, `midi_transcriber.py`) para operar como nós independentes de Sistema Operacional invocados silenciosamente via IPC sub-processos.
- **Svelte Native Microphone (ASR)**: Desenvolvido o componente UI `MicrophoneButton.svelte` alocado estrategicamente na `textarea` principal do Chat. Ao alcance de um toque, ele instiga a API `MediaRecorder` do navegador, captura blob arrays compactos em `audio/webm` e dispara transparentemente para a porta HTTP local do Rust.
- **Axum Multipart Gateway**: O backend em Rust foi expandido estruturalmente. Criamos o `api_multimodal.rs` equipado para devorar uploads de dados corrompidos (Multipart), salvá-los volatilmente no SO temp-dir, extrair o texto instanciando dinamicamente o *faster-whisper* da CPU Local, e entregar a transcrição cirúrgica direto na input do usuário via Svelte Event Dispatchers.
- **Zero-Bindgen Constraint**: Foram debelados os fantasmas mortíferos de compilação do Rust com o Clang 22. Removemos imperativamente a macro `whisper-rs`. O Sovereign Pair consolida sua tese Cíbrida: O Rust gerencia inteligentemente todo o Estado e P2P Network, mas delega a sujeira matemática densa às IAs do ecossistema Python modular (executáveis limpos de boot efêmero = Dano Zero à Memória Ociosa).

## [0.9.8] - 2026-03-31

### 🚀 Sovereign Neural Architect (Dark Mode UI)
- **Universal Dark Theme Architecture**: Finalização completa da topologia `darkMode: 'class'` no Tailwind V4. O usuário agora orquestra e persiste globalmente as paletas de cores entre Dark/Light diretamente via `System Settings`, injetadas dinamicamente na `document.documentElement`.
- **Modals & Document Rendering (SSR)**: Removida a dependência cliente do `DOMPurify` dinâmico em favor de pré-processamento `marked` robusto das modais `ChangelogModal` e `ManualModal`, blindando a renderização nativa tipográfica e aderindo aos contrastes invertidos perfeitos.
- **Engineer Matrix Polish**: Todo o conglomerado de sub-rotas do Hub de Engenharia (`Analytics`, `Quality`, `Routing`, `RAG Pipeline`, `Fine-Tuning`, `Unsloth` e `Reflection Lab`) teve suas interfaces de cor M3 semânticas transmutadas, erradicando telas brancas hostis aos olhos no Modo Escuro. O sistema injeta coerência total do header à seleção de abas (com cores de destaque azuis sutis no texto e backgrounds amenos).

### 🎨 Refinamento Cirúrgico & Polimento Visual
- **Obsidian Callouts Dark Mode**: Integrados estilos reversos para os Callouts do *TipTap/Markdown* (`[!info]`, `[!warning]`, `[!danger]`, `[!success]`). As glosas da Máquina e do Editor agora absorvem a luminosidade da Vault, exibindo backgrounds translúcidos discretos sob tema noturno.
- **Telemetry Hardware UI Widget**: A sobreposição isolada do monitor em tempo-real (T/s, Model e VRAM) obteve tratamentos de refratância nativos `dark:bg-[#1d253b]` e contorno refinado para encaixe visual absoluto acima das barras de navegação.
- **Sovereign Chat Actions Refine**: Reestilizados assincronamente os botões atômicos dinâmicos (`Copy`, `Replay`, `ThumbsUp`, `ThumbsDown`) que aparecem flutuando em hover sobre as mensagens de LLM. Eles agora invocam discretamente fundos azuis e cinzas foscos, preservando a imersão na resposta textual.
- **Markdown Tables Dark Mode**: Corrigido o bug visual onde tabelas renderizadas no Editor (TipTap) e no Chat (Prose) ignoravam o tema escuro exibindo headers e borders estourados em branco. Forçadas classes bg-[#0c1324] e rgba(12, 19, 36, 0.6) nos headers.
- **Sidebar Spacing Consistency**: O espaçamento (`gap`) e as caixas (`py-3`) das rotas cruciais (`Vault`, `Projects`, `Chat`, `Home`) no Control Hub foram rigorosamente ajustados. No estado Colapsado (minificado) eles respiram amplamente, e no modo Expandido mantêm a harmonia vertical sem sobreposições grosseiras como estavam originalmente.
- **Tri-Agent & Dropdowns Visibility**: As seleções de IA no *System Settings* (`The Doctor`, `The Coder`, `The Nurse`) agora manifestam visibilidade perfeita de background preta contra os formulários dinâmicos.

## [0.9.7] - 2026-03-28

### 🚀 Enterprise RAG Pipeline & Agentic Search Loop
- **Malha Tool Calling em Rust (`api_trainer.rs`)**: A extinta arquitetura serial de Web Scraping retrograda (onde o modelo apanhava passivamente e não tinha controle do escopo temporal de busca) foi morta. Injetado um Loop Agêntico que escuta Schema JSON estrito. O LLM Local agora ativamente clama a requisição na Internet através das Ferramentas da Trindade Soberana, para, e depois continua da onde parou emulando Re-act behavior profundo.
- **The Ghost Fallback Chain (`research.rs`)**: Para abolir o terror dos Web Application Firewalls (CloudFlare Drop Rate HTTP 403), engenhamos um cascateamento resiliente que apela por milissegundos a Índices Descentralizados (CDX). A varredura agora ataca paralelamente e organicamente o `Internet Archive (Wayback)`, `Arquivo.pt` (Herança Lusófona), `UK Web Archive` e o sub-node Vefsafn Islândico. Se o endpoint alvo primário for negado por robôs, a malha apela pra memória histórica humana do próprio Wayback Cíbrido. Sem limites.
- **Cross-Encoder Reranker Local Injetado (FastEmbed)**: Instalada a suíte `fastembed` para processamento brutal Anti-OOM. A interface capta 50 urls brutas raspadas, e as corta via macro iteradora `unicode-segmentation`. Com a matriz de micro-chucking na memória volátil, ele rankeia puramente utilizando o BAAI `BGE-M3 Reranker` local. O LLM não engole mais Ads de sites da Web; ele mastiga incialmente apenas as `Top-35` sentenças semanticamente ricas para deduzir suas elaborações, livrando o PC local de latências colossais.
- **Cognitive Quarantine Ledger**: Toda falha de bloqueamento por firewall da busca não será mais atirada no limbo. O SQL Sensus Registry foi expandido e grava relatórios precisos de incidentes, retro-alimentando o usuário para liberação de Quarentena sem perder fluxos preciosos no WAG.
- **Inquisitor Safety Sub-Billion Filter**: Extirparam-se ativamente anomalias de Inquisidores "Halucinados". O Llama proíbe a atribuição de modelos abaixo de 3 bilhões de coeficientes para o posto de Juiz da Informação Web (`1.5b`, `smollm`, `deepseek-r1-1.5b`). Um `cargo build` purificado garante a validação tipográfica.

### 🛡️ The Anti-Hallucination Matrix (SLM Rigidity)
- **StrictCitations & Null-Safe Schema (Fase 1)**: O Extrator Primário foi reimplementado para forçar a tag XML `<scratchpad>` antes de qualquer extração escalar. O modelo é acorrentado a um contrato JSON onde copia verbatim a sentença referenciada (`[- Chunk X]`). Qualquer desvio reverte a saída para `DADO NÃO ENCONTRADO`, erradicando alucinações matemáticas sob estresse.
- **Adversarial Verifier & CoVe (Fase 2)**: Inserção cirúrgica de um validador de oposição (Chain-of-Verification). Terminada a filtragem do extrator primário, o modelo sub-analista `Phi-3.5` inspeciona implacavelmente o dado cruzado contra os *chunks* originais. Se o validador emitir `REJECTED`, o motor Rust aplica veto absoluto, impedindo o vazamento de falsos-positivos na interface UI final.
- **Working Memory Dinâmica (Fase 3)**: Mitigada a "Amnésia" comportamental de LLMs hiper-ágeis em conversas contíguas. A API de Chat (`api.rs`) intercepta logs com mais de 3 turnos e injeta um State JSON (`<state_memory>`) para focar estritamente na fronteira sem repetir o passado consolidado. Na rotina inferior (`api_trainer.rs`), o motor Reranker foi blindado com o *LongContextReorder*, empurrando matematicamente os blocos ideais para os extremos anatômicos da Janela de Atenção.

### 🚀 The Sovereign RAG Trinity (Map-Reduce Architecture)
- **Agent 1: RAG Planner**: O motor Rust agora intercepta a Diretiva de Pesquisa Profunda do usuário e aciona silenciosamente o LLM Local para decompor ordens complexas em um Array JSON de Micro-missões específicas, estilhaçando o problema investigativo de acordo com o padrão Plan & Execute.
- **Agent 2: RAG Extractor (Vector DB)**: O orquestrador injeta puramente em memória (Rust Native) um filtro matemático de *Cosine Similarity* sub-atômico. A malha filtra 30.000 tokens de ruído Web, separa estritamente os "Top-5" parágrafos dourados via vetores, e força o LLM leve a responder *exclusivamente* as micro-perguntas baseadas naquele bloco, erradicando a Alucinação "Lost in the Middle".
- **Agent 3: RAG Synthesizer (Dynamic Model Selection)**: Construído um Elemento Dropdown no controle de Deep Research (UI Svelte) permitindo permuta tática de LLMs em tempo de execução. O "Dossiê Progressivo" do Agente 2 agora é servido ao `qwen2.5:14b` (Heavy Analytics) ou `llama3.2` para formatação blindada final.
- **URL Trust Matrix Vetting**: Substituição de strings cegas por um Scoring Engine purista em Rust. Sites .gov, .edu.br e órgãos acadêmicos (Tier 1) agora obliteram fontes amadoras de SEO, subindo forçadamente para o Top-20 ranking de extração RAG.

### 🤖 RAG Engine Autómaton & Hallucination Radar Convergence
- **Self-Healing RAG (Autómaton Node)**: Escrito e executado um script cibernético fora de banda (`auto_resolve.mjs`) que se conectou ao SQLite e invocou localmente a LLM (`llama3.2`) para atuar como Curadora de Conhecimento. O motor sintético escreveu automaticamente explicações densas para todos os Gaps faltantes e injetou fisicamente as resoluções no Vault em Markdown via API REST, zerando a dívida técnica da base de conhecimento da aplicação.
- **Deep Observability Stream (Axum)**: O interceptador SSE (Server-Sent Events) no gateway de chat em Rust (`api.rs`) foi reconstruído. Agora o sistema clona e despacha ativamente qualquer contexto RAG, Web Search ou Metadados de Sistema *genuínos* e os vincula aos prompts, jogando-os estritamente para a fila da tabela `evaluations`. O bug milenar onde 'The Nurse' não encontrava insumos reais para auditar foi completamente estancado.
- **Zero-Shot Paperclip Node**: Implementada a injeção volátil de memória na interface de Chat. Arquivos de texto e código (`.md`, `.rs`, `.py`, `.json`, `.csv`) anexados via clipe de papel agora são carregados instantaneamente via `HTML5 FileReader` direto para a malha de contexto (`inputContext`), pulando a indexação massiva do RAG para avaliações ultra-rápidas do LLM.
- **Native Changelog Modal**: A tag semântica de versão (`v0.9.7`) no menu `Control Hub` evoluiu para um botão interativo. Ao clicar, o sistema carrega o histórico completo de versões (`CHANGELOG.md`) de forma responsiva, utilizando o `DOMPurify` blindado no client-side (`$effect`) para prevenir falhas drásticas de SSR.
- **Semver UI Badge**: Injetado badge minimalista no cabeçalho do Sidebar, expondo explicitamente a versão da release compilada ativamente no Vite.

### Corrigido
- **Fim da Alucinação Estática do Radar**: Extirpada a âncora de dados mockados (`system-init`) fundida no loop `auto_evaluator.rs`. O Radar de Alucinações (Quality & Gaps UI) inicializa puramente em 0% e agora audita e exibe com total honestidade o *Grounded Confidence Index* calcado puramente no pareamento Humano/Máquina local.
- **SQLite Database Lock Timeout**: Solucionado o silencioso engasgo HTTP que ocorria quando The Nurse avaliava dezenas de transações pesadas em lote no Histórico Cíbrido. A espera assíncrona nas validações do Node (`res.text()`) libertou o DB de concorrências letais nas rotas PUT.

---

## [0.9.6] - 2026-03-24

### Adicionado
- **Zero-Shot Paperclip Node**: Implementada a injeção volátil de memória na interface de Chat. Arquivos de texto e código (`.md`, `.rs`, `.py`, `.json`, `.csv`) anexados via clipe de papel agora são carregados instantaneamente via `HTML5 FileReader` direto para a malha de contexto (`inputContext`), pulando a indexação massiva do RAG para avaliações ultra-rápidas do LLM.
- **Native Changelog Modal**: A tag semântica de versão (`v0.9.7`) no menu `Control Hub` evoluiu para um botão interativo. Ao clicar, o sistema carrega o histórico completo de versões (`CHANGELOG.md`) de forma responsiva, utilizando o `DOMPurify` blindado no client-side (`$effect`) para prevenir falhas drásticas de SSR.
- **Semver UI Badge**: Injetado badge minimalista no cabeçalho do Sidebar, expondo explicitamente a versão da release compilada ativamente no Vite.

---

## [0.9.6] - 2026-03-24

### Corrigido
- **MacOS IPv6 Inference Pipeline**: Eliminada a falha onde requisições de Chat silenciosamente morriam (Connection Refused) no Apple Silicon. Alterado o proxy Axum de `127.0.0.1` rígido para o resolvedor orgânico `localhost:11434`, respeitando a stack nativa IPv6 do Ollama no Darwin.
- **Darwin Vector Injection**: Criado o design purista e transparente (`app-icon-mac.svg`) dedicado estritamente ao bundle Apple (`.icns`), preservando intacto a variante Dark Green nativa de empacotamento do Windows/Linux.

---

## [0.9.5] - 2026-03-24

### Adicionado
- **Deep Memory Sync (Amnesia Fix)**: Implementada a retenção de contexto temporal. A interface Svelte agora constrói arrays expansivos embutindo todo o fluxo da conversa pregressa, extinguindo as antigas inferências "Zero-Shot Amnésicas" e pavimentando as rotas avançadas de Raciocínio multi-hop.
- **Sovereign Multi-Tenant Architecture**: Isolação sistêmica do estado global `chatLayoutState`, solidificando arquiteturas sub-tenant que blindam os painéis operacionais.

---

## [0.9.4] - 2026-03-23

### Corrigido
- **DOS Canonicalize Paths**: Aplicada macro universal em Rust para decepar estritamente os artefatos visuais `\\?\` gerados pelo subsistema do Windows ao resolver caminhos absolutos nativos. As rotas do Vault renderizam puras de volta para a UI Svelte.
- **Borrow Checker Panic no Rust**: Blindagem profunda resolvendo o erro Crítico E0382 no clonador da fila `resolved_model`, extirpando os picos severos e fatais da engine transacional nativa na escalada.
- **GitHub Action Tag Triggers**: Revigorada a estrutura de engrenagem YML do CI/CD assegurando disparo perfeitamente sincronizado durante push tags (`v*`).

---

## [0.9.3] - 2026-03-22

### Adicionado
- **Standalone Cross-Platform Pipeline**: Estabelecidas pontes de integração do `tauri-cli` no O.S para geração híbrida de artefatos Windows (`.msi`, `.exe`) e executáveis AppImage independentes.
- **Native Sidecar (Phases 41-42)**: Emancipação da base acoplada do Tauri, permitindo a orquestração de sub-rotinas compiladas injetadas remotamente no diretório de instalação do O.S.

---

## [0.9.2] - 2026-03-22

### Corrigido
- **DevSecOps Gate 4 Clippy Restricts**: Normalizado todo o ecossistema base RUST contra advertências puristas do `clippy` (Gate 4). Condicionais booleanas desidratadas para macro `saturating_sub`, validando Green Build na esteira Github.
- **ReWOO Hallucination Proxy**: Neutralizou o envenenamento fantasma onde a malha de abstração de Workflow inseria instruções vazias no prompt do Sistema, confundindo o modelo final.

---

## [0.9.1] - 2026-03-22

### 🚀 O Berço do Deep Research WAG

### Adicionado
- **W.A.G (Web Augmented Generation) Module**: Nascimento da estrutura central `deep-research`. O motor Llama agora indexa o modelo aberto da web, construindo scrapes semânticos e jogando-os estaticamente organizados de volta pro Vault local para consumo cíbrido.
- **Web Scraping Mesh Persistence**: Camada conectiva desenhada entre a pesquisa ao vivo (Serper/DuckDuckGo) e o indexador vetorial do RAG, evitando perdas de informação efêmera.
- **Dual-Engine Multi-Hop Evasion**: Engrenagem defensiva nativa de Web Application Firewall (WAF) spoofing, permitindo coletas ininterruptas pelo Sovereign Bot em superfícies blindadas.
- **UI Research Toggle**: Inserido gatilho booleano visual direto na caixa de texto do Svelte, orquestrando a injeção sob-demanda do Deep Research ao lado de instâncias do RAG.

---

## [0.9.0] - 2026-03-22

### 🚀 O Despertar do Protocolo MCP & Ollama Real Engine

Esta release introduz a interoperabilidade de agentes IDE e extermina os Mocks Falsos da arquitetura Cíbrida, injetando fluxos autênticos do Ollama e validando a maturidade corporativa da aplicação com bateria de testes rígida.

### Adicionado
- **Model Context Protocol (MCP) Server**: Construção nativa do Servidor MCP (`/v1/mcp/sse` e `/v1/mcp/message`) em Rust (Axum), permitindo que IDEs de Terceiros (OpenCode, Cursor, Windsurf) gerenciem e indexem o Sensus Vault como ferramenta nativa, obedecendo ao protocolo aberto da Anthropic.
- **Ollama Real Model Creation API**: Os mocks visuais no *Model Trainer* foram implodidos. A suíte de rotas `api_trainer.rs` aciona autenticamente o daemon nativo via porta `11434`, disparando builds e pulls das imagens estritamente controladas no bare-metal.
- **Server-Sent Events (SSE) Progress Tracker**: Transmissão em tempo estrito do payload gerado pelo Ollama (MB por segundo, Status de Digest) direto para a interface Svelte 5 (Model Trainer) anulando deadlocks visuais de longa duração.

### Segurança & Qualidade (QA Suite)
- **Rust Sandbox Hardening**: Implementado barreira Anti-Directory Traversal (`validate_safe_path()`) no núcleo MCP com testes unitários dinâmicos via `tempfile`, barrando agentes externos e payloads N8N de lerem chaves SSH ou arquivos ROOT fora da bolha arbitrária do Vault.
- **Svelte Zero-Warning State (TypeScript/A11y)**: Extirpados +30 alertas críticos de Acessibilidade (Labels ausentes) em dezenas de componentes vitais do Svelte, em conjunto com o expurgo de erros inferenciais críticos de Type-Safety no roteador Global. O Linter (`svelte-check`) atinge `0 Errors` antes da pipeline.
- **Premium Identity Silhouettes**: Extirpado o Avatar de texto padrão ("AD" via `ui-avatars.com`), introduzindo um layout estruturado vetorizado (`User` Lucide) orgânico em paleta Navy Blue com sombras radiantes (`drop-shadow-sm`).
- **Zero-Trust Credential Sweep**: Todo o código encapsulado nesta release foi homologado com escaneamento imperativo assíncrono do `zricethezav/gitleaks`, garantindo 0 chaves vazadas.

## [0.8.3] - 2026-03-21

### 🚀 The Omniscient Cibrid Hub & Dynamic Topology Mapping

Esta release eleva o nível de Autoconsciência do Motor Rust. O painel central do *Sovereign Pair* (Control Hub) descarta de vez dependências mockadas e passa a atuar como um monitor Cíbrido genuíno do ecossistema local do hospedeiro, extraindo variáveis do barramento de hardware com precisão granular.

### Adicionado
- **Native GPU Autodiscovery**: Implementada macro multiplataforma condicionada no Rust (`#[cfg(target_os="linux|macos")]`) que invoca os utilitários de sistema nativos (`glxinfo`, `system_profiler`) para inferir organicamente o Chipset e o Total VRAM Máximo (MB/GB) em tempo de execução, injetando de volta na dashboard UI Svelte sem latência.
- **Dynamic Hub Reality**: A interface do `Home` finalmente transcende ao status real do Vault e Projetos:
  - `Active Projects e Pending Tasks`: Orquestração reativa do Kanban agora exclui logicamente *archived nodes* e contabiliza em tempo-real as progressões do motor Sensus.
  - `Categories Placed e Synced Files`: Leituras de indexação sincronizadas bit a bit lendo as chaves exatas do `sensus_documents` e diretórios raiz no SO.
  - `Firewall Blocks & LLM Latency`: Status dinâmico consumindo gaps embutidos de segurança da thread de execução do proxy *OpenCode*.

### Corrigido
- **Blindagem do Payload Axum (Missing Properties JSON)**: Eliminado o drop visual silenciado (`struct missing`) no Frontend do Svelte, orquestrando perfeitamente a serialização `serde_json` do nó de Hardware para refletir instâncias ociosas da inteligência artificial no SysMonitor.

## [0.8.2] - 2026-03-21

### 🚀 Vault Explorer, Svelte UI & Performance Cíbrida

### Adicionado
- **Integração Real-Time Hardware Telemetry (Memória OS)**: O motor Axum agora lê nativamente `/proc/meminfo` para injetar no dashboard do *Control Hub* a volumetria exata do Hardware (RAM) do hospedeiro atual, neutralizando o limite mockado de 24GB do layout antigo.
- **Vault Data Explorer UI Refinada**: Implementada uma barra de *Command Line Search* unificada, expurgando as inconsistências das antigas interfaces de filtragem e empoderando o grid de arquivos via tags (ex: `tag:projeto`), *paths* e clique dinâmico (sort) nos cabeçalhos transversais.
- **Componente Props Escalado (BlockEditor)**: O Popover Flutuante de edição Frontmatter YAML (`Props`) sofreu um recálculo profundo nas diretivas Tailwind, adquirindo a robustez necessária (`w-[450px]`) para não estrangular chaves e arrays longos e sobrepor as engrenagens de refração visual.

### Corrigido
- **Context-Bombing & ReWOO Engine Latency**: Refatorado o roteador híbrido Rust (`HybridRouter::dispatch_planner`) que estava disparando uma varredura completa (`VaultSearch`) em cada interação mínima do usuário no Chat nativo. A lógica reconfigurada aguarda agora condicionalmente por instruções com `@vault`. Essa mudança resgatou instantaneamente o LLM do estado comatoso (onde demorava minutos lendo 16k tokens).
- **Integração de LLM (The Doctor) e Svelte Typings (HTTP 422)**: Erradicado o travamento bruto onde objetos numéricos (Integers) vazavam do Estado (`globalState.activeWorkspaceId`) e implodiam a desserialização do Endpoint Axum. Conversões blindadas em String asseguraram a consistência dos requests do chat intra-arquivos.

## [0.8.1] - 2026-03-20

🚨 **A Atualização Estabilizadora**
Esta não-planejada e microscópica "micro-patch" solidifica o Core nativo do Motor Cíbrido contra "warnings" da API e desvios de tabela (drift). Ela coroa o esforço gigantesco da estabilização e garante fluidez cega nos Linux / Mac / Win sem warnings legados. 

### 🎉 Melhorias e Correções Profundas (Hotfixes):
- **O Fim da Panificação SQLite / Sync Engine**: Eliminado o bug "Falha ao Ler Tabela de Workspaces" que corrompia as entranhas assíncronas do monitorador The Watcher. O problema de derivação do Schema (onde ele procurava a coluna como String `absolute_path` quando, estritamente, ela era um Integer + String `path` nativo) foi totalmente sanado. As tabelas SQL agora vinculam os File System FSEvents perfeitamente.
- **Limpeza do Lixo de Logs (Rust Native CLI)**: Compilado com Zero Warnings de macros importadas indevidamente (Linter do Cargo). A biblioteca The Nurse / The Watcher (`fs_extra` & `Copy`) e as passagens do `Tauri::AppHandle` foram envelopadas através das travas blindadas condicionalmente via `#[cfg]` Macros, impedindo "Unused Imports" do Windows e do Apple macOS em um ambiente de produção Linux. 
- **O Fim da Mega-Bomba de Artefatos no Release Workflow**: A CI Pipeline que gerava nossos instaladores foi radicalmente lapidada. Variáveis dinâmicas para forçar `Node.JS 24` em processos nativos paralelos (evitando "Deprecation Warning"), e o expurgo do *Artifact Glob Path* ("`**/*`" $\rightarrow$ "`*.AppImage, *.msi`") no Github. O Uploader do GitHub Release agora não travará na nuvem por Rate Limits tentando ejetar milhares de arquivos recursivos em C++ no log, postando EXCLUSIVAMENTE pacotes empacotados.

## [0.8.1] - 2026-03-20

### Melhorias e Correções Profundas (Hotfixes)
- **O Fim da Panificação SQLite / Sync Engine**: Eliminado o bug "Falha ao Ler Tabela" corrompendo as entranhas assíncronas do monitorador The Watcher. O problema de derivação do Schema de `absolute_path` (String) para `path` (Integer mapping) foi totalmente sanado. 
- **Limpeza do Lixo de Logs (Rust Native CLI)**: Compilado com Zero Warnings de macros indevidamente importadas. A biblioteca The Nurse / The Watcher (`fs_extra` & `Copy`) foram envelopadas através das travas condicionalmente blindadas `#[cfg]`, impedindo "Unused Imports" do Windows e MacOS. 
- **O Fim da Mega-Bomba de Artefatos no Release Workflow**: A CI Pipeline que gerava nossos instaladores foi radicalmente lapidada. Variáveis dinâmicas forçam `Node.JS 24` em processos nativos paralelos (evitando "Deprecation Warning"), e o expurgo do *Artifact Glob Path* protege o Uploader do GitHub Release contra API Rate Limits e Not Found Errors.

## [0.8.0] - 2026-03-20

### Adicionado
- **Universal Installers & GUI Setup**: Lançamento do Instalador Visual Tauri v2. O App engloba o Backend RUST injetado via `externalBin` e executa um Setup Wizard na primeira inicialização da Dashboard Svelte.
- **Arquitetura Cíbrida (Thin-Client e Fat-Daemon)**: O motor de dados e segurança (Sensus / SQLite) foi definitivamente movido para Background Daemons escalonados via `sudo/UAC/pkexec`.
- **System Tray (Area de Notificação)**: Adicionado suporte cross-platform nativo para manter a engine ativa enquanto o Frontend webview é desligado com segurança de RAM.
- **KDE Plasma & Shell Implants**: A injeção universal do `sovereign-pair-widget` (Plasmoids) e integrações nativas ocorrem silenciadas via `tauri-plugin-fs` como diretivas do "Usuário Local", anulando os riscos de vazamentos de superusuário do SysDaemon.
- **Logs Nativos Desktop**: A atividade gerada entre o escalonamento do daemon e inicialização das extensões agora emite um `.log` limpo na visualização do Desktop do hospedeiro.

## [0.7.2] - 2026-03-19

### 🛡️ Pipeline DevSecOps: Estabilização e Zero-Downtime CD Fixes

### Adicionado
- **Github Actions Node.js 24 (Future-Proof)**: Injetada a variável global `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` em todos os *workflows* da esteira FOSS, suprimindo advertências de depreciação do Node.js 20 em plugins vitais (`actions/checkout`, `actions/upload-artifact`).
- **Zero-Cost Stateful Backend (GPG Artifacts)**: Implementado um mecanismo no `deploy-oci.yml` para transferir criptograficamente a memória `.tfstate` do OpenTofu entre execuções isoladas do Github Actions. Previsto o *spawn* descontrolado de instâncias órfãs na Nuvem OCI.
- **Hash SHA256 na Chave SSH (GPG Strict)**: A encriptação da memória foi estabilizada através da compactação forçada da Private Key multilinha para um Hash estrito injetado via `stdin`, evitando o crash fatal por quebra de linha no parser do `gpg`.
- **Manual Binary Injector (Failover OCI)**: Construído utilitário nativo bash (`scripts/deploy_binary_manual.sh`) executável isoladamente pelo usuário para contornar falhas no loop de CD do Terraform. Ele trafega credenciais e baixa a Release privada via ponte e API REST da Github sem dependência de ferramentas locais limitadas no host.

### Corrigido
- **Ubuntu apt-get Freeze (cloud-init)**: O `runcmd` do OCI cloud-init estava congelando indefinidamente aguardando intervenção humana para lidar com alertas de "Daemons outdated" gerados pela instrução nativa do `apt-get upgrade`. A atualização de Kernel foi cortada da esteira, encurtando o bootcycle base em longos 10 minutos.
- **Fail-Fast Remote-Exec e Token Sync no OCI**: O script de injeção direta via SSH no Terraform (`compute.tf`) estava engolindo exceções (`gh: command not found`) com sucesso falso em exit loops. Refatorada a string para possuir validação `set -ex` (explodindo falhas críticas no log) e `always_run=timestamp()` forçando re-runs da action caso a instância suba órfã.
- **Oracle VCN DNS Blackhole**: Injetada diretiva estrita via `bootcmd` no `cloud-init` do Arch Linux/Ubuntu OCI para forçar a pré-configuração do `systemd-resolved` com DNS resilientes (8.8.8.8, 1.1.1.1) contornando o DHCP defeituoso nativo do OCI (`169.254.169.254`) que impossibilitava resoluções cruciais de espelhos APT e Github.
- **ActionLint e Semgrep Strictness (Gate 0 e 1)**: Refatorados comandos bash e re-alocadas variáveis de contexto Github para passar sob a malha fina da esteira CI Global. Neutralizada uma falsa vulnerabilidade de Shell-Injection capturada ativamente pelo SAST.
- **Zero-Trust KMS Encryption (SQLite)**: Subtituído o uso altamente perigoso de `unsafe { env::set_var }` por um cache atômico `OnceLock` para a Master Key, varrendo ativamente event log buffers com `zeroize()` para evitar vazamento do vetor criptografado GCM na Memória RAM.
- **SQLite Constraint Trap**: Corrigido um gap colossal onde a API Cíbrida enviava Inteiros Mágicos contra um esquema de banco aguardando UUIDs textuais no instante de criação de um Workspace Global, causando pânico fatal na inicialização de um OCI nativo.
- **Rust Unit Testing (Sovereign Core)**: Implementada uma Sandbox SQLite `in-memory` com mocks perfeitos de `tokio::sync::broadcast` para comprovar a eficácia contra Deadlocks e validar a consistência do Router Axum durante Ingestão de Diretórios.

## [0.7.1] - 2026-03-19
### Changed
- **CI/CD Unification**: FOSS DevSecOps matrices now strictly precede the Standalone Multi-OS Builder, forging a single sequential vulnerability-free build pipeline (`ci.yml`).
- **Artifact Namespacing**: Cross-OS artifacts dynamically rename to avoid Release overwrites on Github Actions.
- **Strict Semantic Versioning**: Refactored the internal tagging structure to omit the `v` wrapper, adhering cleanly to pure SemVer (0.X.Y).

## [v0.7.0] - 2026-03-19
### 🚀 Major Release - Svelte Mesh, Multi-Workspaces & Native CI/CD

### Added
- Complete migration of frontend architecture from Vue 3 to Native Svelte 5.
- Epic `Estabilidade e Certificação` effectively concluded (Vitest + Playwright).
- TipTap ProseMirror integrated directly with native DOM manipulations, eliminating Vue Virtual DOM memory leaks.
- Real-time Hardware Telemetry (T/s + VRAM) bonded natively to the OS Shell using Svelte `$state` tracking.
- KDE Plasma Widget Systray physically opens the Cybrid Web Hub (`127.0.0.1:38001`) bypassing obsolete Vue router links.
- Cross-OS CI/CD Action compiling native `windows-amd64`, `linux-amd64` and `macos-arm64` static executables.
- Complete system decoupling from Docker/Virtualization, elevating the core to Baremetal execution.
- Workspaces Sync via Sovereign Mesh (P2P), including .cybrid JSON credential roaming.
- Purged the entire Vue 3 `web-ui` directory.
- Deprecated legacy `vue-plugin` architectural footprints.
- Emojis unconditionally purged across the OS layout logic.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

> **⚠️ AVISO IMPORTANTE (SemVer Pre-Release):** Este produto **não está maduro o suficiente para a versão 1.0.0**. Todas as ramificações arquitetônicas atuais (Hub Cíbrido, SQLite-Vec, Motor Rust) estão na série `0.x.x` e sujeitas a quebras de contrato (Breaking Changes) sem aviso prévio. A estabilização corporativa FOSS não iniciou.

---

## [0.5.0] - 2026-03-18

### 🤖 Major Release - Agentic Workflows & Zero-Trust Sandbox

Esta versão introduz a primeira etapa de Autonomia Predial (Agentic Workflows) através das Fases 1 (Desacoplamento de Inferência) e Fase 2 (The Evaluator/Coder). Além disso, marca a erradicação cabal das dependências do Docker para a execução do Core Híbrido, tornando a stack Sovereign Pair totalmente portável em Rust nativo.

### Adicionado
- **ReWOO Orchestrator (Reasoning Without Observation)**: Modificada a topologia de requests cruas da OpenAI. A thread Rust agora intercepta os prompts complexos e constrói um DAG (Directed Acyclic Graph) pré-calculado, quebrando tarefas monolíticas em passos concorrentes. 
- **The Coder (Zero-Trust Sandbox)**: Introduzido um Gateway OCI `ssh_gateway.rs` nativo. Scripts gerados de programação ou ferramentas shell não são mais avaliados na máquina host, mas tunelados via subprocessos SSH assíncronos direto para as caixas de areia estéreis provisionadas na Nuvem Oracle, retornando as exceções/STDOUT para o LLM aprender sem ferir o repositório local.
- **KMS-Backed Credentials**: Migração completa das credenciais vitais de nuvem do formato `.env` expostas para o SQLite Key Management System. Chaves SSH, usuário e IPs agora são configuráveis pela Web UI sob forte encriptação AES-GCM 256.
- **KDE Plasma Widget (Wayland Native)**: Lançamento de um Plasmoid Desktop Nativo injetado diretamente no System Tray Explorer do SO. O app fornece telemetria *live* do Rust Core (Memória e Tokens por segundo) contornando totalmente as falhas de renderização do empacotamento AppImage (Tauri) sobre a pilha Wayland.

### Modificado
- **Integração Global Workspaces Total**: Adaptação da visualização hierárquica transversal no Vue3 (`VaultView.vue`). O Sensus Engine agora orquestra a varredura visual de todos os sub-workspaces declarados soltos pelo SO, sem duplicar/copiar um único arquivo físico.
- **Desacoplamento Backend Docker**: Início da supressão das amarras containerizadas. O projeto passa a exigir cadeias CI/CD puras para provisionamento de executáveis `standalone` no lugar do orquestrador efêmero Compose.

### Corrigido
- **Sensus TipTap Component Bug**: Solucionado o glitch intermitente de *race-condition* no mount point visual do editor de blocos Vue3, causado pela assincronia pesada da transição para workpaces distribuídos O.S.
- **MemCache Zumbi KDE Plasma**: Aplicados *hotfixes* profundos e reinstalação paramétrica de pacote para dissipar referências órfãs (`PlasmaCore.IconItem`) travadas no cache da VM QML local.

---

## [0.4.0] - 2026-03-14

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

### Corrigido
- **Ollama DNS Resolution na Oracle (A1)**: Corrigido o erro de timeout onde a API não listava os modelos instalados em Bare Metal na nuvem Oracle via `host.docker.internal:11434` e `extra_hosts`.
- **UI Local Models Discovery**: Corrigida a listagem "Nenhum modelo encontrado" no front-end por roteamentos assíncronos pendentes.
- **TipTap Visual Desync & Markdown Scrambling**: Consertado bug massivo onde o Editor Vue renderizava HTML `<table>` cru em vez de Markdown, e quebrava o conteúdo de arquivos fonte (`.rs`, `.py`) interpolando-os erroneamente. Adicionado Visual-Source debounce.
- **The Doctor (Spotlight) Delays**: Remediado o atraso de mais de 3 minutos no carregamento do Spotlight Modal resolvendo impasses de proxy na interface de Node Isolado.
- **Database OperationalError (SQLite Locked)**: Corrigido o drop HTTP 500 dos comandos `/sys` causados por race conditions no fechamento da Database Vectorial (`sovereign_memory.db`) durante indexações longas.
- **Telemetria Mockada**: Finalizada a renderização em tempo pseudo-real. O dashboard `CronosTimeMap.vue`, `RealtimeLogs.vue`, e `TokenMetricsTracker.vue` agora escutam Streams SSE genuínos trafegando metadados dinâmicos e gaps do motor Rust.
- **Meta-RAG SQLite-Vec Migration**: Rota `/sys` comutada integralmente do pacote depreciado de ChromaDB para as tabelas nativas virtuais do novo compilador SQLite-Vec.
- **Emojis Poluidores & Timings API**: Limpeza sistemática de strings emotivas (ex: "🧠 Consultando Meta-RAG") em `routes.py` para adequação formal corporativa e supressão de exaustões silenciosas do motor FastAPI.
- **TheAccountant AST Fallback**: Arrumado bug matemático onde células aninhadas negativas geravam strings letais (ex: `==A2-B2`) no motor de grafos. Regex encapsulado em parênteses.
- **Postgres ID Overflow**: Impedida a interface gráfica de cuspir um `Date.now()` nos PK Integer do banco durante ações de 'Thumbs Up/Down'.

---

## [0.3.2] - 2026-03-08

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

## [0.3.1] - 2026-03-07

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

## [0.3.0] - 2026-02-27

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

## [0.2.0] - 2026-02-26

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

## [0.2.2] - 2026-02-24

###  Major Release - Backend API, Citações e Modularidade

### Adicionado
- **Provedores LLM Modulares**: Refatoração profunda no núcleo (`config.py` e `llm_factory.py`) para permitir plugar facilmente `openai`, `anthropic`, `groq`, `gemini`, mantendo o `ollama` como a escolha local padrão e blindando a soberania digital.
- **FastAPI e Server-Sent Events (SSE)**: Desacoplamento do motor LlamaIndex do CLI. Adicionados endpoints RESTful em `src/api` rodando em portas dedicadas (`uvicorn`) com streaming de respostas em tempo real para conectar frontends (Chat UIs, Sensus Vault, WhatsApp).
- **Extração Formal de Citações e Fontes**: O RAG agora retorna proativamente ao usuário os arquivos locais ` caminho/do/arquivo.md` ou URLs ` url` usados na inferência, inserindo-os no final de cada streaming.
- **Auto-pull Inteligente do Ollama**: O CLI deteta a falta de modelos vitais no Ollama e proativamente força o download transparente ao invés de abortar o terminal secamente.
- **Tipagem Forte e Testes Modernos**: Atualização completa na validação da base convertendo testes estáticos ao ecossistema `pytest`, utilizando `fixtures` puras e o isolamento seguro vía `pytest-mock` e `MagicMock`, blindando regressões na pipeline de ingestão.
- **Compatibilidade do Ambiente**: Reconfigurado o ambiente local de testes do ChromaDB para rodar suave e estavelmente apenas com versões do Python `3.12` a `3.13`, contornando problemas no ecossistema `Pydantic V1`.

---

## [0.2.1] - 2026-02-17

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

## [0.2.0] - 2026-02-16

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

## [0.1.2] - 2026-02-16

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

## [0.1.1] - 2026-02-16

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

## [0.1.0] - 2026-02-26

### 🚀 Alpha Release - Phase 6 Persistence & Web UI

**Commit**: `d4a7ff9`

### Adicionado
- **FastAPI Engine**: Primeira transmutação do sistema CLI para um servidor web assíncrono modular via FastAPI, incluindo autenticação (`auth.py`), abstrações REST (`routes.py`), e roteamento de dependências de RAG.
- **Sovereign Web UI (Vue 3)**: Inauguração da primeiríssima interface gráfica no navegador utilizando componentes modulares nativos do Vue.js (suportando *Setup* interativo e telas de *Login*).
- **Obsidian Sensus Plugin**: Lançamento do primeiro cliente integrado (em *TypeScript*) para o ecossistema Obsidian, fundindo o Editor de Notas ao motor P2P e RAG do Vault.
- **Core Abstractions**: Refatoração estrutural profunda do Python original, isolando módulos sistêmicos em `engine_builder.py`, `llm_factory.py`, iteradores nativos em `web_search.py` e o demônio rastreador autônomo `watcher.py`.
- **Database & Formats Architecture**: Consolidação física dos DBs relacionais SQLite e extensiva literatura fundadora gerada em `ARCHITECTURE.md` e `FILE_FORMATS.md`.

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
