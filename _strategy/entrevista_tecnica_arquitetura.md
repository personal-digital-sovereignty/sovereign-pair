# Entrevista Técnica: Sovereign Pair (Master Architecture Overview)

**Data da Documentação:** Abril de 2026
**Contexto:** Compilação arquitetural focada no aspecto técnico, DevSecOps e na engenharia Cíbrida (Agentes + Lógica Clássica) puramente explicada e registrada.

---

## 1. Qual o foco do nosso projeto? (Explicado sem dialetos)

O **Sovereign Engine** é um Orquestrador Cíbrido (Cyber-Híbrido) de Engenharia de Dados e Pesquisa Profunda. Em linguagem simples: é uma arquitetura construída em **Rust e Python** que permite rodar orquestrações de Inteligência Artificial Local em cima do hardware do consumidor de forma 100% determinística. 

Enquanto o mercado constrói "Chatbots que alucinam", nós construímos uma esteira de montagem (*Pipeline*) de análise corporativa. O objetivo é pegar perguntas altamente complexas (Finanças, Geopolítica, Macroeconomia), dividi-las em buscas matemáticas isoladas, processar as matrizes por fora do cérebro da IA usando scripts rígidos (ex: `Pandas DataFrame`), e ejetar um relatório financeiro/executivo C-Level inquestionável. Tudo isso rodando *air-gapped* usando Local-LLMs.

---

## 2. As nossas tools (Ferramentas) estão todas em `python_workers/dataset_proxies`?

**Não.** O desenho arquitetural separa a Inteligência Executável do Lixo Estático:

As "Tools de Inteligência" (Lógica Python de Engenharia) estão espalhadas diretamente na raiz de `core/python_workers/`. Destacam-se:
- `registry.json` (Aonde as ferramentas são cadastradas pro Agente ler).
- `sovereign_matrix.py` (Buscador de finanças e macroeconomia).
- `analyze_and_join_time_series.py` (Onde reside o Pandas Joiner e a extração do *Pearson $r$*).
- `culture_matrix.py` e `academic_matrix.py`.
- `empirical_verifier.py` (Advogado do Diabo antivieses).

Já a subpasta `core/python_workers/dataset_proxies/` serve puramente como um "Mock/Cache". Ela armazena JSONs mortos (como `gasolina.json`), agindo como Proxy local caso as APIs primárias sofram Timeout ou Derrubada, garantindo tolerância a falhas. Em resumo: Tools no `python_workers/`, Caches no `dataset_proxies/`.

---

## 3. Resumo dos Agentes da Arquitetura (Um a Um)

A arquitetura se divide em dois eixos paralelos: os Cérebros (Engines Locais LLM) e os Oráculos (Tools Python).

### Eixo 1: A Tríade Cognitiva (LLMs Ativos)
1. **The Master (O Pesquisador Orquestrador):** Geralmente um SLM veloz (`Qwen 2.5:7b` ou `Llama 3.1:8b`). Seu papel não é responder ao usuário, mas quebrar problemas lógicos usando **Tool Calling**. Ele invoca a internet e monta a cesta de "Fatos Brutos".
2. **The Inquisitor (A Vacina Epistêmica / Advogado do Diabo):** Uma inteligência pragmática (`Mistral-Nemo:12b`) que critica a síntese do The Master procurando furos lógicos e falsas correlações estatísticas. É o nosso "Firewall Anti-Alucinação".
3. **The Scribe (O Redator Sênior C-Level):** Acionado por fim (`Phi4:14b`). Opera às cegas lendo o Dossiê Perfeito construído pelos outros estagios (e validado matematicamente) com o único trabalho de escrever um poderoso *Data Storytelling* livre de invenções.

### Eixo 2: Modelos Oráculos (Data Tools Python)
1. **Open-Data Matrix:** Tickers financeiros e indicadores Macro.
2. **Especulative Oracle (Mercado Futuro):** Isolamento paramétrico que restringe consultas da IA a contratos futuros/hedges, impedindo que ela confunda a bolsa Spot histórica com a especulativa.
3. **Sovereign Symbiotic Joiner:** Script nativo para Outer Join Pandas. Desobriga o *LLM* a cruzar dados temporais, fazendo tudo deterministicamente.
4. **Academic Gateway:** Extração dura via PubMed, NASA, e bases *arXiv*.
5. **WikiLeaks & Geo-Político:** Varredura OSINT dedicada.

---

## 4. Agentes aplicados no contexto do RAG/WAG?

No que tange o isolamento RAG (Retrieval-Augmented Generation) / WAG (Web Augmented Generation), temos os arquivistas focados e engessados:

1. **The Vectorizer:** Embedders focados em contexto (ex: `bge-m3` ou `nomic-embed`). Convertem documentos corporativos em coordenadas densas e matemáticas. 
2. **Lexical Sieve (Filtro BM25 Nativo):** Em Rust, nós penalizamos Falsos Positivos do RAG. Um pré-filtro lê densidade de contexto antes mesmo de incomodar o buscador Vetorial, abaixando muito a latência (`latency override`).
3. **The Reranker / Cross-Encoder:** Assina ou reprova a qualidade do que foi buscado; evita o fenômeno "Lost in the Middle" da janela de contexto eliminando laudas irrelevantes antes que cheguem na mesa do *The Master*.
4. **Multi-Node Reader Matrix:** Substitui um Scrapper genérico por falanges de extração Web Paralelas visando driblar *Rate Limits* sem usar APIs pagas de extração Web (WAG Real Time).

---

## 5. Como usamos o `llama.cpp` e GGUFs na Engine?

Nós não usamos o Python nem bibliotecas lentas como LlamaIndex para as contas de Inferência de Agentes. O Rust do nosso backend dispara requisições via Ollama, que atua apenas como uma API Envelopadora. O maquinário pulsante é 100% C/C++ injetado diretamente em GPU/CPU via Metal/CUDA no `llama.cpp`.

Modelos como `Phi4` de 14 Bilhões de parâmetros exigiriam memórias absurdamente pesadas na casa dos 40GB+. Com arquitetura GGUF manipulada pelo `llama.cpp`, aplicamos Quantizações Rigorosas (`Q4_K_M` e afins), condensando matrizes massivas para operarem em simples memórias RAM convencionais de 27GB com velocidade e performance "Bare-Metal".

---

## 6. Como implementamos o Memory GC (Limpeza do Ollama)?

Sendo o Ollama um servidor persistente, ele tenta fazer cache do que carrega (para fins de velocidade nas próximas perguntas). Isso colapsaria a RAM nas alternâncias (Ex: Qwen saindo da GPU para Phi4 entrar). 

**Solução:** Identificamos que o framework herda o flag `--keep-alive`. Nós encapsulamos isso na chamada `fire_eviction_protocol` no nível do Kernel Rust (`memory_manager.rs`). Usando um Task Token Mudo (Empty Request) com um sub-sinal json `{ "keep_alive": 0 }` atrelado a um Timeout mínimo "Fire-and-Forget" (300ms), ordenamos a desconstrução e ejeção total do Grafo Computacional do último Agente do núcleo VRAM. Um Garbage Collector nativo, implacável e hiper-veloz que limpa a calçada de modelos pesados para o *The Scribe* caber.

---

## 7. Como se exibe as matrizes matemáticas na Tela (Editor)?

Usamos SvelteJS V5 mesclado à estrutura **TipTap (ProseMirror)** via `BlockEditor.svelte`.

Quando *The Scribe* gera os logs de Matrizes/DataFrames advindos do motor Simbiótico Pandas Python, ele imprime as bordas rústicas em puritano Markdown `| Mes | Inflacao |`.
Na WebUI, nós acionamos um interceptador (`tiptap-markdown`) em cascata com a ramificação especializada de grides (`@tiptap/extension-table`). Com um design minimalista, renderizamos uma Planilha visual perfeitamente tratada estilo Notion (linhas zebradas, caixas redimensionáveis interativas, alinhamento absoluto), mas sem plotar nativamente a visão "Gráfico de Pizza". Apenas o registro puritanamente matricial. A UI foca na veracidade da trilha de auditoria.

Os "Gráficos de Força em 3D", renderizados separadamente (`CognitiveGraph.svelte`) pela Engine Svelte são encarregados unicamente do Mapeamento do Cérebro Neural (Agent Flow e Tokens) pra fins visuais administrativos.

---

## 8. Como funciona a Interceptação Nativa do Áudio Front-End?

Exatamente como uma extração Bare-Metal WebRTC (dispensando pacotes em nuvem super faturados). O Componente `MicrophoneButton.svelte` do painel se apodera da Interface do Operacional requisitando a licença `navigator.mediaDevices.getUserMedia()`. 

Para evitar IOPS drásticos em disco local, alocamos instâncias lógicas de Micro-Memória (`MediaRecorder.ondataavailable`), acumulando os blocos da fala. No final, nós zipamos o vetor dentro do contêiner empacotado (`audio/webm`) e despachamos pela rede em um *FormData*, enviando-o pro *Endpoint Back-End* nativo do Motor Rust (`api_multimodal.rs`). De lá, a chamada entra num pipeline Whisper (Transcritor de Voz local ou em Docker), que expele o texto traduzido de volta direto para o Input Principal (Markdown Editor). Pipeline 100% Nativo sem sair do ecossistema e com *Rate Limit Zero*.
