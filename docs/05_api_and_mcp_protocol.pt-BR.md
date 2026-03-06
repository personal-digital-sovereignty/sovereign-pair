# Tratado V: Protocolo de Interoperabilidade (API & MCP)

O projeto Sovereign Pair foi concebido para expor o seu cérebro eletrônico central através de dois protocolos distintos e mortais. O sistema atende tanto a engenheiros de automação corporativos (Webhooks) quanto desenvolvedores de Software Raiz de IDE.

## 1. A API REST Clássica (Integração N8N & HTTP)

A porta de entrada primária da espinha dorsal é a aplicação FastAPI (`src/api/routes.py`), que geralmente roda no seu Orquestrador (A Nuvem Gratuita Oracle). 

Ela fornece "endpoints" síncronos e assíncronos pesadamente otimizados para Webhooks estáticos. Este é o **método oficial e preferido** quando você precisa espetar a Inteligência do Sovereign Pair em construtores de Fluxo Visual como `N8N`, `Make/Integromat` ou um Front-End desenhado em `Vue.js`.

### 1.1 As Rotas Críticas
- `POST /v1/chat/completions`: A Rota Mestra e o pão com o diabo da aplicação. Ela aceita as mesmas estruturas de Payload (`messages: []`) idênticas que a Open-AI da Microsoft exige. Esta rota sorrateiramente engatilha todo o duto do **RAG Matemático Híbrido** e aplica o Bypass de "Empty Response" para impedir que o sistema trave em dias zero.
- `GET /v1/projects`: Escaneia fisicamente a pasta de arquivos do seu servidor (`Sensus Vault`) e devolve um JSON array mapeando todas as pastas separadas dos seus Múltiplos-Inquilinos (Tenants).
- `POST /v1/sys/stats`: Grita aos céus pela telemetria física nua e crua da placa de vídeo e consumo de RAM DDR do seu PC Gamer Físico onde roda a IA escondido, atestando Uptime.

> [!WARNING]
> Devido às severas leis restritivas da física de se inferir modelos locais hiperpesados usando placas de redes Mesh P2P, a resposta da IA **NÃO será em milissegundos**. Chamadas Webhook convencionais disparadas pelo nó HTTP do N8N podem demorar aterrorizantes 3 minutos para receber a string inteira formatada. Modifique obrigatoriamente as configurações Timeout "Timeout Configuration" do seu N8N para sumariamente ignorar o clássico *Drop/Abortamento* padrão de 60 Segundos. 

---

## 2. A Integração do Contexto Nativo: Anthropic MCP

O Sovereign Pair tomou a arcaica arquitetura LangGraph, aniquilou-a e expôs nativamente as engrenagens de raciocínio lógico profundo dos seus Agentes (O Doutor, O Enfermeiro, O Programador) através da maravilha revolucionária chamada **Model Context Protocol (MCP)** chancelada pela `Anthropic`.

Isso transforma e converte o seu back-end caseiro num "Módulo Físico Local de Expansão de Habilidades", que se acopla como um cordão umbilical nas IDEs Modernas Corporativas (VSCode, Cursor, Cline).

### 2.1. Soberania Absoluta Cíbrida (Zero Internet Local-First)
Diferente das requisições via Internet com APIs Web REST convencionais que podem, eventualmente, vazar pacotes HTTPS snifáveis, o esquema bruto de acoplamento do MCP corre debaixo do túnel exclusivamente engatado via **Stdio** (Standard Input/Output) de Comunicação Inter-Processos (IPC). A sua IDE cria uma ponte local cega de Soquete dentro da memória RAM do Windows/Mac. O seu precioso código de software bilionário e arquiteturas da empresa **jamais pisarão num pacote de rede**. A sua empresa torna-se Zero-Trust inviolável.

### 2.2. O Ritual de Acoplamento do Cliente IDE (VSCode / Cline)
Para injetar o Cofre do Sovereign Pair inteiro voando diretamente pro workflow de código aberto na sua tela, apenas adicione e anexe no finalzinho do seu arquivo de configuração `settings.json` padrão de MCP da Máquina:

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
- **Ferramentas (Tools):** A IA rodando dentro da sua IDE ganha repentinamente os super-poderes brutos de *chamar funções programáveis em Python* vivas. Acionando a faca `sensus_vault_search`, o agente estúpido da IDE tem a epifania insana de revirar o Banco de Dados do ChromaDB Sovereign no meio de uma conversa fiada sobre código CSS só para caçar uma maldita regra arbitrária de negócio PDF que o analista botou lá em 2024.
- **Recursos (Resources):** A IA ganha capacidade autônoma passiva e assombrosa para ler silenciosamente os Markdowns enfiados nas subpastas blindadas criptografadas do seu HD `Sensus Vault` e se enraízar nativamente com a filosofia do seu código ANTES de tentar gerar classes e interfaces com alucinações bestas da gringa tiradas do ChatGPT em nuvem.

> [!TIP]
> **Acelerador Juniores (Glossário Rápido):**
> Compare APIs API tradicionais com as famosas e velhas Placas de Wi-fi pings infinitos de "Lá e Cá", vulneráveis na Rede Interna LAN ou abertas pra nuvem AWS.
> Agora, imagine e visualize o Protocolo **Anthropic MCP (Stdio)** literamente como o bom, velho, rústico e indestrutível **Cabo Físico USB**. Ao invés do Cursor disparar pings pra Open-AI via Web (HTTP), você enfia esse cabo da IA invisível do HD direto na "Tomada USB" imaginária do VSCode e ela lê seus diretórios de código numa simbiose de memória RAM intransponível a ataques DoS.
