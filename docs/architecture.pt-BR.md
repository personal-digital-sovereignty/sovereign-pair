# Sovereign Pair - Arquitetura de Sistemas Híbridos (Cibrid)

**Versão da Topologia:** 3.3.0
**Classificação do Documento:** Engenharia & Operações de Infraestrutura (SRE)
**Foco:** RAG On-Premises, Node Orquestrador (OCI) e Redes Zero-Trust.

Este compêndio oficial detalha a planta topológica do Sovereign Pair. Destina-se a Arquitetos de Soluções e Engenheiros de Confiabilidade (*Site Reliability Engineers*) responsáveis por estender ou auditar a infraestrutura de Recuperação Aumentada por Conexão Semântica (RAG) em cenários de missão crítica.

---

## 1. Topologia Macro: O Paradigma Cibrid

A arquitetura transcende aplicações Node monolíticas, bifurcando-se em dois planos de execução simbiótica e independentes unificados por uma malha de rede definida por software (SDN). A camada de custo computacional denso atua sob premissa de *Intranet/Air-Gapped* (*On-Premises*), enquanto a resiliência e a orquestração de APIs rodam levemente em nós de Alta Disponibilidade em nuvem pública (Oracle OCI).

### 1.1 Plano de Inferência Densa (On-Premises / Deep Compute)
- **Local:** Workstations com Aceleradores Tensorizados Paralelos (GPUs Locais AMD/NVIDIA - Mín: 8GB VRAM).
- **Motores:**
  - **Ollama Daemon:** Motor de alocação de memória C++ nativa (Llama.cpp) residente na porta `11434`. Opera inteiramente Offline (Air-Gapped), isento de tráfego de egress para a internet.
  - **ChromaDB Vector Store:** Opera em protocolo *PersistentClient* utilizando a árvore física `data/chromadb` alvejando discos SSD/NVMe locais para gravações de Embeddings Paralelos Massivos. Lida com a base matriz das coleções semânticas densas sobrepondo custo zero de nuvem e zero trânsito exterior.

### 1.2 Plano de Coordenação e Orquestração (OCI Cloud Free Tier)
- **Local:** Cloud Pública Oracle (Node Compute A1 Flex - ARM64 / 24GB RAM).
- **Motores:**
  - **Microserviço RAG (FastAPI/Uvicorn):** App *Stateless* construído puramente com injeção de dependências Pydantic V2 atuando de Gatekeeper na comunicação entre frontends, motores analógicos (N8N) e a base de GPU local.
  - **Banco Transacional Efêmero (SQLite/PostgreSQL):** Aramzena apenas estado das sessões, relativas a prompts e chaves relacionais ao Vault local físico gerados na OCI.
  - **Frontend SPA (Vue3 Proxy):** Entregue através de Servidores Caddy/Nginx atuando unicamente em cache otimizado.

---

## 2. Padrões de Network e Segurança Criptográfica (Zero-Trust)

A integração entre os pólos *On-Premises* (inferência) e *Cloud* (orquestração/APIs) refuta o redirecionamento de portas sobre o protocolo TCP na internet pública (`0.0.0.0`), que violaria a lei das superfícies de ataque abertas.

### 2.1 Malha WireGuard Encriptada (Tailscale mTLS)
A cola arquitetônica entre o Node Cloud e a Workstation GPU é o subsistema IP virtual administrado pelo Tailscale. 
O tráfego trafega ponta a ponta criptografado (e2e) em invólucro UDP/Wireguard. 
Os aplicativos (FastAPI na Nuvem escutando a DB na Nuvem) e a GPU requisitada *On-Premises* "acham" estar hospedados na mesma subnet `100.x.x.x` LAN física, o que suprime completamente as sobrecargas cognitivas na elaboração de firewalls complexos e DMZs perigosas na cloud. Não há necessidade de reverso de IP Estático caro.

### 2.2 Controle de Tráfego API (Inbound/Outbound)
Qualquer tráfego extrínseco à malha que solicite comunicação (Ex: Um dispositivo Web do usuário) esbarra em *Rate Limiters*, regras transversais estritas de *CORS* (apenas domínios chancelados na *Allowed Origins*) e a verificação imperativa Bearer com Assinaturas baseadas em Segredo Operacional Forte.

---

## 3. O Padrão de Ingestão Híbrida Inteligente (RAG Pipeline)

Para neutralizar *Alucinações Críticas* e *Cegueira Temporal* (onde o LLM inventa bases ou ignora datas cruciais passadas nos chats), o motor abstém a técnica falha trivial de Simulação Cosseno isolada, implantando um padrão de Arquitetura de Busca Híbrida densificada.

### 3.1 O Roteamento de Pesquisa em Tempo Real
1. **Trigger de Consulta:** Ao cruzar as APIs RESTful e acionar o módulo `engine_builder`, o subsistema fragmenta a requisição do usuário.
2. **Avaliação Relacional Simultânea (TDD Otimizado):** Duas árvores de indexação separadas são varridas paralelamente pelas Threads.
   - O *Indexador Vetorial* (ChromaDB) traduz conceitos filosóficos e semânticos fluidos.
   - O *BM25 Custom Retriever* traduz rigor posicional (palavras cruas, UUIDs de log, números fiscais idênticos em relatórios).
3. **Fusão Estatística:** As pontuações conflitantes relativas aos mesmos documentos resgatados nas 2 instâncias passam por modelagem através do algoritmo de Rank Recíproco. Somente o Top-*K* mais qualificado (ajustado de ~15 para 5 nós por economia em cargas VRAM extremas) cruza vivo para a montagem de injeção dentro da "Janela de Contexto" atrelada ao fluxo vivo que desce pro LLM.

---

## 4. Orquestração Baseada em Pastas (Vault Session Storage)

Ao invés de adotar estruturas baseadas em Foreign Keys hiper-normalizadas (O que inflama falhas lógicas e de transações distribuídas assíncronas no SQLite), adotou-se o Design Patter "String Metadada Contextual".

Na tabela relacional do sistema `chat_sessions`, uma coluna solteira `folder_name` garante a categorização de projetos, chats e focos. Se for `null`, o nó habita a base geral. Isso converte o processamento da construção da Árvore Lógica Organizacional no Front-End Framework em algo computado na RAM dos nós dos navegadores na leitura de renderização da API, aliviando o estresse físico no banco local de ser taxado em Joins complexas e inúteis, preservando I/O rápido em tempo transacional micro.

---

## 5. Model Context Protocol (A Expansão Cognitiva IDE)

Para além de consumir a malha de RAG Cíbrida via Web UI, a topologia 3.3.0 adota o padrão **MCP (Model Context Protocol)** da Anthropic. Isso posiciona o Sovereign Pair como um módulo passivo de expansão de contexto para engenharia de software reversa.

### 5.1 Arquitetura Stdio (Standard I/O)
Clientes e agentes de codificação autônomos acoplados a IDEs (ex: OpenCode, Cline ou Cursor) invocam o binário `src/mcp_stdio.py`. O Sovereign Pair inicializa um loop de comunicação `JSON-RPC` via entrada e saída padrão (RAM/Socket Local).
- **Isolação Zero-Trust:** O Agente de IDE não realiza chamadas de rede externas ou escuta portas LAN;
- **Sensus Resources:** A base `VAULT_DIR` é espelhada nativamente para o IDE, instruindo IAs operárias (The Coder) sobre as regras de negócio escritas no Obsidian antes da submissão de código.
- **Tools Integradas:** O Agente local pode deflagrar pesquisas semânticas manuais no ChromaDB via Ferramenta `sensus_vault_search` sem violar o Sandbox corporativo.

---

**Glossário Técnico Referenciado:** Vide `docs/glossary.pt-BR.md`.
