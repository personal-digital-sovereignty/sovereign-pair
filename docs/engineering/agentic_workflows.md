# Roteiro Ocupacional: Padrões de Fluxo e Agentes (Agentic Workflows)

Este documento descreve os 9 padrões fundamentais aplicados de fluxos automatizados (Agentic Workflows) voltados à infraestrutura híbrida do **Sovereign Pair**, indicando papéis do sistema e topologia designada para o processamento correspondente de tarefas.

## Fases Estratégicas e Orquestração Preditiva

O roteiro evolutivo da base do Sovereign Pair tem como alvo preencher defasagens de orquestração linear (Routing) garantindo autonomia de ponta a ponta sem prejuízos em recursos locais processuais.

### Fase 1: Desacoplamento de Inferência e Eficiência Operacional
*Diretriz: Limitar excesso na contagem de inferência em tokens locais e mitigar chamadas consecutivas iterativas em CPU/GPU primária.*

1. **ReWOO (Reasoning without Observation)**
   - **Camada Física Designada:** Infraestrutura Local (Workstation C/C++ Engine).
   - **Justificativa Operacional:** Agentes que utilizam o padrão *ReAct* padrão incorrem em gastos expressos repetindo observação linear ao longo de passos de ferramentas. O ReWOO instaura planos integrais através de espaços alocativos interligados que preveem e executam paralelos sub-rotinas, poupando processamento excessivo via consultas fracionadas ao modelo base principal e mantendo a taxa limite sustentável em hardware restritivo local.
2. **Parallelization (LLM Aggregation)**
   - **Camada Física Designada:** Computação Distribuída (Nó Local + Serviço Oracle Cloud OCI).
   - **Justificativa Operacional:** Permite desfragmentar solicitações transacionais custosas dividindo arquivos primários grandes e executando fluxogramas de análise por intermédio sincrônico da rede VPN entre diferentes endpoints em malha.

### Fase 2: O Sistema Validador-Analítico
*Diretriz: Aperfeiçoar assertividade RAG contendo instâncias avaliadoras assíncronas de auditoria lógica.*

3. **Evaluator-Optimizer**
   - **Camada Física Designada:** Instância Restritiva Oracle Cloud OCI.
   - **Integração:** Adiciona-se processo assíncrono na Cloud (Avaliador) com objetivo de submeter retornos ao rigor comparativo documental originário do prompt RAG antes da devolução ao front HTTP. Tal modelo auxilia mitigando "alucinações" em contexto não local.
4. **Reflexion**
   - **Camada Física Designada:** Oracle Cloud OCI (Ambiente Sandboxed Isolado).
   - **Integração:** Garante instâncias onde *The Coder* consegue executar auto-correções operacionais de fluxos Python limitados pela IDE de programação. O processo capta saídas do ambiente shell, inspeciona e avalia seu retorno de falha, realizando consertos de código de automação isento da máquina física primária.

### Fase 3: Macro-Orquestração 
*Diretriz: Processamentos prolongados que independem da interface imediata.*

5. **Plan and Execute**
   - **Camada Física Designada:** Híbrido. O serviço em nuvem roteiriza fluxos e os executa de modo autônomo. Eficiente perante análise e formatação paralela de blocos amplos documentais PDF isolados O.S Base.
6. **Prompt Chaining**
   - **Camada Física Designada:** Híbrido. Criação de *pipelines* transacionais determinísticos utilizando *outputs* engessados via JSON limitando etapas para que a saída atue de imediato como modelo (Template Input) na função subsequente.

### Fase 4: Autonomia Terminal Integrada
*Diretriz: Ferramentas atreladas no Desktop.*

7. **Autonomous Workflow**
   - **Camada Física Designada:** Instanciamento unicamente local com *Sandboxing* rígido de ferramentas.
   - **Atenção:** Inclusões finais que concedem permissão processual via Mapeamento TUI ou sistema (Filesystem Manipulation). Requer o estrito emprego de *Policies Zero-Trust* e confirmação do programador isolada atada ao Model Context Protocol (MCP Extensions).

---

## Topologia Computacional (Diretrizes Arquiteturais)

### 1. Auditoria e Optimização Hospedada na OCI (Evaluator)
A implantação atesta a separação de papéis na qual instâncias *Ampere Node 24GB* hospedam agentes analíticos rápidos focados na validação (e.g., Llama-3 de dimensões reduzidas). 
**Fluxograma:** Enquanto o Workstation processa via Hardware NPU/GPU requisições pesadas referentes à criação dos documentos, ele submete rascunhos assíncronos a rede privada Cloud O.S. A verificação remota (Optimizer) analisa os resultados provados RAG com base do input inicial antes da autorização HTTP renderizando retorno mitigador e estático final perante o Client API. Evita-se, assim, gasto duplo da arquitetura base.

### 2. Segurança Híbrida em Sandboxing de Código Reflexivo
Configurar métodos *Reflexion* na base originária acarreta fragilização base local (Cofres Workstation OS Filesystem Risk), devido a *scripts Python* gerados pelo modelo. O isolamento operacional da rotina delega a testabilidade à Nuvem O.S (Através de instâncias Docker Container Efêmeras isoladas via N8N Gateway API Node Workers), que empacotam e submetem validação retornando o sintático da exceções contidas de volta ao Modelo Base para que as corrija mantendo infra local íntegra e não-exposta (Zero-Trust Logic Code Execution).

### 3. Atenuação de Limites Preditivos Locais via ReWOO
Para arquiteturas limitadas por VRAM ou barramentos locais LPDDR (Memory Buss Constraint), evita-se chamadas repetitivas via modelo cognitivo na base RAG Rota Padrão. O framework compõe um roteamento único, instanciando funções nativas simultaneamente isolando e gerando dados complementares, para só então recorrer à *LLM CPU Engine* final provendo coesão (Integração sem dependência em loop de consultas).
Esse desenho evita colapsos processuais causados em falhas por limite contextual originários nas repetições O.S Base (Ollama Loop Memory Faults).

### 4. Distribuição Relacional por Assimetria de Paralelização 
Múltiplas requisições simultâneas em inferenciadores locais como `Ollama` implicam disputas constantes por KV Cache allocation (Alocação em Memória Preditiva), gerando sobreposições originárias na VRAM O.S Framework Kernel. A infraestrutura adota a distribuição paralela simétrica, invocando o provedor GPU Local Node em demandas de menor variação estrutural (Temperature 0.1), delegando fluxos transacionais analíticos da rede OCI O.S Base via roteamento privado Tailscale HTTPS API, separando e evitando sobreposições de processo nas respostas locais e equilibrando escalonamento assíncrono nativo local de processadores menores.
