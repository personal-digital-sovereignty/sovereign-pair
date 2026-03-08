# Tratado V: Protocolo de Interoperabilidade (API & MCP)

O projeto Sovereign Pair foi concebido para expor o seu cérebro eletrônico central através de dois protocolos distintos e mortais. O sistema atende tanto a engenheiros de automação corporativos (Webhooks) quanto desenvolvedores de Software Raiz de IDE.

## 1. A API REST Clássica (Integração N8N & HTTP)

A porta de entrada primária da espinha dorsal é a aplicação FastAPI (`src/api/routes.py`), que geralmente roda no seu Orquestrador (A Nuvem Gratuita Oracle). 

Ela fornece "endpoints" síncronos e assíncronos pesadamente otimizados para Webhooks estáticos. Este é o **método oficial e preferido** quando você precisa espetar a Inteligência do Sovereign Pair em construtores de Fluxo Visual como `N8N`, `Make/Integromat` ou um Front-End desenhado em `Vue.js`.

### 1.1 As Rotas Críticas
- `POST /v1/chat/completions`: A Rota Primária e motor central cognitivo da aplicação. Ela aceita as mesmas estruturas de Payload (`messages: []`) que a API da OpenAI exige. Esta rota engatilha ativamente o **RAG Matemático Híbrido** e aplica o Bypass de "Empty Response" para impedir que o sistema trave em dias zero (o momento de instalação cru onde o banco vetorial ChromaDB ainda está técnica e fisicamente vazio, sem nenhum PDF para leitura).
- `GET /v1/projects`: Escaneia a estrutura dimensional do Cofre raiz (`Sensus Vault`) e devolve um JSON array mapeando os subdiretórios de Projetos, que funcionam como contêineres lógicos e inquebráveis para isolar Múltiplos Inquilinos (Tenants) separados.
- `POST /v1/sys/stats`: Consolida e reporta a telemetria física nua de hardware (consumo da placa de vídeo e RAM do Nó de Inferência no SO), atestando a robustez e o Uptime.

> [!WARNING]
> Devido às severas leis restritivas da física de se inferir modelos locais hiperpesados usando placas de redes Mesh P2P, a resposta da IA **NÃO será em milissegundos**. Chamadas Webhook convencionais disparadas pelo nó HTTP do N8N podem demorar aterrorizantes 3 minutos para receber a string inteira formatada. Modifique obrigatoriamente as configurações Timeout "Timeout Configuration" do seu N8N para sumariamente ignorar o clássico *Drop/Abortamento* padrão de 60 Segundos. 

> [!NOTE] 🧬 **Código Vivo: A Rota REST Completa (SHA: `94bfb2f`)**
> ▫️ **Controlador Core de Webhooks:** `src/api/routes.py`
> ▫️ **Inicializador da Aplicação:** `src/api/main.py`
> ▫️ **Dashboard Visão-Mestre (Vue.js):** Engrenado primariamente em `src/ui/`

---

## 2. A Integração do Contexto Nativo: Anthropic MCP

A arquitetura original baseada em LangGraph (que mantinha grafos complexos e inflexíveis presos à nuvem) foi substituída para expor nativamente as engrenagens de raciocínio profundo dos seus Agentes (*The Doctor*, *The Nurse*, *The Coder*) através do protocolo aberto **Model Context Protocol (MCP)** da Anthropic. O atrativo primário e de marketing dessa virada de chave é claro: Ao invés de isolar a inteligência no terminal da aplicação RAG, o ecossistema transforma o seu back-end inteiro num poderoso "Módulo de Expansão de Habilidades", que se acopla ativamente como um cordão umbilical inteligente nas IDEs corporativas mais modernas (VSCode, Cursor, projetos baseados no Cline, e nosso vindouro projeto próprio *OpenCode*).

### 2.1. Soberania Absoluta Cíbrida (Zero Internet Local-First)
Diferente das requisições via Internet com APIs Web REST convencionais que podem, eventualmente, vazar pacotes interceptáveis na rede via ataques de *Sniffing*, o esquema bruto de acoplamento do MCP corre debaixo do túnel local engatado exclusivamente por **Stdio** (Standard Input/Output) de Comunicação Inter-Processos (IPC). A sua IDE cria uma ponte cega de Soquete dentro da memória RAM local. O seu precioso código arquitetural corporativo **jamais pisará roteado num pacote de rede**. O ambiente torna-se Zero-Trust inviolável. **[Código Vivo: Camada IPC isolada em `src/mcp_stdio.py`]**

### 2.2. O Ritual de Acoplamento do Cliente IDE (OpenCode / VSCode)
Para injetar o Cofre do Sovereign Pair inteiro no seu fluxo de trabalho de programação (Ex: Um Visual Studio Code integrado via OpenCode), utilize a configuração do Assistente Inteligente (conhecido mundialmente como *Cline* ou seus *Forks* derivados). Basta ajustar o arquivo `cline_mcp_settings.json` local da máquina anexando:

```json
"mcpServers": {
  "sovereign-pair": {
    "command": "python",
    "args": ["-m", "src.mcp_stdio"],
    "env": {
      "PYTHONPATH": "/caminho/completo/absoluto/pro/sovereign-pair/"
    }
  }
}
```

### 2.3. Diferenças do Protocolo (Tools vs Resources)
Da exata contagem do momento que sua IDE liga as antenas de conexão com o `mcp_stdio.py`, ocorre uma fusão vital:
- **Ferramentas (Tools):** A IA rodando dentro da sua IDE ganha repentinamente superpoderes corporativos atrelados a funções programáveis em Python. Acionando a busca `sensus_vault_search`, o agente estúpido da IDE passa a escanear o banco vetorial do Sovereign ChromaDB no meio de uma tarefa CSS apenas para resgatar e consultar diretrizes de negócio vitais escondidas em um PDF de Requisitos. **[Código Vivo: Tool `@mcp.tool()` exportada]**
- **Recursos (Resources):** A IA acoplada ganha capacidade autônoma passiva e assombrosa para ler os subdiretórios blindados de Projetos do seu HD `Sensus Vault` e se enraízar com a filosofia do seu negócio ANTES de tentar gerar códigos genéricos pautados em alucinações enviesadas de plataformas SaaS externas da gringa. **[Código Vivo: Passiva Operacional `@mcp.resource()`]**

> [!TIP]
> **Acelerador Juniores (Glossário Rápido):**
> Compare APIs API tradicionais com as famosas e velhas Placas de Wi-fi pings infinitos de "Lá e Cá", vulneráveis na Rede Interna LAN ou abertas pra nuvem AWS.
> Agora, imagine e visualize o Protocolo **Anthropic MCP (Stdio)** literamente como o bom, velho, rústico e indestrutível **Cabo Físico USB**. Ao invés do Cursor disparar pings pra Open-AI via Web (HTTP), você enfia esse cabo da IA invisível do HD direto na "Tomada USB" imaginária do VSCode e ela lê seus diretórios de código numa simbiose de memória RAM intransponível a ataques DoS.

> [!NOTE] 🧬 **Código Vivo: O Servidor Anthropic MCP (SHA: `94bfb2f`)**
> ▫️ **Motor de IPC local (Stdio Server):** `src/mcp_stdio.py`
> ▫️ **Config do Assistente (OpenCode/Cline):** `cline_mcp_settings.json`

---

## 3. O Ecossistema OpenCode (TUI & Pair Programming)

O **OpenCode** foi integrado oficialmente ao ecossistema Sovereign Pair para oferecer uma via expressa ao VS Code. Através dessa integração, toda a sua digitação na IDE flui por um Proxy *OpenAI-Compatible*, sem bater na Internet, batendo diretamente no RAG Híbrido Cíbrido (Ollama Local ou no *"The Coder"* remoto rodando num nó Oracle de alta densidade).

### 3.1 Instalação e Engate
Para instalar e espelhar o poder do Sovereign Pair no seu Visual Studio Code usando o OpenCode Terminal User Interface (TUI):

1. **Instale o Binário Subjacente:**
   No Arch Linux (ou via gerenciador correspondente):
   ```bash
   sudo pacman -S opencode
   ```
2. **Instale a Extensão Mágica na IDE:**
   Acesse as Extensões do seu VS Code, procure e instale o pacote oficial `OpenCode` (desenvolvedor SST). Isso criará a "Command Unit" no seu painel lateral.
3. **Plante o Arquivo JSON Isolador (`opencode.json`):**
   Na raiz absoluta do Workspace que você deseja analisar (como dentro do próprio repo `sovereign-pair` ou em projetos do `home-organizer`), crie um arquivo chamado `opencode.json`:
   
   ```json
   {
       "$schema": "https://opencode.ai/config.json",
       "provider": {
           "sovereign-local": {
               "npm": "@ai-sdk/openai",
               "name": "Sovereign Pair Local Gateway",
               "options": {
                   "baseURL": "http://localhost:8000/v1/opencode",
                   "apiKey": "sovereign-local"
               },
               "models": {
                   "qwen2.5-coder:7b": {
                       "name": "Local NPU/GPU Worker"
                   },
                   "coder": {
                       "name": "Sovereign The Coder (Oracle Remote Node)"
                   }
               }
           }
       }
   }
   ```
4. **O Teste de Sangue (Atalho Divino):**
   Com a API rodando no `uvicorn` local (porta 8000, e bypass estrito rodando), abra qualquer arquivo da sua IDE. Ao invés de usar as caixas engessadas de Chat nativas de mercado, você deve **Disparar o OpenCode TUI Nativo**.
   * Pressione o atalho estrito: `Ctrl+Esc`
   * Imediatamente um sub-terminal dinâmico da OpenCode nascerá. Este módulo intercepta seu Workspace por inteiro e despeja os blocos para o endpoint da sua máquina. Testado com 20.000 tokens e **Custo Zero**.
