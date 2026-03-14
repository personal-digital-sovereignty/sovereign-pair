# Implantação e Operações de Infraestrutura

## 1. Arquitetura Orientada a Alta Eficiência e Baixo Custo (Oracle Cloud OCI)

Na finalidade de estender o ciclo de vida e a capacidade operacional em instâncias físicas pessoais de desenvolvedores (Hardware do Edge Local), delegam-se aplicações de infraestrutura que não processam contexto persistente local diretamente para *compute nodes* na grade de Cloud Servers. A otimização adotada foi implementada para garantir resiliência aos nós virtualizados estritamente dentro da arquitetura **ARM64**. O uso do *target deployment* oficial e testado em homologação para isso é na instância gratuita tipo *Ampere A1 Compute* da Oracle Cloud Infrastructure (OCI).

### 1.1 Orquestração em Contêineres (Docker)

O fluxo operacional do código foi completamente alocado na topologia robusta e portável baseada em engine Linux *Docker*. Foram sumariamente refutados implementos que corrompam as bibliotecas locais originais do Host SO com instaladores de linguagem padrão, com as instâncias contidas em manifestos isolados escaláveis.

1.  **Backend FastAPI (`sovereign-api`):** API servidora processual atrelada ativamente. Roteia tráfego multi-tenant concorrente, encapsula instâncias LLM em Workers Background e efetua as abstrações dos tokens na camada Python do RAG.
2.  **Motor RAG e Workflow Automático (`n8n`):** O módulo autônomo. Implementa APIs restritas legadas e realiza interface via Webhook Request System com sistemas externos validados para acionar fluxos orquestrados no servidor RAG localmente sem poluição visual no PWA Padrão.
3.  **Engine de Fila Redis (`redis`):** Provisão transitória em contêiner alocado sob memória nativa *In-Memory*, cuja atribuição restrita é funcionar de Event-Bus primorial e Lock Controller nas rotinas processuais horizontalizadas de filas (Queues) do fluxo `n8n`.
4.  **Banco de Retenção Estrutural PostgreSQL (`postgres`):** Processo dependente relacional dedicado restritamente como cache nativo a long-termo persistindo estruturas não vetorializadas e Logs inerentes unicamente às funções vitais das rotinas executadas pelo framework Webhook interno do nó orquestrador N8N.

> [!NOTE] 
> O padrão imposto a rodutologia de Deploy de Integração Contínua acopla todas essas definições nos sub-processos orquestrais de malha `docker compose up -d` isolados atreláveis aos fluxos específicos. 
> ▫️ **Topologia Padrão Backend Server:** `docker-compose.yml`
> ▫️ **Topologia Workflow N8N Server Nuvem:** `docker-compose.n8n.yml`

---

## 2. Abstração de Contorno e Camada Zero-Trust Networking

Por determinação global à operação DevSecOps aplicada ao *Endpoint*, as implementações das APIs (tanto processual física RAG via Porta `8000`, ou Worker Orchestrators N8N porta `5678`) localizadas em VPS/Bare-Metals ou expostos localmente com *IP Pessoal Reverso*, **nunca** serão anexadas no firewall sistêmico com preenchimento global Bind a Interfaces abertas (ex. rotear via `0.0.0.0` para Gateways Public IPv4). Processos *Stateful* ou banco de dados sensíveis escanchados são expostos a injúrias técnicas massivas de automações *Bot Net / Scraping / Ransomware DB Drop* assim que indexados na *public internet*.

Adotou-se então a blindagem por encapsulamento *Overlay Network* configurada primicialmente à nível do Tunnel Peer-to-Peer nativo (Ferramenta `Tailscale` / base Wireguard Engine) atuando via criptografia intrínseca para os nodes. As transferências e Requisições API atestadas processar-se-ão estritamente no meio fechado.

### 2.1 Conectividade P2P Cíbrida (Vínculo Tunelado Node / Cloud Host)
1. Certificação e ingresso atreladas à API Mesh Layer tanto na Hospedagem (Nó Computacional OCI Nuvem) perante Cliente Desktop de Processamento Backend Node (Hardware Local).
2. O servidor virtual Tailscale delegará DHCP abstrato e designará de forma estática blocos não roteáveis classificados na subnet segura via Carrier-Grade NAT. (ex: escopo IP de túneis `100.X.X.X`).
3. O `docker-compose.yml` e arquivos infra afins, designam ativamente a contenção e mapeio Exclusivo na interface nativa mTLS atestando *Bind Isolation*, ex. `ports: ["100.x.x.x:5678:5678"]`.
4. Todas invocações remocionais (como o Gateway FastApi demandar que Nuvem execute Predições no Modelo Qwen-2.5 do Ollama Cloud) seguem explicitamente a sintaxe HTTPS atada àquela VPN Virtual (`http://100.y.y.y:11434`), mantendo tráfego invisível e impossível a espelhametos do Gateway Operadora / IPS locais da rede local pública comum.

> [!WARNING]
> O Engine de Inferência `Ollama` assume nativamente a restrição Bind Padrão de Listen TCP cravado na variável Loop-Back Address (`127.0.0.1`), refutando acesso cruzado de pacotes externos na mesma porta física do processador. Para que os Workers N8N e as topologias Cloud OCI alcancem as instâncias de placa Llama físicas no interior das dependências privadas (Seu Workstation físico contendo SQLite e Motor RAG GPU CUDA), impõe-se a exigência no ambiente `.env` O.S injetar e delegar o serviço do processo OLLAMA no escopo de acesso restrito pela VPN, atestando como valor extra de reinicialização no SystemD: `OLLAMA_HOST=0.0.0.0 ollama serve`. (O que será contido logo em seguida mediante aos filtros UFW / Firewall restritivo aos túneis Tailscale do O.S base). 

---

## 3. Gestão Preditiva de Hardware e Trocas Computacionais Agressivas

### O Parâmetro do Nó de Nuvem Remota (Oracle A1 OCPU ARM)
- **Escopo Técnico:** Módulo autônomo transferencial configurado massivamente na implantação base infra-as-code. Desempenha a resolução lógica do pipeline, focando massivamente na rotina Ollama Virtual nativa desonerada de GPUs. Em prol da sua restrição técnica proveniente à arquitetura de chipset ARM processional (sem Unidades Neuromorficas) aliadas ao disco lógico Block Storage padrão da rede OCI, requer hacks agressivos na manipulação e buffer Kernels atenuando restrição crítica I/O Disk de grandes vetores.
- **Engenhosidade Aplicada e Alocação O.S ZRAM:** Dispara no momento *Init-Cloud Provisioning Script* instâncias paramétricas no Root do Server instalando controladores utilitários (`zram-tools` forçando alocação de Swap Memory em formato de algoritmo de super-compressão). Resguardando o tamanho final dinamicamente, possibilita extração pesada via CPU Arm pura do conteúdo dos modelos sem estourar e congestionar transações assíncronas no HD SSD sub-par.
- **Taxas Empíricas Praticadas:** Processos e inferências com OCI nativo conseguem estabilidade de vazão computacional na métrica de ~6 tokens extraídos na secundagem sobre modelo de codificação pura *qwen2.5-coder*.

### O Host Persistente (Workstation Pessoal Base Edge Node)
- **Escopo Técnico:** Encapsulador de Arquivos físicos confidenciais operantes MD e repassos orquestrados no SQlite RAG via *File-Watcher System*.
- **Estratégia Computacional de Preservação:** A carga nativa LLM na interface e nos testes isolados asfixia RAM ociosa local do Desktop O.S quando solicitada paralelamente. A finalidade desta arquitetura base Cíbrida/Híbrida baseia-se exatamente em transferir este workload para orquestradores OCI, delegando e repassando à interface PWA do Frontend ou FastAPI estritamente as instâncias lógicas de Indexação Matemática. A GPU/CPU do usuário permanece nativamente leve ao dia a dia de Software e Compilação operante.

> [!NOTE]
> Rotinas transacionais orquestrais originadas em clientes dependentes assíncronos HTTP (via Request Axios N8N, ex.) são inerentes a restrições programacionais severas atinentes à métrica *Connection-Timeout*. Disparos em modelagens em "estado frio" que não usufruam de render stream (`SSE`), atestarão respostas tardias e desencadearão rompimentos padrão com saídas 504 no orquestrador (Excedentes de 120seg). A contramedida foi adicionada intrinsecamente na base do FastApi declarada na variável de ambiente local estrita e rígida (`REQUEST_TIMEOUT="300.0"`). O tempo máximo dilui limites de interrupção subjacente a rede, acomodando e alinhando adequadamente I/O demorados originados da inferência OCI ou Local-First sem forçar cancelamento forciato da chamada.
