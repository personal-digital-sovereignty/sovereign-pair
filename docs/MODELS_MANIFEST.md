# Manifesto de Modelos e Arquitetura de Agentes (Sovereign Pair)

Este documento estabelece a taxonomia oficial para a escolha e uso dos modelos de linguagem (LLMs) dentro do sistema corporativo **Sovereign Pair v0.9.9+**. 

A plataforma não foca em um único modelo "faz-tudo". Em vez disso, ela segmenta os recursos através de um sistema multi-agente, onde modelos menores e especializados atuam em conjunto, minimizando custos computacionais e fornecendo resultados altamente precisos em ambientes locais (Edge Computing).

---

## 1. A Malha de Agentes Cognitivos (Processamento de Texto)

Para isolar responsabilidades no processamento do RAG (Geração Aumentada por Recuperação) e prevenir que alucinações afetem o texto final, a arquitetura Rust aciona dinamicamente os seguintes perfis especialistas:

### 1.1 Indexação e Banco Vetorial
*   **The Mom / The Dad (Monitores de Arquivo e Vetorizadores):**
    *   Sempre que os arquivos Markdown ou PDFs locais são modificados, esses agentes entram em cena.
    *   **Modelos de Embeddings Recomendados:** `nomic-embed-text:latest` (compacto e veloz) ou `bge-m3:latest` (ideal para indexação multilíngue de alta densidade). Transformam parágrafos de texto em coordenadas numéricas para o banco de dados `sqlite-vec`.

### 1.2 Triagem e Qualidade
*   **The Sentinel (Filtro de Ameaças):**
    *   Opera inspecionando nativamente a estrutura dos *prompts* e reações do banco antes de enviar para o gerador final. Funciona bem com modelos ultra-rápidos e leves, como o `qwen2.5:1.5b`.
*   **The Nurse (Roteador Semântico):**
    *   Classifica a intenção do usuário da interface. Ele decide se uma mensagem exige pesquisa no banco de dados, se é uma simples conversa trivial ou se necessita invocar componentes na tela.
    *   **Modelos Recomendados:** `smollm2:1.7b` ou `qwen2.5:1.5b`.

### 1.3 Inferência e Geração
*   **The Doctor (Motor de Resposta Base):**
    *   A "mente" por trás do fluxo conversacional principal. Trabalha unindo os blocos de texto trazidos pelos Rerankers (FastEmbed) para formular a conclusão.
    *   **Modelos de Alto Desempenho (Workstations > 16GB RAM):** `qwen2.5:14b` ou `llama3.1:8b`.
    *   **Modelos Moderados:** `phi4-mini` (excelente para dedução lógica estrutural) ou `deepseek-r1:1.5b` (ótimo para racionalizar passo a passo reduzindo erros prévios).
*   **The Coder (Extensão de Desenvolvimento):**
    *   Totalmente isolado do chat coloquial, atende de forma passiva através do Proxy OpenCode (`127.0.0.1:38001`) às solicitações de IDEs de mercado como o VS Code ou Cursor.
    *   **Modelo Recomendado:** `qwen2.5:7b-coder` ou `qwen2.5-coder:14b` (de acordo com a memória de hardware / GPU disponível).
*   **The Accountant (Auditoria Estrutural):**
    *   Garante que formatos de JSON exigidos por certas etapas ou tabelas cruzadas respeitem a integridade estrutural O.S sem predições errôneas.

---

## 2. A Camada Cíbrida (Nós Multimodais de Visão e Áudio)

Com a versão 0.9.9, o Sovereign Pair removeu bibliotecas complexas ligadas à compilação direta do Rust (como as antigas pontes `whisper-rs` em C++). Isso impedia problemas de desempenho e falhas de ambiente entre sistemas operacionais diferentes.

Para processar mídias, o sistema adota agora o modelo Cíbrido (Rust + Nodes independentes em Python):

### 2.1 O Modelo de "Despertar Efêmero"
Em vez de manter pesados processos de GPU carregados em repouso 100% do tempo, o motor Rust gerencia a infraestrutura. Quando tarefas multimídia são solicitadas (como por exemplo o upload de um extrato via UI ou um botão Svelte de gravação via microfone), o Rust invoca scripts independentes de linha de comando operados sob Python. Tais processos executam as suas bibliotecas nativamente em silêncio, devolvem o valor final calculado (texto transcrito/vetorizado), e se excluem da memória VRAM assim que o processo encerra.

### 2.2 Nós e Ferramentas Empregadas

1.  **Transcrição de Voz (Microfone Svelte):**
    *   **Nó Python Instalado:** `faster-whisper`
    *   **Modelo Base Utilizado:** `whisper-large-v3-turbo` (~800M parâmetros).
    *   Garante transcrições excelentes em Português-BR com latência quase em tempo real, sem a necessidade das antigas bibliotecas de C++ sobrepostas ao instalador do core do Rust.

2.  **Visão e Leitura de Imagens Gerais (VLM):**
    *   **Serviço:** Instanciado convencionalmente na GPU pelo daemon `Ollama`.
    *   **Modelo Tático Recomendado:** `gemma-3-4b`. Esse modelo possui um contexto avançado de análise utilizando o encoder *SigLIP*. É incrivelmente efetivo para classificar fotos ou extrair percepções visuais sem consumir toda a memória de vídeo de uma GPU convencional de desktop.

3.  **Processamento de Documentos de Texto Pesados (OCR Estrito):**
    *   **Nó Python Instalado:** `paddleocr` ou dependências relativas mantidas na subpasta `/nodes/`.
    *   **Utilidade Prática:** Sublinha extrema eficácia em quebrar layouts de tabelas e recibos fiscais. Onde as *LLMs* visuais convencionais (VLMs) começam a alucinar tentando "adivinhar" letras borradas, a extração autônoma do Paddle resolve a estrutura pura do texto com validação clássica antes de repassá-lo ao vetorizador SQLite.

4.  **Midi Trancoder Engine:**
    *   **Nó Python Embutido:** `basic-pitch` da Spotify API.
    *   Analisa frequências captadas remotamente da máquina, sem corromper memória alocada das funções conversacionais Rust da IDE do usuário.

 *(A presente taxonomia reflete a maturidade plena da versão 0.9.9+, orientada para ecossistemas sustentáveis, modulares e isentos de lock-in tecnológico em hardware oneroso).*
