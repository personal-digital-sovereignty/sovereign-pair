# Arquitetura e Filosofia do Sistema

## 1. Princípios de Arquitetura Local-First e Soberania de Dados

A arquitetura do **Sovereign Pair** foi projetada para mitigar a dependência de infraestruturas em nuvem de terceiros, garantindo o controle absoluto sobre o ciclo de vida dos dados gerenciados. Os princípios fundamentais do sistema são:

1. **Privacidade de Código e Dados:** O processamento ocorre primariamente em ambientes isolados, evitando o uso não intencional de dados de negócio para o treinamento de modelos fundacionais públicos.
2. **Processamento no Edge Computacional:** A infraestrutura é dimensionada para explorar a aceleração nativa de hardware local (GPU/CPU/NPU), habilitando a execução de Modelos de Linguagem Grande (LLMs) localmente.
3. **Padrão Zero-Trust:** As transferências de dados operacionais obrigatórias entre os nós de serviço trafegam exclusivamente via túneis criptografados em malha P2P (mTLS via Tailscale ou WireGuard), restringindo exposição à internet WAN.

O sistema é modular, orientado ao processamento multi-agente e integra-se diretamente ao File System local do Host, ambientes integrados de desenvolvimento (IDEs) e frameworks Open-Weight (como ecossistemas Llama 3 e Qwen).

> [!NOTE] 
> O código-fonte referente à topologia inicial de borda encontra-se mapeado pelas seguintes âncoras sistêmicas:
> ▫️ **Front-End PWA (Sensus Vault):** `web-ui/src/views/VaultView.vue`
> ▫️ **API Gateway (FastAPI):** `src/api/routes.py`

---

## 2. Topologia de Distribuição Híbrida

O framework adota um modelo de implantação de Rede Híbrida (ou *Cíbrida*), pulverizando e distribuindo a carga de tráfego computacional restritivamente.

*   **Nó de Borda (Host Edge / Workstation):** Estação de processamento restrito gerenciando as rotinas intensivas preditivas (via Daemon do `Ollama`) e assegurando os repositórios vetoriais. Detém toda responsabilidade nativa em cima de proteção, CRUD de diretórios e persistência de sessões vitais de segurança.
*   **Nó Auxiliar em Nuvem (Instância OCI):** Serviço instanciado na Oracle Cloud (Compute Node ARM64 Ampere) com o fim estrito de roteamento das interfaces auxiliares estáticas, workers desacoplados assíncronos e processamentos que fogem à jurisdição das camadas de persistência sensíveis do host físico, amortecendo picos de uso da infraestrutura central a custo zero atrelado.
*   **Camada de Rede Abstrata (VPN Mesh):** Transferência restrita via IPs Classe 100 reservadas (`100.x.x.x`) do ambiente cliente Tailscale, erradicando *Port Bindings* perigosos e firewalls externos desavisados.

> [!NOTE] 
> **Definições Arquiteturais Base:**
> *   **LLM (Large Language Model):** Aplicação e binário inferencial hospedados tipicamente na ferramenta `Ollama`.
> *   **RAG (Retrieval-Augmented Generation):** Técnica de extração lógica que alimenta prompts do Agente provendo uma formatação de contexto previamente apurada a partir dos Embeddings Físicos alocados antes da compilação e despacho real ao LLM em segundo plano.
> *   **Banco de Dados (Vector DB):** Abstração relacional otimizada na biblioteca `SQLite` local, substituindo lógicas não atracadas anteriormente aplicadas via ChromaDB, com total persistência do modo WAL (Write-Ahead Logging) na recuperação hiperdimensional paralela.

---

## 3. Orquestração de Micro-Agentes (MAS)

O código implementa de forma distribuída subsistemas ou "Micro-Agentes" modulares para evitar gargalos causados pela alucinação técnica dos modelos fundamentais globais (`Hallucinations` em janelas massivas de raciocínio).

1.  **The Mom / The Dad (Indexação e I/O):** Rotinas assíncronas em monitoramento ininterrupto sob o File System da máquina (`FileWatcher` acionados pelo SO Kernels via Rust). Processam a serialização de Chunks baseados em Markdown, extraem o Metadata respectivo, e injetam via Embedding no Sqlite Vectors com baixo I/O Cost.
2.  **The Sentinel (Filtro de Segurança Frontal):** Módulo restritivo responsável pelo escaneamento cru e rigoroso dos vetores ou requests em formato raw injetados nas pastas. Submete o prompt aos detectores focados em "Prompt Injections", inibindo contaminações executáveis antes da gravação indexada.
3.  **The Nurse (Triagem e Roteamento O.S):** Instância classificador semântica com finalidade exata de roteamento técnico. Categoriza a *intent* da *Request API*, descolando execuções focais entre código abstrato puro, manipulação de UI PWA isoladas ou buscas baseadas em documentações (RAG Search).
4.  **The Doctor (Inferência RAG Core via LangGraph):** Raciocínio profundo que efetua sub-steps lógicos processando interações da Knowledge Base provida matematicamente pela injeção vetorial RAG nas suas *memories local buffers*.
5.  **The Coder (Executor Sintático Programável):** Interface de resposta atrelada a predefinições unicamente puras a programação em frameworks específicos que devolvem avaliações sistêmicas puras (Bypass do contexto livre abstrato e RAG natural).
6.  **The Accountant (Auditoria Estrutural de Logs/Números):** Auditor lógico isolado focado no refinamento exato da precisão escalar que ataca defeitos genéricos presentes nos outputs primários de matemática não validados e de referencial cruzado providos por LLMs, gerando correções contábeis determinísticas aplicáveis antes do Payload HTTP Response.

> [!NOTE] 
> ▫️ **Espinha Dorsal dos Agentes:** `src/agent.py`
> ▫️ **Submódulos da Pipeline de Tarefas:** `src/core/the_*.py`

## 4. Particionamento Isolado Multi-Tenant O.S

O servidor backend FastApi detém provisões e arquiteturas preparadas que englobam a fragmentação segura perante cenários Múltiplos ou Corporativos escaláveis (Multi-Tenant RAG SaaS).

A engenharia contida no Retreiver impõe isolamento ao Vector Database por camada de UUID Metadata Keys atreladas na injeção da criação dos vetores textuais no SQlite, coíbindo vazamento de matriz em queries realizadas entre Contas/Client-Ids distintos processados simetricamente e simultaneamente nas bases de log. 

> [!WARNING]
> No estado trivial do sistema backend RAG, repositórios nativamente vazios dispararão quebras logísticas ou matrizes não passíveis de cálculo (ex: Status `"Empty Response"` do Retreiver do Node Engine submetido aos Nodes LlamaIndex). A fim de neutralizar travamentos para novos usuários implementa-se de forma sistemática nas sub-redes uma estrutura de *Fallback* apelidada de **Sovereign Bypass**, o qual intercepta Exceções de Listas Vazias e comuta a API RAG instantaneamente para uma API de Chat Genérica e Livre à Base Conversacional Base model.
