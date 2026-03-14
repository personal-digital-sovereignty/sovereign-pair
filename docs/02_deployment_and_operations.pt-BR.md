# Implantação e Operações de Infraestrutura

## 1. Arquitetura Eficiente de Implantação (Oracle Cloud OCI)

Para poupar o uso contínuo de recursos no hardware do desenvolvedor (ambiente local), aplicações secundárias sem necessidade de acesso ao banco de dados isolado podem ser provisionadas em servidores em nuvem. O ambiente homologado para este caso é a instância gratuita *Ampere A1 Compute* da Oracle Cloud Infrastructure (OCI), operando sob arquitetura ARM64.

### 1.1 Orquestração em Contêineres (Docker)

Todo o fluxo operacional do back-end é containerizado através do Docker. O uso de instâncias escaláveis e isoladas evita conflitos com as dependências nativas e bibliotecas de sistema operacional locais.

#### Serviços Isolados Core O.S (Container/Node Level)

1.  **Backend Nativo O.S OCI Gateway (`sovereign-api`):** API mestre e matriz funcional compilatória do projeto O.S construída em **Rust (Axum + Tokio)**. Provê rotinas estruturais de processamento e leitura RAG operados iterativamente via sistema de matriz interna nativa C/C++ `sqlite-vec` ao invés de depender de instanciadores python.
2.  **Sensus Vault UI Frontend (`sovereign-web`):** Módulo Vue 3.x empacotado puramente focado provendo Client-Side-Rendering UI estática sem expor servidores externos integrativos. Requisita interface diretamente direcionada à API restritiva Gateway e opera a PWA.
3.  **Fila de Processos (`redis`):** Sistema para armazenamento transitório em memória. Atua como barramento de mensagens e controlador primário para as listas de execução dos fluxos assíncronos gerados pelo N8N.
4.  **Banco de Dados PostgreSQL (`postgres`):** Banco relacional dedicado ao cache de longo prazo e ao registro de eventos para as execuções dos workflows do nó N8N.

> [!NOTE] 
> A automação dos contêineres está dividida em sub-processos do `docker compose` específicos para cada serviço.
> ▫️ **Topologia Backend Servidor:** `docker-compose.yml`
> ▫️ **Topologia N8N Nuvem:** `docker-compose.n8n.yml`

---

## 2. Isolamento de Rede e Zero-Trust Networking

Por questões de segurança (DevSecOps), nenhuma interface de API (como a porta `8000` do RAG ou a porta `5678` do N8N) deve ser exposta diretamente à internet pública (através de binds globais como `0.0.0.0` nos roteadores de borda). O serviço está configurado para operar primordialmente dentro de um encapsulamento de rede fechada e validada.

Emprega-se a conexão via *Overlay Network* configurada através do túnel remoto ponto-a-ponto nativo, gerido pelo `Tailscale` (baseado em WireGuard). Toda requisição administrativa ocorrerá apenas nessa sub-rede.

### 2.1 Conectividade P2P Híbrida 
1. A certificação e a integração ocorrem pelo provisionamento da chave da máquina na rede do cliente Tailscale do desenvolvedor.
2. A VPN designará blocos de IP fixos baseados na sub-rede de carrier-grade NAT segura (`100.x.x.x`).
3. O mapeamento de acesso nos arquivos do `docker-compose.yml` restringe os endpoints estritamente para essa rede interna (exemplo: `ports: ["100.x.x.x:5678:5678"]`).
4. Solicitações remotas, como pedidos direcionados pela API hospedada na nuvem ao `Ollama` na máquina do usuário, trafegam usando a interface da VPN (`http://100.y.y.y:11434`), sendo inacessíveis à navegação de rede pública.

> [!WARNING]
> O serviço do `Ollama` reserva o acesso local na interface de loopback tcp (`127.0.0.1`) por padrão. Para que os serviços de nuvem ou workers no Docker consigam se comunicar com ele através do Tailscale, é necessário configurar o SystemD da máquina host para incluir a variável de ambiente: `OLLAMA_HOST=0.0.0.0`. O acesso seguro global continua sendo regido pelo firewall do sistema (ex: UFW), que deve permitir o tráfego exclusivamente para a interface de rede provida pelo Tailscale.

---

## 3. Gestão de Recursos e Processamento Otimizado

### Nó Computacional em Nuvem (Oracle A1 OCPU ARM)
- **Escopo Técnico:** O servidor remoto atua delegando a resolução do pipeline de workflows LLM em instâncias independentes. Por conta da infraestrutura baseada em processadores ARM na arquitetura de rede padrão, processos pesados sem o devido acompanhamento de cache podem encontrar limitações de leitura e escrita (I/O).
- **Otimização ZRAM:** A automação inicial do servidor (cloud-init) implanta a biblioteca `zram-tools` no host. Essa estratégia comprime e designa uma partição específica de RAM Virtual, minimizando operações custosas em disco rígido SSD, viabilizando inferências moderadas sem exceder o tempo limite das conexões.

### Estação Local (Workstation do Usuário)
- **Escopo Técnico:** Controlador central dos arquivos Markdown sigilosos e responsável pela sincronização primária do banco SQLite via file-system watcher.
- **Estratégia Computacional:** Manter modelos LLM em execução paralela às atividades do dia a dia do usuário consome capacidade de processamento local (RAM e GPU). Com a distribuição híbrida, o usuário desonera sua estação de operações de roteamento contínuo (API, Node Webhooks) à nuvem, acionando a máquina nativa majoritariamente nas instâncias isoladas de busca semântica, priorizando estabilidade no fluxo normal de desenvolvimento do desktop.

> [!NOTE]
> Requisições integrativas em HTTP exigem cautela com a métrica de transação e os cortes conhecidos por "Connection Timeout". Acionar o modelo hospedado "frio" após longo tempo sem cache ou em consultas sem renderização por *Server-Sent Events (SSE)* podem ultrapassar retornos regulares de proxy, interrompendo a chamada e gerando retornos HTTP 504 no orquestrador. A constante `REQUEST_TIMEOUT` é configurada no ambiente `.env` para suprir margens conservadoras (como `300.0` segundos) mitigando esse risco transacional durante respostas longas do backend.
