# Sovereign Pair - Sistema Avançado de RAG e Inteligência Artificial Soberana

**Sovereign Pair** é um sistema completo de Retrieval-Augmented Generation (RAG) em arquitetura desacoplada, focado em **alta performance, privacidade absoluta e segurança Zero-Trust**. Projetado para unificar inteligência local via modelos locais (Ollama) ou provedores em nuvem, o sistema se integra nativamente ao seu fluxo de trabalho através de uma API robusta e de um plugin nativo para Sensus Vault.

> [!TIP]
> **Quer ver o motor funcionando e ter aquele "brilho nos olhos"? 👀✨**
> Confira a nossa página de [Demonstração Visual e Showcase](docs/SHOWCASE.md) para ver a IA operando na prática com nossa Web UI!

---

## Visão Geral da Arquitetura

O sistema superou as iterações base e opera hoje como um **Córtex Mestre Tri-Core O.S**, sustentado nos seguintes pilares:

1. **Inteligência Local e Reflexiva (LLM)**
   - Execução 100% offline via **Ollama** gerenciado de forma implacável pela O.S., travando contextos na VRAM em tempo de compilação sem "Cold Boots".
   - Inferência RAG assisturada por **LangGraph** (StateGraphs) permitindo o sistema agir instintivamente com tags `<thinking>` e autocriticar antes de responder (Loop Agentic).

2. **Memória Atômica Cíbrida (SQLite Native)**
   - O absoleto banco ChromaDB e ineficiências transacionais do O.S. foram **extirpados**.
   - **sovereign_memory.db**: Única fonte da verdade O(1). O banco Sqlite O.S (`journal_mode=WAL`) gerencia histórico de chat, quadros Kanban e a infraestrutura Vetorial, alcançando escrita atômica instantânea dos textos no SSD local.

3. **Backend RAG (Sovereign Core - Rust & Python)**
   - O.S Tri-Core Engine construído em **Rust (Axum + Tokio)** entregando milissegundos de latência em leitura de diretórios O.S, gestão Kanban e roteamento LLM.
   - Suporte nativo ao **Server-Sent Events (SSE)** em tempo asíncrono e extração de telemetria precisa cravando o uso de CPU e Custos Ocultos por Token.

4. **Omni-Dashboard O.S (God Mode Cockpit Vue JS)**
   - A Interface Web PWA evoluiu para uma central de Guerra Panorâmica de Múltiplos Painéis (Tri-Core Tracker O.S), substituindo de forma integral quaisquer antigos "plugins de terceiros". Aqui, os logs de Kernel, Monitoria de Recursos (VRAM/RAM) e gerenciamento dos drives virtuais se fundem numa obra de design Wide-screen O.S extrema.

5. **A Ciber-Malha de Interligação Mesh (Oracle OCI)**
   - Servidor Local atua também de forma assimétrica acoplado ao servidor autônomo na infraestrutura Cloud. O **MeshSyncWorker** e o "The Blue Collar" mineram PDFs internet afora de forma autônoma 24/7 na Oracle e os disparam para o RAG DOMESTICO assíncronamente.

---

## Funcionalidades Principais

### Busca Híbrida Avançada (Hybrid Search v2.1.0)
A precisão mestre do motor: combina **Busca Vetorial Densa** (sentido semântico) com **BM25 Retrieval** (palavras-chave exatas e datas) através de uma fusão algorítmica (_Reciprocal Rank Fusion_), elevando a fidelidade da Recuperação de Documentos.

### Memória Conversacional Persistente
Ao contrário de implementações RAG estáticas, o agente lembra quem você é e sobre o que debateram na mesma sessão. O histórico do chat flui automaticamente de e para o banco de dados SQL e realimenta o buffer de contexto da Inteligência Artificial.

### Ingestão Incremental Extrema (Zero-Cost Sync)
Ao alimentar milhares de notas no sistema, a pipeline apenas processa deltas (arquivos novos, alterados ou removidos). Utiliza **Hashing Paralelo SHA256** (cache LRU) para alcançar 95%+ de redução no tempo processual, incluindo "Garbage Collection" automático das matrizes vetoriais obsoletas e suporte vitalício ao Server MCP.

### MAS (Multi-Agent System) LangGraph & Rust Core
Nossa cadeia intelectiva suporta LangGraph Agents com padronização global de nomenclatura: **The Mom**, **The Dad** (Orquestração), **The Nurse** (Triagem Semântica/Roteamento via LangGraph StateGraphs), **The Doctor** (Raciocínio RAG Avançado), **The Coder** (Engenharia Mestre) e **The Accountant** (Motor Matemático). Eles operam de forma isolada e em uníssono encapsulando de ponta-a-ponta a resiliência cognitiva da IA.
A partir da **v2.0**, os agentes de infraestrutura pesada (**The Mom** e **The Dad**) foram migrados para um **Sovereign Core nativo em Rust** (com ciber-paralelismo `Rayon` e `notify` de OSKernel), entregando latência quase nula na ingestão multithread e extirpando de vez os gargalos de Python e ChromaDB, agora centralizados em `sqlite-vec` atômico.

### Oracle "Blue Collar" & Mesh Tunneling
O Sovereign V2 possui uma inteligência descentralizada. Um módulo de Extração Nuvem (O Trabalhador Braçal) varre automaticamente a web por tópicos e mastiga o conhecimento na sua instância OCI A1 (Oracle). No Edge (Sua Máquina/Local), o **MeshSyncWorker** atua como cron-job assíncrono via VPN, clonando incrementalmente os vetores da Nuvem para o seu HD. O nó local absorve passivamente a experiência do seu clone na rede!

### O Mandato "The Sentinel" & Zero-Trust
O sistema opera através de controle restritivo militar. Requisições HTTP limitadas por preflights de CORS e Web Application Firewall. O **The Sentinel** intercepta Prompt Injections em T0 (Tempo Zero), quarentena vetores maliciosos e monitora o God Mode Cockpit. Na CI/CD, o sistema FOSS DevSecOps é mandatório.

---

## Instalação e Requisitos

### Pré-Requisitos
- Python 3.10+
- Node.js 18+ (Para compilar o Plugin do Sensus Vault / Interface Web)
- Ollama instalado e em execução (se desejar inferência 100% local)

### Setup Básico

1. **Clonar e Preparar o Ambiente**

> **Aviso de Implantação Cloud (Oracle OCI / Servidores Linux):**  
> Para ambientes de produção ou servidores remotos virtuais, a arquitetura padronizada (usada pelos scripts de CI/CD e Cloud-Init) exige que o sistema seja clonado e implantado estritamente no diretório **`/opt/sovereign-pair/`**.

**Para Servidores Linux (Produção):**
```bash
cd /opt
sudo git clone https://github.com/Personal-Digital-Sovereignty/sovereign-pair.git
cd /opt/sovereign-pair
```

**Para Desktops Locais (Desenvolvimento):**
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

### Topologias de Implantação (Cenários Cíbridos)
O Sovereign Pair evoluiu para uma infraestrutura Multi-Topológica, dividindo-se baseando-se no que roda Localmente *versus* Nuvem:

**Cenário 1: The Cloud Citadel (100% Servidor OCI)**  
Tudo centralizado no Oracle (Tailscale, Ollama, SQLite, Mesh Tunneling).
```bash
docker compose up -d --build
```

**Cenário 2: The Offline Bunker (100% Local / Desktop)**  
Roda absolutamente **tudo** localmente na sua máquina física, englobando a carga de processamento das GPUs e CPUS via motor Rust.
```bash
docker compose -f docker-compose.local.yml up -d --build
```

---

## Mapeamento de Diretórios Principais

- `src/` - Núcleo Funcional (Engine RAG, Retriever, Processadores, Utilities em Python).
- `src/api/` - Controladores, Rotas FastAPI, Middlewares, Tokens e Modelos de Banco de Dados SQLite.
- `docs/` - Acondiciona os **6 Tratados/Manifestos Mestres** explicando minuciosamente o ecossistema, todos fornecidos em versões nativas unificadas (`.en-US.md` e `.pt-BR.md`).
- `data/` - Repositório da Inteligência (Vault Cru, Banco de Dados Chroma DB Vetorial e Banco Relacional memory.db).
- `sensusvault-plugin/` - Código fonte TypeScript da Interface Nativa do Sensus Vault.

Para um detalhamento microscópico de como cada classe, banco ou servidor operam, dedique a leitura ao manifesto inaugural de arquitetura: **[01_architecture_and_philosophy](docs/01_architecture_and_philosophy.pt-BR.md)**.

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