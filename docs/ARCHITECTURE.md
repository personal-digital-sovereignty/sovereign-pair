# Sovereign Pair RAG - Documentação Técnica e Arquitetural

Este documento serve como a **fórmula ultra-técnica e infraestrutural** do projeto `Sovereign Pair RAG`. Ele detalha a topologia completa do sistema, a separação de responsabilidades (Backend, Frontend, Plugin e Daemon), bem como os fluxos de dados essenciais que fazem a inteligência artificial interagir com o ambiente local do usuário de maneira soberana.

Seja para manutenções futuras, expansão de capacidades ou delegações de implantação (Deployment em Cloud/Remote), esta página servirá como a única "Fonte da Verdade".

---

## 1. Topologia Macro do Sistema

O projeto adota uma arquitetura em camadas **[Desacoplada]**, o que significa que as responsabilidades de Banco de Dados, Processamento de IA, Interface de Usuário e Coleta de Notas estão estritamente separadas por via de APIs e Interfaces locais (REST e SSE).

### 1.1 Diagrama de Componentes

1. **Inteligência Artificial (LLM & Embeddings)**
   - Provida nativamente pelo **Ollama** (rodando localmente via daemon próprio do Ollama em `http://127.0.0.1:11434`).
   - Abstrações suportadas via `LlamaIndex` para outros provedores via Nuvem (`OpenAI`, `Anthropic`, `Groq`, `Gemini`).

2. **Banco de Dados (Vectorial & Relacional)**
   - **ChromaDB (Vector Database):** Opera em modo `PersistentClient` lendo e gravando matrizes vetoriais ricas (.sqlite3 interno e parquet) localizados fisicamente em `data/chromadb`.
   - **SQLite (Database Relacional):** Operado pelo `SQLAlchemy` (ORM), armazenado fisicamente em `data/sqlite.db`. É a fonte de verdade para metadados de sistema, Cache de Documentos, Configurações de LLM e Histórico Conversacional.

3. **Backend RAG (Servidor de Contexto)**
   - Uma API construída em **FastAPI** rodando via **Uvicorn** na porta `8000`.
   - Contém a "pipeline" completa de Geração Aumentada por Recuperação (RAG). Lê do banco vetorial, fala com o LLM e devolve aos clientes (UI e Obsdian).

4. **Clientes (UI)**
   - **App Vue 3 (Web UI):** Um aplicativo Reactivo rodando via `Vite` (porta `5173`), acessível via navegador. Dialoga com a API via Server-Sent Events (SSE).
   - **Plugin Obsidian (Integração Direta):** Uma extensão `.js` dentro do software Obsidian que extrai o contexto da anotação atual no editor e a injeta via REST para a API Backend.

5. **Daemon Observador (Auto-Sync)**
   - O `watcher.py` usa a biblioteca de sistema operacional `watchdog` para espionar a pasta `data/raw_docs/`.
   - Toda alteração em formato de texto nesta pasta aciona um processamento na surdina da pipeline no backend para vetorização.

---

## 2. Fluxo de Dados Funcional (Como as coisas conversam)

### A. Fluxo de Ingestão de Documentos (Upload & Indexação)
1. **Através da API (`routes.py` -> `POST /v1/upload`):** 
   - Recebe um binário/texto -> Lê o Hash (SHA256).
   - Verifica contra o SQLite se o hash é idempotente (ignora se sim).
   - Se o nome existe para outro hash: O sistema lida ativamente com a renomeação (adicionando trechos hachados) para não destruir vetores passados (`rename_if_exists=True`).
   - Dispara `src.ingest.process_single_file` via `asyncio.to_thread` na Background para não pendurar a API.
2. **Através do Watcher (`watcher.py`):**
   - Assiste modificações de arquivo no SO diretamente e invoca nativamente os chunks do LlamaIndex (via parser de Markdown `MarkdownNodeParser`) para o `ChromaDB`.
3. **No ChromaDB (`ChromaVectorStore`):** O texto é vetorizado pelo modelo de Embeddings (ex: `nomic-embed-text` ou `bge-m3`) configurado no Banco.
4. **No BM25 (`CustomBM25Retriever`):** Além dos vetores densos, os arquivos alimentam paralelamente o buscador probabilístico exato (Okapi BM25) para não perdermos relevância em termos cruciais.

### B. O Fluxo de Engenharia de Consulta (Chat & Inferência)
1. Usuário envia Requisição Opcionalmente com Conhecimento embutido (`message`, a flag `active_document` do Obsidian, etc.) para o `POST /v1/chat`.
2. A fábrica abstrata `engine_builder.build_chat_engine` é acionada:
   - Ela reidrata a "Memória do RAG" fazendo um SELECT no Relacional (SQLite) (`SELECT * FROM chat_messages WHERE session_id = ?`).
   - Habilita uma "Pesquisa Híbrida" unificando a Busca Vetorial Pura (LlamaIndex base) e o _Custom_ BM25 Index (_custom_retrievers.py_) via Rank Recíproco.
3. Se o Usuário inseriu Data Relativa (`/web hoje`), a engine de _Web Scraper_ é engatada interceptando respostas do *DuckDuckGo* via `BeautifulSoup`.
4. O *LLM Provider* mastiga o contexto consolidado e cospe uma resposta via `StreamingResponse` (tokens fragmentados usando a flag `data:` nativa de Server-Sent Events).

---

## 3. Respostas Técnicas a Eventuais Decisões de Deployment

Para garantir o futuro do software e a sua segurança arquitetural, detalhamos as resoluções vitais sobre migração baseadas na infraestrutura desenvolvida.

### P1: "E se eu enviar o servidor Ollama remotamente para a nuvem? O modelo de linguagem (LLM) baixado precisará estar no meu desktop ou no servidor remoto?"
**Resposta:** O modelo de linguagem (`llama3.2`, `bge-m3`, etc.) é inteiramente executado do lado onde a aplicação **Ollama** se encontra instalada como serviço (o servidor de inteligência bruta). Se você hospedar o Ollama remotamente, *a sua máquina local ("Desktop") não precisará baixar nenhum megabyte do modelo*, servindo apenas como uma "casca gráfica" e de "contexto".
- **Como a rede atuará?** No nosso código (`src/config.py`), o Backend em FastAPI buscará a `.env` variável `OLLAMA_BASE_URL` (hoje setada em `http://127.0.0.1:11434`). Para rodar em remoto, bastará alterar este valor para o seu IP servidor (ex: `http://192.168.1.50:11434`). A inteligência ocorrerá *Lá*, gastando a Placa de Vídeo (GPU) Remota, e devolvendo o texto rápido para seu backend FastAPI local processar e expor na UI!

### P2: "E se eu quiser remover o ChromaDB/SQLite da minha máquina ('Desktop') e rodar o Banco de Dados num Servidor à parte, como devo proceder? A arquitetura atual aguenta isso?"
**Resposta:** Absolutamente sim. A arquitetura foi construída 100% preparada para essa eventual escalabilidade horizontal.
O estágio atual do nosso app utiliza `PersistentClient` (no caso do Chroma) e `sqlite:///` (no caso do banco relacional) **somente** por fins de praticidade "Zero Config" e soberania ultra-fechada. Mas separar isso é plenamente suportado:

1. **Para migrar o Relacional (SQLite -> PostgreSQL na nuvem):**
   Sem tocar em nenhuma Tabela ou Classe! Devido ao nosso uso sólido do **SQLAlchemy** (um ORM Abstrato), as regras de banco são portáveis.
   *Ação:* Na pasta raiz (`.env`), você trocará a variável atual `DB_URL=sqlite:///data/sqlite.db` para a URL do seu servidor remoto:
   `DB_URL=postgresql://seu_usuario:sua_senha@ip_do_servidor:5432/sovereign_db`
   Ao reiniciar o Uvicorn (`FastAPI`), ele rodará o `models.Base.metadata.create_all(bind=engine)` construindo magicamente todas as tabelas (Sessões, Cache, Configurações) direto no banco externo.

2. **Para migrar o Vector DB (Local ChromaDB -> Remote Chroma/Qdrant/Pinecone):**
   Hoje instanciamos a interface nativa por pastas: `chromadb.PersistentClient(path="./data/chromadb")`.
   *Ação:* Você subirá um "Server Docker do Chroma" na sua VPS externa. Em seguida, no arquivo `src/config.py`, trocará:
   ```python
   # DE:
   chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
   # PARA:
   chroma_client = chromadb.HttpClient(host="MEU_IP_NA_NUVEM", port=8000)
   ```
   E toda a inferência de vetores e a memória dos Documentos acontecerá puramente via chamadas HTTP, deixando a sua máquina Desktop completamente livre e atuando como uma cliente esbelta do sistema de "Sovereign Pair"!

---

## 4. Práticas Futuras para Feature Requests

**Atenção Desenvolvedor:** A partir do commit assinalado na Data Base (`Fev/2026`), **qualquer nova Feature de UI, Backend ou Ingestão** deve obrigatoriamente ser sumarizada no índice `#2 Fluxo de Dados Funcional` deste documento.

1. Commits referentes à atualizações listadas aqui **devem** ser acompanhados de comentários detalhados descrevendo qual *Layer* da infraestrutura foi modificado. 
2. Testes Reais (*Pytest*) de escopo *Unitário* ou *Modular* devem obrigatoriamente passar na malha contínua do pipeline local antes da Fusão do Código (Merge).
