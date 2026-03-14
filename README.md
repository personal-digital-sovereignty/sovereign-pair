# Sovereign Pair

Sovereign Pair é um sistema de Retrieval-Augmented Generation (RAG) com arquitetura desacoplada, projetado com foco em alta performance, privacidade de dados e segurança Zero-Trust. O sistema suporta a execução de modelos de linguagem (LLMs) localmente (via Ollama) ou por meio de provedores em nuvem, sendo orquestrado por uma API RESTful e operado nativamente por sua própria interface Web PWA, batizada de Sensus Vault.

> **Demonstração Visual**
> Consulte a página de [Demonstração Visual e Showcase](docs/SHOWCASE.md) para exemplos de interface e operação do sistema.

---

## Visão Geral da Arquitetura

O sistema opera com base nos seguintes componentes principais:

1. **Inferência Local e Reflexiva (LLM)**
   - Execução local offline utilizando **Ollama** para gerenciamento de contexto alocado em VRAM.
   - Pipeline RAG implementada com **LangGraph** (StateGraphs), permitindo iterações reflexivas (tags `<thinking>`) e autocorreção durante a inferência.

2. **Persistência de Dados (SQLite)**
   - O banco de dados vetorial legado (ChromaDB) foi substituído de forma a priorizar velocidade transacional.
   - **sovereign_memory.db**: Banco SQLite configurado com `journal_mode=WAL`, responsável por gerenciar o histórico de conversas, quadros Kanban e embeddings vetoriais, proporcionando gravações atômicas e redução de latência no armazenamento local e indexação.

3. **Backend RAG (Rust & Python)**
   - Motor principal construído em **Rust (Axum + Tokio)** e **Python (FastAPI)**, otimizado para operações de baixa latência em leitura de sistemas de arquivos, gestão de estado (Kanban) e roteamento de requisições ao LLM.
   - Suporte a **Server-Sent Events (SSE)** para respostas assíncronas e telemetria estrita de uso de recursos (CPU, contagem de tokens).

4. **Dashboard Web (Vue.js)**
   - Interface Web (PWA) de painel único que centraliza logs do sistema, monitoramento de recursos (RAM/VRAM) e navegação interativa e controlada do repositório físico de documentos.

5. **Arquitetura Distribuída (Oracle OCI)**
   - O nó local sincroniza dados com instâncias em nuvem, quando acionado. O processo **MeshSyncWorker** realiza extração de dados de forma assíncrona em servidores na Oracle Cloud e atualiza os embeddings no repositório local de forma incremental, integrando a pesquisa web ao Vector Database sem prejudicar a CPU local.

---

## Funcionalidades Principais

### Busca Híbrida Avançada (Hybrid Search v2.1.0)
Combina **Busca Vetorial Densa** (aproximação semântica) com **Busca BM25** (correspondência exata de palavras-chave) utilizando o algoritmo *Reciprocal Rank Fusion*, otimizando a assertividade da filtragem antes da injeção de contexto.

### Memória Conversacional Persistente
A arquitetura RAG mantém o fluxo do estado conversacional salvando o histórico estruturado de interações no banco de dados e realimentando restritamente o "context memory buffer" do LLM em solicitações dinâmicas de conversas sequenciais.

### Sincronização Incremental 
A rotina de ingestão de arquivos processa unicamente os deltas diferenciais (arquivos criados, alterados ou sistematicamente deletados). Através de validação por **Hash SHA256** (cache LRU em memória), a recontagem estrita atinge drástica redução no custo computacional.

### Sistema Multi-Agente (LangGraph & Rust)
A orquestração cognitiva é delimitada através do encapsulamento de agentes modulares em workflows direcionados: **The Mom**, **The Dad** (Orquestração de Dados e I/O), **The Nurse** (Roteamento Semântico e Classificação de Requisições), **The Doctor** (Análise RAG, Prompt Engineering), **The Coder** (Validação e Geração de Lógica de Software) e **The Accountant** (Auditoria de Casos Extremos Multivariáveis). 
A alta escala de mapeamento físico e de paralelismo em embeddings foi nativamente reescrita em **Rust**, valendo-se das dependências computacionais `Rayon` (Multi-Threading de Kernel) e `notify` (File-Watcher OS).

### Segurança da Arquitetura (Zero-Trust)
O ambiente restringe severamente endpoints não autenticados via bloqueio originário de preflights (CORS) e Application-Level Middleware Control. Validações contra *Prompt Injections* mitigam que vetores de pesquisa retornem payloads executáveis na Dashboard do Sistema. O projeto garante verificações de CI/CD (SAST/DAST) nos merges e branches de infraestrutura.

---

## Instalação e Requisitos

### Pré-Requisitos Computacionais
- Sistema Linux / WSL2
- Python 3.10+
- Node.js 18+ (Para compilação dos Módulos Web e Plugin)
- Ollama runtime system (se for configurar como endpoint estritamente local)

### Procedimentos Básicos de Deploy

> **Aviso de Compatibilidade de Infra (Cloud-Init):**  
> Os metadados Terraform e as rotinas automatizadas de Continuous Deployment preveem explicitamente que a raiz da hospedagem esteja no diretório `/opt/sovereign-pair/`.

**Infraestrutura Linux (Nós de Produção):**
```bash
cd /opt
sudo git clone https://github.com/Personal-Digital-Sovereignty/sovereign-pair.git
cd sovereign-pair
```

**Workstations Isoladas (Desenvolvimento e Uso Pessoal):**
```bash
git clone https://github.com/Personal-Digital-Sovereignty/sovereign-pair.git
cd sovereign-pair
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Injeção de Variáveis .env**
Crie a estrutura declarativa copiando o arquivo fornecido pelo repositório:
```bash
cp .env.template .env
```
*(As propriedades técnicas `EMBED_MODEL`, `LLM_MODEL` e `CORS_ORIGINS` necessitam estar alinhadas à arquitetura planejada.)*

**3. Rotação de Credenciais de Segurança**
Estabeleça tokens JWT estáticos rodando o utilitário nativo via Python:
```bash
python scripts/setup_security.py
```

---

## Estratégias Operacionais de Deploy

### Cliente e Agente CLI Isolado
Para debugar rapidamente inferências assíncronas no seu Vector DB interno, o diretório disponibiliza uma abstração direta via shell O.S, dispensando instâncias REST ativas.
```bash
python src/cli.py chat
```

### Topologias de Implantação e Contêiner

**Cenário de Deploy Integral Web-Only (Cloud OCI)**  
Ambiente executado exclusivamente na Nuvem (API, Workers DAST, Ollama em rede isolada mTLS e SQLite persistido em Volumes Lógicos Cloud).
```bash
docker compose up -d --build
```

**Cenário Edge Computing Bare Metal (Nó Local)**  
Recurso voltado a Desktops potentes, transferindo 100% da carga operacional (Rust, RAG, Web GUI e GPUs físicas da máquina base) sob isolamento local.
```bash
docker compose -f docker-compose.local.yml up -d --build
```

---

## Mapas Arquiteturais dos Repositórios

- `src/` - Contratos técnicos de processamento modular, Retriever Vetorial e fluxos orquestrados em Python.
- `src/api/` - Entregas de Rota via FastAPI, Schemas do Pydantic, Integração de Sessões e Autenticação JWT.
- `docs/` - Acondiciona manifestos técnicos da construção da aplicação, incluindo design system e logs de refatoramento.
- `infra/` - Assets Terraform, dockerfiles otimizantes, shell-scripts e cloud-inits.
- `data/` - Volume compartilhado contendo dados primários e banco relacional masterizado (`sqlite-vec`).
- `web-ui/` - Camada VUE PWA para visualizações gerenciais.

Para detalhes arquiteturais microscópicos de serviços internos, indexe-se ao manual [Architecture Overview](docs/01_architecture_and_philosophy.pt-BR.md).

---

## Ciclos de Vida (Testes)

Integram o repositório nativamente testes sistêmicos e rotinas independentes via PyTest cobrindo Edge e End-to-End no roteador de RAG.

```bash
# Validar toda a bateria de Unit/Integration tests
python -m pytest tests/
```

---

## Licenciamento de Software

O código fonte restritivo encontra-se sob regimento validado da [**PolyForm Noncommercial License 1.0.0**](https://polyformproject.org/licenses/noncommercial/1.0.0).

- **Limites de Aplicação Não Comercial**: De uso garantidamente liberado sem pagamento para finalidades particulares, estudo algorítmico acadêmico, sem fins lucrativos ou topologia de laboratórios domésticos (HomeLabs isolados). O código e os seus dados processados localmente mantêm-se protegidos de invasão corporativa corporativa.
- **Implementação Comercial Restrita**: Nulamente permitido derivar o core vetorial e seu back-end, criar wrappers sob o fluxo, ou encapsular e alienar soluções pagas originárias ou parciais desta base para clientes B2C/B2B sem que obtenha-se documentada e assinada a vertente comercial de uma Autorização Proprietária do titular.

Para alinhamentos voltados a implantações empresariais de software robusto, acione corporativamente via: jefersonlopes@proton.me.