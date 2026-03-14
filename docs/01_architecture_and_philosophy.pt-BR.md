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
> ▫️ **API Gateway (FastAPI):** `src/api/routes.py`

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
6.  **The Accountant (Auditoria Estrutural de Dados):** Validador isolado focado no refinamento e cruzamento de dados numéricos para correção lógica de saídas fornecidas pelos LLMs primários antes do envio da resposta HTTP final.

> [!NOTE] 
> ▫️ **Agente Principal:** `src/agent.py`
> ▫️ **Módulos da Pipeline:** `src/core/the_*.py`

## 4. Isolamento Multi-Tenant

A API backend (FastAPI) possui suporte para operações escaláveis e corporativas em estrutura multi-inquilino (Multi-Tenant).

As buscas e alocações de vetores são divididas lógicas no SQLite através de chaves únicas (UUIDs) de metadados durante a criação dos chunks. Esse processo impede o cruzamento indevido de pesquisas entre usuários ou sessões clientes distintas.

> [!WARNING]
> Em implantações novas, bancos de dados vazios podem gerar falhas na recuperação de contexto (retornando o status "Empty Response" para os frameworks como o LlamaIndex). Para evitar interrupções sistêmicas nesses cenários, o sistema possui um fallback integrado (**Sovereign Bypass**), que intercepta essas respostas vazias e redireciona a requisição automaticamente para um fluxo de chat convencional sem validação de RAG preliminar.
