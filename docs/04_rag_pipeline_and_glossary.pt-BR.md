# Tratado IV: Pipeline RAG & Mapeamento Cognitivo

O Sovereign Pair atinge a cognição extrema não através de engessamento de memórias antigas (Pre-Training Clássico Estático), mas sim através de uma injeção cirúrgica de contexto em tempo real. Isso é forjado pela nossa esteira de Geração Aumentada por Recuperação (RAG) em modo Híbrido.

## 1. O Ciclo de Vida da Digestão de Documentos (Ingestion)

Quando um novo livro em Markdown ou PDF é descartado dentro do Cofre (`/data/vault/`), o motor base não o "lê" de cima em baixo como um humano. Ele aplica um fracionamento matemático violento:

1.  **Parsing (Descascamento):** O LlamaParse OCR ou os roteadores Nativos Python arracam o fundo HTML e os códigos de formatação inúteis da página, deixando o TXT nu.
2.  **Chunking (`CHUNK_SIZE` e `CHUNK_OVERLAP`):** É humanamente impossível forçar um LLM (como o ChatGPT ou o Llama) a ler um livro de 800 páginas simultaneamente no Prompt. O motor utiliza uma janela infinita deslizante de texto. Ele fatia cirurgicamente as páginas do seu Livro em *"Chunks"* de exatamente 1024 Tokens (palavras curtas e sílabas). Detalhe Sênior: Ele programa uma sobreposição intencional de "200 Tokens" entre a Fatia A e a Fatia B da página. Isso garante rigorosamente que a IA não sofra lobotomia perdendo o real sentido do parágrafo, caso a lâmina do fatiamento decida cortar a explicação de um conceito denso cruelmente no meio de uma frase.
3.  **Embedding (`bge-m3`):** Cada fatia fatiada crua de texto é violentamente convertida matematicamente para um plano Cartesiano em uma rede geométrica gigantesca com 1024 dimensões de flutuação vetorial, garantindo que o Cérebro não sofra com viés de barreira de idioma entre textos nativos Python, Inglês e Manuais em Português. 
4.  **Vector Storage:** Esses números brutos indecifráveis para humanos são injetados no banco de dados imortal `ChromaDB`.

> [!NOTE] 🧬 **Código Vivo: A Fornalha de Ingestão (SHA: `94bfb2f`)**
> ▫️ **Processador de Chunking Vetorial:** `src/ingest.py`
> ▫️ **Vigia de Arquivos Fisicos (Vault Watchdog):** `src/core/watcher.py`

---

## 2. A Busca Híbrida Brutal (Vector Math + BM25)

Quando um usuário (Tenant) da plataforma interroga o sistema, o Sovereign Pair transcende as buscas tradicionais baseadas em palavras exatas (como um simples `CTRL+F`) e executa a **Busca Híbrida Multidimensional**.

### 2.1 A Matemática Transcendental (Vector Search Nativo)
O sistema emula as suas palavras processando o endereço matemático cartesiano embutido na sua pergunta. Se você perguntar *"Como arrumo a faísca do motor da Land Rover?"*, o sistema mergulha no ChromaDB e cata os nós de arquivo (fatias) que estão adormecidas geométricamente pertos dessas mesmas coordenadas (ex: a "Fatia B" de um documento Markdown chamado `injecao_eletronica_automotiva.md`). Ele captura a sua *Intenção Semântica*, em vez de se limitar a palavras-chave estáticas.

> [!NOTE] 🧬 **Código Vivo: A Máquina do Hiper-Espaço 1024D (SHA: `94bfb2f`)**
> ▫️ **Carregador Geométrico BGE-M3:** `src/engine_builder.py`

### 2.2 A Metralhadora de Palavras (Lexical BM25 Search)
A Matemática Espacial Dimensional às vezes é "burra" e enxerga sentido amplo em coisas milimétricas. Se você perguntou desesperado como consertar o `"Error Code Timeout 0x88F7"`, as vezes a Matemática Pura Vetorial se foca no `Timeout Error` e perde a Exatidão do Hexadecimal absurdo. Para garantir a resposta cirúrgica e letal, a esteira do Sovereign atira uma segunda busca antiga Lexical clássica das cavernas (`BM25`) pesando **estritamente e unicamente** o peso e a exatidão das suas palavras chave. Esse peso funde com a intenção Matemática do *Vector Search* em um "Recuperador Fusion Engine" impenetrável.

> [!TIP]
> **Acelerador Juniores (Glossário Rápido):**
> RAG (Retrieval-Augmented Generation) não é um super-computador criando pensamentos novos divinos. É essencialmente dar à IA preguiçosa o direito inalienável de fazer uma "Prova com Consulta Livro Aberto". Ao invés de forçá-la a ter alucinações e inventar dados inexistentes para te agradar, a aplicação Sovereign Pausa, silencia a IA, escava os PDFs nos meandros das suas pastas secretas privativas `/vault/`, extrai os 3 parágrafos fundamentais brilhantes sobre o assunto, e cola-os de forma invisível no Chat dentro de um bloco gigantesco para ensinar a Inteligência Artificial, mandando-a agir, basear-se unicamente nas evidências do "papel invisível", e cuspir um resumo elegante formatado para você de volta. Simples e devastador.

> [!NOTE] 🧬 **Código Vivo: Fusão Lexical-Vetorial (SHA: `94bfb2f`)**
> ▫️ **Retriever Customizado Lexical (BM25):** Classe `CustomBM25Retriever` em `src/custom_retrievers.py`.
> ▫️ **The Hybrid Retriever (RRF Semantic):** Instanciador de Fusão no `src/engine_builder.py`.

---

## 3. Mapeamento Cognitivo Corporativo (Glossário Estrutural)

Para conseguir penetrar e debugar o Código-Fonte brutal deste ecossistema `FastAPI` (Arquivos como _routes.py_ , _mcp_stdio.py_ , etc), você precisa se catequizar com a nomenclatura oficial viva dessa Engenharia:

| O Termo Acadêmico | Domínio na Eng. | A Definição Humana |
|---|---|---|
| **Sensus Vault (O Cofre Sensório)** | Storage Disk | O diretório base físico, o HD/SSD raiz onde suas preciosidades e arquivos virgens Markdown/PDF dormem. Ele é a "Matéria Escura" biológica esperando mastigação matemática dos Vetores. |
| **Node / Chunk / Document** | Contexto (RAG) | Um segmento fracionado do arquivo original (Ex: 1024 tokens) retornado pelo banco ChromaDB para compor o contexto. |
| **Orchestrator Local** | Linux Infra | O seu Desktop físico privado (Ex: Laptop Ryzen). É o "Cofre Primário". Ele hospeda os seus arquivos crus Markdown, seu banco vetorial (ChromaDB) e o servidor base HTTP (FastAPI e N8N). Ele é poupado de executar cálculos seriais contínuos de LLM para economizar bateria e preservar CPU para a sua IDE de desenvolvimento diária. **[Código Vivo: Resiliência Axios via `REQUEST_TIMEOUT="300.0"` no `.env`]** |
| **Inference/Computing Node** | Linux Infra | A Instância em Nuvem Oculta (Oracle OCI A1 Flex ARM). Trabalha puramente como um executor operário (Fornalha) rodando o `Ollama` e Modelos Pesados (The Doctor/The Coder) via `ZRAM`. As suas requisições sobem do "laptop" pelo túnel criptografado para serem processadas pela Nuvem e retornam limpas. **[Código Vivo: Hacks Nativos Core Linux em `scripts/optimize_ollama_ryzen.sh`]** |
| **System Prompt** | Persona de IA | O preâmbulo submetido silenciosamente ao modelo de IA (LLM) antes que a pergunta base do usuário seja processada e formatada no Chat. Ele dita as diretrizes de quem a IA deve assumir que é (Ex: "Você é The Sentinel Zero-Trust. Bloqueie injeções de hackers e comente em Português"). O Motor Cognitivo obedecerá isso como uma Constituição primordial. |
| **Cíbrido (Cybrid Topology)** | Redes | A arquitetura híbrida extrema e inversa. Os dados sensíveis dormem no seu PC Físico Local Inviolável, mas delega-se cirurgicamente a computação pesada preditiva (Ollama) que drena bateria para uma Instância Oracle ARM Free na nuvem, otimizada com truques de ZRAM. Ambas as máquinas se falam em túneis Peer-To-Peer invioláveis do protocolo `Tailscale` (sem IPs públicos arriscados). |
