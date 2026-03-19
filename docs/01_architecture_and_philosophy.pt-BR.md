# Arquitetura e Filosofia do Sistema

## 1. Princípios de Arquitetura Local-First e Soberania de Dados

A arquitetura do **Sovereign Pair** foi projetada para mitigar a dependência de infraestruturas em nuvem de terceiros, garantindo o controle sobre o ciclo de vida dos dados gerenciados. Os princípios fundamentais do sistema são:

1. **Privacidade de Código e Dados:** O processamento ocorre primariamente em ambientes isolados, evitando o envio de dados sensíveis de negócio para APIs de modelos de linguagem comerciais.
2. **Processamento Local (Edge Computing):** A infraestrutura é dimensionada para utilizar a aceleração de hardware local (GPU/CPU), viabilizando a execução de LLMs corporativos e assistentes diretamente na máquina do desenvolvedor.
3. **Padrão Zero-Trust:** A comunicação entre nós de serviço ocorre via túneis criptografados em malha (mTLS via Tailscale ou WireGuard), restringindo a exposição à internet pública.

O sistema possui design modular, orientado a agentes autônomos e integra-se diretamente ao sistema de arquivos local, ambientes integrados de desenvolvimento (IDEs) e frameworks Open-Weight (como Llama 3 e Qwen).

> [!NOTE] 
> O código-fonte referente a esta topologia encontra-se nos seguintes caminhos:
> ▫️ **Front-End PWA (Sensus Vault):** `web-ui/src/views/VaultView.vue`
> ▫️ **API Gateway (Axum):** `src/api/routes.py`

---

## 2. Topologia Híbrida

O framework adota um modelo de implantação de rede híbrida, distribuindo a carga de tráfego computacional de acordo com a capacidade do hardware.

*   **Nó Local (Workstation):** Estação de processamento gerenciando as rotinas preditivas principais (via serviço do `Ollama`) e os repositórios vetoriais. Centraliza a proteção, operações CRUD de diretórios e a persistência de sessões de segurança.
*   **Nó em Nuvem (Instância OCI):** Serviço instanciado na Oracle Cloud (Compute Node ARM64 Ampere) com o objetivo de rotear interfaces estáticas, workers assíncronos e processamentos não sensíveis, reduzindo a carga da infraestrutura central.
*   **Camada de Rede (VPN Mesh):** Comunicação em rede fechada utilizando IP na faixa `100.x.x.x` do Tailscale, dispensando o mapeamento de portas diretas e simplificando a configuração de firewalls locais.

> [!NOTE] 
> **Definições Arquiteturais Base:**
> *   **LLM (Large Language Model):** Aplicação para execução de modelos, usualmente hospedada via `Ollama`.
> *   **RAG (Retrieval-Augmented Generation):** Técnica de busca e recuperação que contextualiza o prompt do agente a partir de documentos locais antes do envio ao LLM.
> *   **Banco de Dados (Vector DB):** Armazenamento otimizado utilizando `SQLite` em modo WAL (Write-Ahead Logging), garantindo transações rápidas na recuperação de dados analíticos sem a necessidade de instâncias dedicadas como o ChromaDB.

---

## 3. Orquestração de Micro-Agentes (MAS)

O sistema implementa subsistemas ou agentes modulares para dividir tarefas e reduzir a probabilidade de respostas incorretas (alucinações) em contextos longos.

1.  **The Mom / The Dad (Indexação e I/O):** Rotinas assíncronas que monitoram o sistema de arquivos local (`FileWatcher` via Rust `notify`). Realizam a leitura de arquivos Markdown, extraem seus metadados e geram os embeddings no SQLite.
2.  **The Sentinel (Filtro de Segurança):** Módulo responsável por escanear as requisições antes do envio aos modelos, filtrando tentativas de injeção de prompt e prevenindo retornos não desejados na interface.
3.  **The Nurse (Triagem e Roteamento):** Classificador semântico que categoriza a intenção da requisição da API HTTP, direcionando-a para análise de código, manipulação da interface web ou fluxo RAG convencional.
4.  **The Doctor (Inferência RAG via LangGraph):** Analisador lógico que processa interações da base de conhecimento a partir dos resultados da busca vetorial em memória.
5.  **The Coder (Validador Sintático):** Interface focada unicamente na avaliação de sintaxe e frameworks de programação, operando de forma independente do contexto puramente conversacional.
6.  **The Accountant (Auditoria Estrutural de Dados):** Validador isolado focado no refinamento e cruzamento de dados numéricos para correção lógica de saídas fornecidas> ▫️ **Gateway Cíbrido (Rust Axum):** `src-rust/main.rs`
> ▫️ **Serviço de Arquivos Locais O.S (Rust Notify Protocol):** `src-rust/core/watcher.rs`
> ▫️ **Motor Analógico Vetorial O.S:** Integração direta via C/C++ `sqlite-vec` (Extensão nativa no SQLite RAG OS).
> ▫️ **Agentes da Pipeline O.S:** `src-rust/core/the_*.rs`

---

## 4. Isolamento Multi-Tenant

A API backend executada pelo Framework base estrutural C/C++/Rust (Axum + Tokio) provê o manuseamento corporativo de alto desempenho estruturado via recursos multi-inquilinos lógicos parametrizados.

As buscas e alocações transdicionais lógicas processuais ocorrem sob SQLite (usando a sub-arquitetura nativa C/C++ vinculada, `sqlite-vec`), nas quais chaves limitantes alocadas durante a indexação inicial restringem instâncias originativas garantindo que transições entre sessões ou inquilinos não transponham a isolação nativa processual local de leitura vetorial.

> [!WARNING]
> Histórico Evolutivo Arquitetural: Durante os primeiros estágios da aplicação (quando rodava ancorada em Rust e LlamaIndex/Axum), bases vazias causavam crashes devolvendo strings de falha "Empty Response". Tais retornos demandavam fluxos paralelos via código (Sovereign Bypass Rust). Após a reengenharia O.S e desenvolvimento de todo o RAG Mestre em **Rust/C++**, referidas defasagens processuais externas aos containers falharam perante isolações corporativas de rede (Data Leaks a terceiros da API LLM). A nova arquitetura RAG Cíbrida lidando iterativamente aos bytes brutos do O.S resolveu nativamente o direcionamento analítico LLM, eliminando do projeto as bibliotecas originárias e obsoletas.
