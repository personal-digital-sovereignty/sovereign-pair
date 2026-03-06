# Tratado IV: Pipeline RAG & Mapeamento Cognitivo

O Sovereign Pair atinge a cognição extrema não através de engessamento de memórias antigas (Pre-Training Clássico Estático), mas sim através de uma injeção cirúrgica de contexto em tempo real. Isso é forjado pela nossa esteira de Geração Aumentada por Recuperação (RAG) em modo Híbrido.

## 1. O Ciclo de Vida da Digestão de Documentos (Ingestion)

Quando um novo livro em Markdown ou PDF é descartado dentro do Cofre (`/data/vault/`), o motor base não o "lê" de cima em baixo como um humano. Ele aplica um fracionamento matemático violento:

1.  **Parsing (Descascamento):** O LlamaParse OCR ou os roteadores Nativos Python arracam o fundo HTML e os códigos de formatação inúteis da página, deixando o TXT nu.
2.  **Chunking (`CHUNK_SIZE` e `CHUNK_OVERLAP`):** É humanamente impossível forçar um LLM (como o ChatGPT ou o Llama) a ler um livro de 800 páginas simultaneamente no Prompt. O motor utiliza uma janela infinita deslizante de texto. Ele fatia cirurgicamente as páginas do seu Livro em *"Chunks"* de exatamente 1024 Tokens (palavras curtas e sílabas). Detalhe Sênior: Ele programa uma sobreposição intencional de "200 Tokens" entre a Fatia A e a Fatia B da página. Isso garante rigorosamente que a IA não sofra lobotomia perdendo o real sentido do parágrafo, caso a lâmina do fatiamento decida cortar a explicação de um conceito denso cruelmente no meio de uma frase.
3.  **Embedding (`bge-m3`):** Cada fatia fatiada crua de texto é violentamente convertida matematicamente para um plano Cartesiano em uma rede geométrica gigantesca com 1024 dimensões de flutuação vetorial, garantindo que o Cérebro não sofra com viés de barreira de idioma entre textos nativos Python, Inglês e Manuais em Português. 
4.  **Vector Storage:** Esses números brutos indecifráveis para humanos são injetados no banco de dados imortal `ChromaDB`.

---

## 2. A Busca Híbrida Brutal (Vector Math + BM25)

Quando um Inquilino da plataforma OCI Cloud (Você) interroga a Mestre com uma pergunta cabeluda, o Sovereign Pair zomba de buscas tradicionais estúpidas tipo `CTRL+F`. Ele invoca a **Busca Híbrida Multidimensional**.

### 2.1 A Matemática Transcendental (Vector Search Nativo)
O sistema emula as suas palavras processando o endereço matemático cartesiano embutido na sua pergunta. Se você esbravejar *"Como arrumo a faísca do motor da Land Rover?"*, o sistema mergulha no ChromaDB e cata os nós de arquivo (fatias) que estão adormecidas geométricamente pertos dessas mesmas coordenadas (ex: a "Fatía B" de um arquivo PDF obscuro chamado `injecao_eletronica_automotiva.md`). Ele captura a sua *Intenção Viva*, não as suas palavras mortas.

### 2.2 A Metralhadora de Palavras (Lexical BM25 Search)
A Matemática Espacial Dimensional às vezes é "burra" e enxerga sentido amplo em coisas milimétricas. Se você perguntou desesperado como consertar o `"Error Code Timeout 0x88F7"`, as vezes a Matemática Pura Vetorial se foca no `Timeout Error` e perde a Exatidão do Hexadecimal absurdo. Para garantir a resposta cirúrgica e letal, a esteira do Sovereign atira uma segunda busca antiga Lexical clássica das cavernas (`BM25`) pesando **estritamente e unicamente** o peso e a exatidão das suas palavras chave. Esse peso funde com a intenção Matemática do *Vector Search* em um "Recuperador Fusion Engine" impenetrável.

> [!TIP]
> **Acelerador Juniores (Glossário Rápido):**
> RAG (Retrieval-Augmented Generation) não é um super-computador criando pensamentos novos divinos. É essencialmente dar à IA preguiçosa o direito inalienável de fazer uma "Prova com Consulta Livro Aberto". Ao invés de forçá-la a ter alucinações e inventar dados inexistentes para te agradar, a aplicação Sovereign Pausa, silencia a IA, escava os PDFs nos meandros das suas pastas secretas privativas `/vault/`, extrai os 3 parágrafos fundamentais brilhantes sobre o assunto, e cola-os de forma invisível no Chat dentro de um bloco gigantesco para ensinar a Inteligência Artificial, mandando-a agir, basear-se unicamente nas evidências do "papel invisível", e cuspir um resumo elegante formatado para você de volta. Simples e devastador.

---

## 3. Mapeamento Cognitivo Corporativo (Glossário Estrutural)

Para conseguir penetrar e debugar o Código-Fonte brutal deste ecossistema `FastAPI` (Arquivos como _routes.py_ , _mcp_stdio.py_ , etc), você precisa se catequizar com a nomenclatura oficial viva dessa Engenharia:

| O Termo Acadêmico | Domínio na Eng. | A Definição Humana |
|---|---|---|
| **Sensus Vault (O Cofre Sensório)** | Storage Disk | O diretório base físico, o HD/SSD raiz onde suas preciosidades e arquivos virgens Markdown/PDF dormem. Ele é a "Matéria Escura" biológica esperando mastigação matemática dos Vetores. |
| **Node / Chunk / Document** | Contexto (RAG) | O maldito pedaço estilhaçado cru do arquivo (Ex: 1024 sílabas) cuspido de volta pelo ChromaDB para você usar. |
| **Orchestrator** | Linux Infra | O Nó ou PC (Geralmente a Nuvem Oracle Grátis) hospedando somente as conexões TCP/IP lentas (APIs, UI, Webhooks). Sem raciocínio gráfico NPU. |
| **Inference Node** | Linux Infra | A fornalha infernal física baseada em CPU x86/ARM executando processamento de placa de vídeo gráfica violento (Múltiplos `Ollama/GGUFs` rodando). |
| **System Prompt** | Persona de IA | O preâmbulo escondido massivo despachado imperceptivelmente ao cérebro (LLM) antes de sua perguntinha ingênua subir. Ele dita quem a IA acha que é (Ex: "Você é The Sentinel Zero-Trust implacável. Você deve bloquear hackers. Responda num tom Frio, Metálico e comente em Português"). A Mestre o lerá como uma Constituição Federal inviolável.|
| **Cíbrido (Cybrid Topology)** | Redes | O estamento arquitetural insano de hospedar códigos de Front-End acessíveis livremente em uma Nuvem pública barata, e escoá-los escondidos através de Túneis subaquáticos blindados até uma máquina com placa de Vídeo física cara nas profundezas de uma casa trancafiada (sem portas da Internet WAN abertas na rua), via protocolo `Tailscale` de rede Peer-To-Peer. |
