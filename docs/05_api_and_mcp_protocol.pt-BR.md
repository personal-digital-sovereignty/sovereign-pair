# Protocolo de Interoperabilidade (API REST & MCP)

O projeto Sovereign Pair foi concebido para exportar o motor de inferência central através de protocolos integrativos. O sistema atende tanto ambientes orientados a Webhooks (Edge Networks / N8N) quanto desenvolvedores buscando extensibilidade nativa de IDEs.

## 1. A Interface RESTful Clássica (Integração N8N & HTTP)

A interface de entrada contínua baseia-se na aplicação FastAPI (`src/api/routes.py`), provisionada preferencialmente no Nó Orquestrador ou Computacional Cloud (Ex: Oracle OCI). 

Ela fornece endpoints síncronos HTTP desenvolvidos para atender ao roteamento estático. Este é o método padrão arquitetural para instanciar as requisições RAG e de inferência a construtores de Fluxo Visual como `N8N`, `Make` ou aplicações construídas sobre PWA/SPA em `Vue.js`.

### 1.1 As Rotas Primárias de Acesso
- `POST /v1/chat/completions`: EndPoint motor central da aplicação. Estruturado para aceitar os mesmos Schemas de Payload (`messages: []`) contidos na API da OpenAI. Esta rota dispara o pipeline de **RAG Matemático Híbrido** e invoca o Bypass de Prevenção a Retornos Vazios, mitigando interrupções sistêmicas quando o banco histórico ou índice vetorial (`SQLite`) encontrar-se desprovido de metadados durante as inicializações iniciais (Day-0).
- `GET /v1/projects`: Função encarregada do escaneamento unidirecional do sistema de diretórios físicos baseados na pasta (`Sensus Vault`). Retorna o objeto JSON *Array* provendo a segregação passiva por Projetos, atuando como marcadores lógicos e isolantes para o sistema de suporte a *Tenants* Multi-Clientes.
- `POST /v1/sys/stats`: Endpoint reservado para retorno passivo em tempo real extraindo o diagnóstico cru sistêmico do Kernel OS (Telemetria do uso base em memória VRAM/RAM associada e diagnósticos das instâncias de inferência), parametrizando medições de viabilidade e Uptime nativo das instâncias da infraestrutura.

> [!WARNING]
> Ao instanciar e escalar *requests* de inferência pesadas (contextos locais massivos que exijam validação matemática em processadores desprovidos de NPU/CUDA operando via tunelamentos P2P Node), a latência do TTFB (Time To First Byte) não operará no baixo espectro contínuo obtido em arquiteturas Cloud OpenAI. Webhooks acionados sob processos síncronos N8N podem gerar restrições por Timeout HTTP prematuro perante ciclos processuais extrapolando 60 a 120 segundos. Impõe-se configuração forçada dilatando o limite de tempo estrito da transação HTTP no nó de request integrador para prevenir falsos registros de *Drop HTTP/Timeout*. 

> [!NOTE] 
> ▫️ **Roteamento REST (Routes Core Base):** `src/api/routes.py`
> ▫️ **Entrada Operacional Padrão:** `src/api/main.py`
> ▫️ **Consumo Web Frontend:** Direcionado às requisições do escopo da camada `src/ui/` no framework nativo.

---

## 2. Padrão Integrativo Base Contexto Nativo (MCP Protocol)

Em otimização técnica perante as abstrações implementadas originalmente baseadas em nós estáticos complexos, refatorou-se as transações em Python habilitando a arquitetura inter-agentes a operar suportando nativamente as especificações de comunicação provindas do padrão industrial aberto **Model Context Protocol (MCP)** chanceladas nativamente na biblioteca da Anthropic. Esta funcionalidade converte a API nativa da aplicação (Base de Toolkits Contextuais e Componentes de busca) transmutando o *Back-End RAG* em instâncias parametrizadas de um Servidor de Dependência passivo atrelável nativamente (Plugins) interagindo diretamente em IDEs modernas do ambiente Desktop corporativo (Vs Code suportado à extensores Cline/OpenCode, Cursor). 

### 2.1 Isolamento Direto Computacional (IPC Stdio) Segurado Ponto a Ponto
Em contraste analítico e mitigatório de vulnerabilidades relativas a APIs convencionais em transferências públicas internet orientadas via WAN/TCP, e suas exposições intrínsecas correlatas à interceptações passivas por portas livres HTTP via sniffing O.S System. A abstração construtiva MCP Protocol roda no fluxo físico instanciando tráfego lógico através da infraestrutura **Stdio** (Standard Input/Output) operando as requisições puras via Comunicação Interprocessos nativas no Kernel OS Base (IPC Process). Desta forma o cliente construtor cria sockets lógicos isolando tráfego de memória de software entre as interfaces restritivas do Editor de Texto VS e as bases Python da Engine Vectorial sob isolamentos computacionais totais *Zero Trust environment*, extirpando rastro processual transacionável roteável atestado nativo sob o escopo rede O.S Linux/Windows. **[Diretriz Isolamento Baseado Stdio OS IPC Kernel Routing Mapeado no Backend nativo através de instâncias lógicas operativas declaradas sob arquivo `src/mcp_stdio.py`]**

### 2.2 Procedimento Padrão para Injeção Client IDE Extensibilities (Acoplamento Vs Code Process Engine)
O carregamento lógico processual em instâncias base de dependências do RAG Framework (Sovereign Pair Toolkit System Extension Tool Base Search Engine Functions e System Resources Integrations) encapsulados integrando base Workflows analíticos dentro de um VS Code configurado pela Base Cline Fork/Models Requirements:

Em parametrização via O.S JSON instancie os construtores O.S Puros da linha de processamento terminal originados do O.S Host nativo:

```json
"mcpServers": {
  "sovereign-pair": {
    "command": "python",
    "args": ["-m", "src.mcp_stdio"],
    "env": {
      "PYTHONPATH": "/caminho/absoluto/da/raiz/do/projeto/sovereign-pair/"
    }
  }
}
```

### 2.3 Estruturação Exportada Nativo MCP Specification Model Interface Protocol Base (Ferramentas/Resource Node Types)
As transações validadas em Stdio daemon O.S Kernel engatilharão acessos de integração nativas exportadas puramente acoplando extensibilidade passiva direta na capacidade lógica de LLM Assistants vinculados em ambiente de edição código Desktop:
- **Exposições Funcionais Processuais Dinâmicas Abstract Types System (Tools):** Liberação instanciada restrita providencia acesso executivo chamando as engines de base isolada restrita. Delegando permissões do tipo invocação rotineira nativas para uso das extensivas de Client AIs sob VS Code extensões efetuarem *Vector DB Query Index Search Executions* restritivas buscando referencial O.S físico de negócios isoladas e restritas formatada provindo bases textuais Vault de validação RAG anterior predição em código. (Atestado mapeado nativamente através System Decorators Mappings Object Data `@mcp.tool()`)
- **Provimento Passivo Recurso Integrativo Dados Crús Fixados OS Path Hierarchy Base Models (Resources):** Extratificações englobadas recursivas puras de validações e leituras atreladas do escopo de pasta física root dir System /Vault Docs providenciando indexação do contexto sem intervenção e limitadas de isolamento a dados origens puros de base e semântica Markdown corporativo anterior à base O.S compilatória IDE Local. (Atestado nativamente através Model Declarative Node Mappings via Resource Types Object Data Decorator Base `@mcp.resource()`).

> [!NOTE] 
> ▫️ **Host IPC Python System Kernel Gateway File Config:** Rotinas englobadas processuais localizadas intrinsecamente formativa O.S nativa `src/mcp_stdio.py`
> ▫️ **Reference Environment Base Params Configuration Models JSON Objects List Mappings:** Mapeamentos instanciados similares aos requisitos base estruturais Cline Engine Core Model de interfaces UI extensions Visual Studio settings requirements JSON O.S definitions bases files (e.g. `cline_mcp_settings.json`).

---

## 3. Topologia TUI Operativa do Projeto OpenCode Local (Proxy O.S)

Adaptação paramétrica O.S que implementou nativamente suporte e vinculidade abstrata orientada proxy ao cliente externo terminal OpenCode TUI provendo roteamento passivo da IDE base direto a consumptibilidade O.S nativa REST Local Gateway OpenAI-Compatible O.S de interface de rede privada Cíbrida/Edge. Extirpanção restrita do processamento Cloud External AI Vendors nativamente limitando todo data-pipe sob Model Nodes instanciados no Ollama Local Runtime O.S.

### 3.1 Provisionamento Estático Binário e Instanciações
Instalação configuracional em OS Hosts do Command Unit de Roteamento Extensivo Proxy HTTP O.S Isolado Terminal OpenCode API Component Base.

1. **Host Client Binary Tool Installation Steps:**
   Instalabilidade paramétrica nativa linux de repositórios base O.S oficiais da base Arch / Similares do arquivo estático compilado nativamente.
   ```bash
   sudo pacman -S opencode
   ```
2. **Registro OS Client Package IDE Extensões VS Code UI Models:**
   Baixar módulo e integrar instâncias nativas extension O.S Market VS Code (Identificado pacote nativamente base de provider SST - OpenCode Package API). 
3. **Mapeamento Root Dir Isolate Provider Definitions JSON OS Mapping Proxy HTTP Gateway Configuration (`opencode.json`):**
   Mapear isolando a Workstation em subdiretórios restritivamente as workspaces instanciando os direcionamentos proxies puros nativos:
   
   ```json
   {
       "$schema": "https://opencode.ai/config.json",
       "provider": {
           "sovereign-local": {
               "npm": "@ai-sdk/openai",
               "name": "Sovereign Root System Node Proxy Local System Edge Endpoint Gateway Base Model",
               "options": {
                   "baseURL": "http://localhost:8000/v1/opencode",
                   "apiKey": "sovereign-local"
               },
               "models": {
                   "qwen2.5-coder:7b": {
                       "name": "Workstation Limit Execution Models Nodes Compute Inference Model Object Setup Configuration Parameters"
                   },
                   "coder": {
                       "name": "Host Oracle OS Oracle Base Processor Node Remote Cloud Oracle Instance Base Compute Cloud Edge Compute Model"
                   }
               }
           }
       }
   }
   ```
4. **Acionamento O.S TUI Shortcuts:**
   Possuindo instâncias validadoras em rotas FastAPI restritiva ouvindo conexões (Port O.S Nativa 8000 via System UVicorn Process HTTP/1.1), utiliza subterminal OS Shortcut acionando gatilho: `Ctrl+Esc`. Providencia interface sub-terminal integrativa, permitindo despejos unitários restritos OS Base isolados puramente nativos OS Interface Model.
