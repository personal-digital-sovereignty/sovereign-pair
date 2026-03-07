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

3. **Backend RAG e Servidor de Contexto (FastAPI/MCP)**
   - Exposição via API RESTful de alta concorrência gerida por corrotinas assíncronas do LlamaIndex (`astream_chat`).
   - Servidor **MCP (Model Context Protocol)** embutido, convertendo o Sovereign Vault (ChromaDB + Markdown) em recursos nativos mapeados diretamente para sistemas HOST (como Claude Desktop e VSCode).
   - Suporte a **Server-Sent Events (SSE)** nativo para respostas textuais em Streaming Real-Time.
   - Segurança e autenticação rigorosa via **JWT (JSON Web Tokens)**.

4. **Trindade de Clientes Nativos**
   - **App Vue 3 (Web UI / God Mode Cockpit)**: Além da experiência PWA de IA, integra consoles de governança absoluta de IPs/UUIDs engaiolados, quarentena do Sentinel e Anti-Injeção.
   - **Plugin Obsidian 3.0**: Interface hiper-integrada oferecendo 3 visualizações (Mini-Web lateral, Minimalista focado no texto, e Spotlight Modal gigantesco para brainstormings).
   - **Agente Terminal (CLI)**: Uma das mais parrudas interfaces interativas de Terminal.

5. **Orquestração Cíbrida Zero-Cost (N8N OCI)**
   - Integração com o orquestrador N8N (Queue Mode) atrelado a banco Postgres.
   - Broker efêmero rápido via **Redis** hospedado no nível gratuito da Nuvem (Oracle A1 Flex OCPU).
   - Tunelamento estático 100% blindado por **Gatekeeper Cloudflare / Tailscale VPN**, isolando portas da internet pública.

6. **SecOps FOSS Enterprise (A Tríade de Defesa)**
   - **Gitleaks (Native Local Docker)**: Scanner militar bloqueando nativamente pushes com credenciais (pre-push hook).
   - **Semgrep SAST**: Análise estática avançada de código procurando bypasses, hardcoding e injeções no repositório.
   - **Zizmor & Trivy**: Auditoria de imagens OCI (Containers) e verificação extrema de permissões e segurança na esteira Github Actions.

---

## Funcionalidades Principais

### Busca Híbrida Avançada (Hybrid Search v2.1.0)
A precisão mestre do motor: combina **Busca Vetorial Densa** (sentido semântico) com **BM25 Retrieval** (palavras-chave exatas e datas) através de uma fusão algorítmica (_Reciprocal Rank Fusion_), elevando a fidelidade da Recuperação de Documentos.

### Memória Conversacional Persistente
Ao contrário de implementações RAG estáticas, o agente lembra quem você é e sobre o que debateram na mesma sessão. O histórico do chat flui automaticamente de e para o banco de dados SQL e realimenta o buffer de contexto da Inteligência Artificial.

### Ingestão Incremental Extrema (Zero-Cost Sync)
Ao alimentar milhares de notas no sistema, a pipeline apenas processa deltas (arquivos novos, alterados ou removidos). Utiliza **Hashing Paralelo SHA256** (cache LRU) para alcançar 95%+ de redução no tempo processual, incluindo "Garbage Collection" automático das matrizes vetoriais obsoletas e suporte vitalício ao Server MCP.

### MAS (Multi-Agent System) LangGraph
Nossa cadeia intelectiva já suporta LangGraph Agents: O Enfermeiro (Triagem de Sentimentos), O Doutor (Raciocínio Clínico de RAG) e O Programador (Execução Direta de Ferramentas), encapsulando de ponta-a-ponta a resiliência cognitiva da IA.

### O Mandato "The Sentinel" & Zero-Trust
O sistema opera através de controle restritivo militar. Requisições HTTP limitadas por preflights de CORS e Web Application Firewall. O **The Sentinel** intercepta Prompt Injections em T0 (Tempo Zero), quarentena vetores maliciosos e monitora o God Mode Cockpit. Na CI/CD, o sistema FOSS DevSecOps é mandatório.

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
Para testes ultrarrápidos e debug, invoque a CLI oficial do sistema. Ela herda suas configurações globais (Nome, Ocupação, Localização) e não depende do API estar de pé:
```bash
python src/cli.py chat
```
> O agente lerá os dados no seu vector db local, interagirá com o Ollama nativamente, e fará pesquisas web (através do comando /web).

### Subindo o Motor Central (Full Stack)
Se você deseja iniciar o Backend FastAPI e o Frontend Web juntos numa tacada só:
```bash
python src/cli.py start --full
```
_Também é possível subir apenas a infra de API usando `--server` ou apenas o Vue3 com `--web`._

### Integrando o Obsidian (Plugin Nativo)
Sovereign Pair vem com um plugin em TypeScript embutido para Obsidian, criando uma simbiose profunda com sua base de texto.
```bash
cd obsidian-plugin
npm install
npm run build
```
O Plugin empacotado reside em `.obsidian/plugins/sovereign-pair/` no seu Vault. Uma vez habilitado no Obsidian, você ganha o controle do histórico de pastas e o superpoder da injeção de contexto ativo diretamente pelo editor, sob as 3 filosofias visuais fornecidas pelo plugin.

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