# Sovereign Pair - Sistema Avançado de RAG e Inteligência Artificial Soberana

**Sovereign Pair** é um sistema completo de Retrieval-Augmented Generation (RAG) em arquitetura desacoplada, focado em **alta performance, privacidade absoluta e segurança Zero-Trust**. Projetado para unificar inteligência local via modelos locais (Ollama) ou provedores em nuvem, o sistema se integra nativamente ao seu fluxo de trabalho através de uma API robusta e de um plugin nativo para Obsidian.

> [!TIP]
> **Quer ver o motor funcionando e ter aquele "brilho nos olhos"? 👀✨**
> Confira a nossa página de [Demonstração Visual e Showcase](docs/SHOWCASE.md) para ver a IA operando na prática com nossa Web UI!

---

## Visa Geral da Arquitetura

O sistema superou a fase inicial de "Apenas Ingestão Incremental" e funciona hoje como um **Motor de Contexto** central, dividido em quatro grandes pilares:

1. **Inteligência e Processamento Base (LLM & Embeddings)**
   - Integração com **Ollama** para execução 100% local e offline na própria GPU/CPU.
   - Suporte transparente (via `LlamaIndex`) a provedores em nuvem (OpenAI, Anthropic, Gemini, Groq).
   - Embedding models locais (ex: `bge-m3`, `nomic-embed-text`) alimentando bases vetoriais.

2. **Memória Híbrida e Persistência de Dados**
   - **ChromaDB**: Banco de dados vetorial operando em arquitetura persistente local (`data/chromadb`).
   - **SQLite + SQLAlchemy**: Banco de dados relacional que mantém todo o histórico de conversas e estado da API (`data/sovereign_memory.db`).

3. **Backend RAG e Servidor de Contexto (FastAPI)**
   - Exposição via API RESTful com rotas de Upload, Ingestão e Chat.
   - Suporte a **Server-Sent Events (SSE)** nativo para respostas textuais em Streaming Real-Time.
   - Camada rígida de autenticação e proteção via **JWT (JSON Web Tokens)**.

4. **Clientes Integrados**
   - **Plugin Obsidian (Nativo)**: Interface ItemView inserida no menu lateral do Obsidian, que acopla a base de conhecimento (Vault) e o documento ativo diretamente à memória do RAG.
   - **Agente de Terminal (CLI)**: Uma rica e colorida interface de Prompt iterativa para testes e conversas rápidas na raiz do sistema.

---

## Funcionalidades Principais

### Busca Híbrida Avançada (Hybrid Search v2.1.0)
A precisão mestre do motor: combina **Busca Vetorial Densa** (sentido semântico) com **BM25 Retrieval** (palavras-chave exatas e datas) através de uma fusão algorítmica (_Reciprocal Rank Fusion_), elevando a fidelidade da Recuperação de Documentos.

### Memória Conversacional Persistente
Ao contrário de implementações RAG estáticas, o agente lembra quem você é e sobre o que debateram na mesma sessão. O histórico do chat flui automaticamente de e para o banco de dados SQL e realimenta o buffer de contexto da Inteligência Artificial.

### Ingestão Incremental Extrema
Ao alimentar milhares de notas no sistema, a pipeline apenas processa deltas (arquivos novos, alterados ou removidos). Utiliza **Hashing Paralelo SHA256** (cache LRU) para alcançar 95%+ de redução no tempo de processamento em comparação à indexações flat, incluindo "Garbage Collection" automático das matrizes vetoriais obsoletas.

### Segurança Zero-Trust
O sistema opera através de restrições por chaves (API Keys/JWT). Domínios de processamento são separados e requisições HTTP são limitadas por preflights de CORS definidos via manifesto estrito, blindando conexões indesejadas na rede local.

---

## Instalação e Requisitos

### Pré-Requisitos
- Python 3.10+
- Node.js 18+ (Para compilar o Plugin do Obsidian / Interface Web)
- Ollama instalado e em execução (se desejar inferência 100% local)

### Setup Básico

1. **Clonar e Preparar o Ambiente**
```bash
git clone https://github.com/Personal-Digital-Sovereignty/sovereign-pair.git
cd sovereign-pair
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Configuração Variáveis de Ambiente (.env)**
Crie a estrutura de variáveis clonando o template fornecido:
```bash
cp .env.template .env
```
_Note: Ajuste o seu `EMBED_MODEL`, `LLM_MODEL` e portas de CORS conforme necessário._

3. **Geração de Credenciais de Segurança**
Como a API tem arquitetura fechada por padrão, gere os tokens JWT do proprietário do sistema:
```bash
python scripts/setup_security.py
```
Esse script preencherá sua chave de administração JWT direto no `.env`.

---

## Uso Diário

### Agente Terminal (CLI)
Para testes ultrarrápidos e debug, invoque o Agente de linha de comando:
```bash
python src/agent.py
```
> O agente lerá os dados no seu vector db local, fará pesquisas web (caso o comando /web seja incluído no prompt) e interpelará seu sistema local.

### Subindo o Servidor de Contexto (Backend API)
A espinha dorsal para os clientes Front-End e Plugins.
```bash
# Inicia em ambiente FastAPI / Uvicorn (Porta 8000)
python src/api/main.py
```
_Documentação interativa das rotas acessível via **Swagger** em `http://localhost:8000/docs`_.

### Integrando o Obsidian (Plugin Nativo)
Sovereign Pair vem com um plugin em TypeScript embutido para o aplicativo Obsidian, criando uma Sidebar fixa nativa.
```bash
cd obsidian-plugin
npm install
npm run build
```
Copie a pasta compilada (`main.js`, `manifest.json`, `styles.css`) para o diretório `.obsidian/plugins/sovereign-pair/` no seu Vault. Habilite nas configurações do aplicativo. Você enviará mensagens à IA diretamente de dentro do Obsidian através da janela lateral, contextualizado na nota que você estiver escrevendo.

---

## Mapeamento de Diretórios Principais

- `src/` - Núcleo Funcional (Engine RAG, Retriever, Processadores, Utilities em Python).
- `src/api/` - Controladores, Rotas FastAPI, Middlewares, Tokens e Modelos de Banco de Dados SQLite.
- `docs/` - Manuais detalhados (`API.md`, `ARCHITECTURE.md`, `USER_GUIDE.md`).
- `data/` - Repositório da Inteligência (Vault Cru, Banco de Dados Chroma DB Vetorial e Banco Relacional memory.db).
- `obsidian-plugin/` - Código fonte TypeScript da Interface Nativa do Obsidian.

Para um detalhamento microscópico de como cada classe, banco ou servidor operam, dedique a leitura no manual [ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Testes Automatizados

O repositório abriga suítes completas de testes unitários e de estado End-to-End para garantir estabilidade da memória iterativa e persistência.

```bash
# Rodar testes incrementais em lote
python -m pytest tests/

# Validar sincronia de estado da Ingestão
python tests/validate_state.py
```

---

## Autoria

Sistema arquitetado, projetado e documentado por:
- **Jeferson Lopes**

---

## Licença

Este software e seu código-fonte subjacente são governados pela licença [**PolyForm Noncommercial License 1.0.0**](https://polyformproject.org/licenses/noncommercial/1.0.0).

**O que significa na prática?**
- **Soberano para a Comunidade Local**: Uso estritamente ilimitado para finalidades pessoais, acadêmicas, sem fins lucrativos ou implantação em seu próprio HomeLab privado. O controle do seu ambiente deve continuar pertencendo a você.
- **Vedado o Uso Comercial sem Pacto Prévio**: Fica estritamente proibido extrair capital, engatar esse módulo ativamente em pipelines de empresas (fintechs, e-commerces, soluções Saas) ou revender partes desmembradas deste repositório na forma de produtos B2B ou B2C sem aquisição de uma **Licença Proprietária Comercial**.

Para implantações co-corporativas ou se procura viabilidade de integração comercial e arquitetural do **Sovereign Pair**, envie correspondência comercial (jefersonlopes@proton.me). Todo o intelecto de orquestração vetorial, backend nativo e inteligência continuam sendo primazia legal do Autor.