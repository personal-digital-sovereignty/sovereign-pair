# Protocolo de Interoperabilidade (API REST & MCP)

O Sovereign Pair foi projetado para expor seu motor de inferência central através de protocolos integrados. O sistema provê suporte unificado contemplando tanto a automação focada em Webhooks (via orquestradores como N8N), quanto desenvolvedores adotando extensões em ambientes locais baseados no padrão MCP.

## 1. A Interface REST (Integração HTTP via Axum O.S)

A infraestrutura compilatória principal em Rust Axum (`src-rust/main.rs`) expõe uma interface padrão para serviços. A implantação central pode ocorrer na nuvem (como a OCI) ou instanciada localmente de forma nativa.

Este modelo arquitetural permite que construtores visuais de fluxo e aplicações Web em `Vue.js` interajam nativamente com os endpoints síncronos da infraestrutura.

### 1.1 Roteamento e Endpoints Disponíveis
- `POST /v1/chat/completions`: EndPoint principal, padronizado com os Schemas JSON de Payload (como a matriz `messages: []`) estipulados na sintaxe de integrações padrão OpenAI. A rota engatilha o pipeline RAG (Retrieval-Augmented Generation) acionando consultas locais e prevendo retornos conversacionais. Possui lógica mitigatória acoplada para contornar instabilidades de pesquisa em bancos recém criados através do *Fallback Sistemático* que prioriza um fluxo unicamente voltado para Chat regular (ignorando pesquisa documental forçada).
- `GET /v1/projects`: Função responsável por listar e delimitar os diretórios físicos lidos no cofre do sistema (Sensus Vault). Retorna *Array* indexado de forma lógica facilitando segregação estrutural de projetos e a hierarquia base de clientes.
- `POST /v1/sys/stats`: Rota auxiliar passiva. Permite monitorar em *Real-Time* as condições brutas sistêmicas, exibindo telemetria da taxa de requisição, uso de memória (RAM e VRAM) e atividade geral do sistema operacional.

> [!WARNING]
> Consultas complexas em instâncias de CPU pura (desprovidas de NPU/Placa Gráfica dedicada) demandam uma margem extensa de resposta por vias HTTP. A latência inicial TTFB (Time To First Byte) apresentará comportamentos longos operando em nuvens gratuitas ARM64 (Node Cloud OCI). Deve-se configurar manualmente os parâmetros de latência no cliente orquestrador (e.g N8N / Frontend AXIOS), extendendo as restrições padrão de conexão (Timeouts HTTP) para janelas amplas entre 60 a 120 segundos. 

---

## 2. Padrão Integrativo MCP (Model Context Protocol)

Buscando padronizar integrações locais voltadas a desenvolvimento de software em VS Code (Cline, Cursor, etc), as rotinas da API nativa em **Rust** contam com um servidor compatível ao formato interativo do sistema **Model Context Protocol (MCP)**, apoiado pelo framework nativo open-source da Anthropic. Esse servidor extrai os processos regulares e os mapeia tecnicamente convertendo o Back-end em dependências passivas de "Tools" (Ferramentas) ou "Resources" (Conteúdo estático), operados via extensões do sistema operacional.

### 2.1 Rede via Stdio IPC (Comunicação Sem Portas TCP)
A implementação do MCP elimina a dependência de conexões abertas convencionais via TCP/HTTP no Desktop. Toda interação transacional adota o modo padrão *Stdio* (Standard Input/Output) efetuando leitura restrita mediante à via de comunicação inter-processos segura no sistema operacional nativo (IPC Node Kernel Routing). A abordagem elimina riscos associados ao monitoramento passivo LAN/WiFi O.S (Network Panning). **A declaração da via isolada encontra-se definida integralmente no binário local originário do gateway `src-rust/mcp_stdio.rs`]**.

### 2.2 Requisitos de Instanciação do Kernel no Client (Acoplamento a IDE VS Code)
O método de registro nas extensões assistentes impinge atrelamento puramente configuracional ativando chamadas no Rust local sem invocar sub-roteiros Python ou processos Docker externos à máquina do usuário:

Configuração e Registro:
```json
"mcpServers": {
  "sovereign-pair": {
    "command": "cargo",
    "args": ["run", "--release", "--bin", "sovereign-mcp-server"],
    "env": {
      "RUST_LOG": "info",
      "CARGO_MANIFEST_DIR": "/caminho/absoluto/da/raiz/do/projeto/sovereign-pair/"
    }
  }
}
```

### 2.3 Especificações Mapeadas via MCP (Módulos Tools e Resources)
Comunicação suportada providencia a liberação de chamadas para o assistente da IDE:
- **Tools (Comandos Preditivos Expostos):** Submódulos que habilitam o acionamento direto via requisições operacionais LLM base. Expõe funções restritas permitindo solicitações externas (`Search Query Executions`) às variáveis do Vector DB buscando extrações formatadas de regras do negócio e trechos cruciais originários dos manuais locais. (Habilitado nativamente marcadores estáticos de rotas como o decorator `@mcp.tool()`).
- **Resources (Mapeamentos do File System Systemático):** Disponibilizará ao cliente arquivos fundamentais isolados na estrutura física local sem exigir pesquisa interpretativa, oferecendo acesso passional constante de referências literárias ou logs sistêmicos (Via anotação limitador `@mcp.resource()`).

---

## 3. Topologia TUI do OpenCode Local (Proxy)

A implantação prevê rotinas e padrões restritivos baseados em Proxy local que convertem requisições originárias formatadas aos limites de nuvens públicas orientadoras de CLI Extensions (Apliacações TUI baseadas em Coder como OpenCode) redirecionando seus prompts diretamente ao modelo provido de forma local pela interface `Ollama` ou API base. 

### 3.1 Instanciação Operacional do Binário OpenCode
Configurações de infraestrutura Linux em que repousará as definições de Command Line local isoladas OpenCode API Component.

1. **Instalação Paramétrica Linux:**
   Obtenção através dos reposicionadores gerenciais da via `pacman` (para distros baseadas em Arch), fornecendo acesso rápido e simplificado à ferramenta.
   ```bash
   sudo pacman -S opencode
   ```

2. **Mapeamento Restrital de Integrações Locais Gateway (`opencode.json`):**
   Os espaços de trabalho (Workspaces) operantes serão submetidos às especificações exclusivas re-roteando o HTTP via URL Base nativa O.S Gateway:
   
   ```json
   {
       "$schema": "https://opencode.ai/config.json",
       "provider": {
           "sovereign-local": {
               "npm": "@ai-sdk/openai",
               "name": "Sovereign Root Interface Endpoint",
               "options": {
                   "baseURL": "http://localhost:8000/v1/opencode",
                   "apiKey": "sovereign-local"
               },
               "models": {
                   "qwen2.5-coder:7b": {
                       "name": "Local Fallback Fast Execution Execution Model Node Setup"
                   },
                   "coder": {
                       "name": "Remote Oracle Tunnels Computation OCI Engine Network Configuration"
                   }
               }
           }
       }
   }
   ```

### 3.2 Bypass Expresso via Linha de Comando O.S (CLI Variables)
Alternativamente, caso o desenvolvedor não deseje versionar arquivos estáticos `opencode.json` em repositórios corporativos visando *Zero-Trust* estrito, é perfeitamente viável "enganar" a engine TUI do OpenCode injetando o host Sovereign através de Variáveis de Ambiente O.S (Padrão OpenAI) diretamente no momento da chamada no terminal:

```bash
# Injeção Estrita de Proxy Base Native Local (OpenAI Bypass)
OPENAI_BASE_URL="http://localhost:8000/v1/opencode" OPENAI_API_KEY="sovereign-local" opencode
```
Essa invocação terminal suprime imediatamente as rotas da web nativas da extensão/CLI, encapsulando 100% da telemetria e fluxos Coder nas validações do Rust Axum Local.

### 3.3 Invocação Sistêmica no Ambiente (IDE Terminal)
Após rodar e indexar os servidores backend com Cargo Build / Axum Local na porta `8000`, engatilhará chamadas O.S em subterminal nativo (usando atalhos customizados *e.g., Ctrl+Esc* dentro da IDE ou Terminal). Isso estabelece um processamento de codificações restritas e exclusivas provindas do motor físico O.S Axum sob comando puramente local sem interagir arquiteturalmente com a Nuvem WAN API externa comercial O.S.
