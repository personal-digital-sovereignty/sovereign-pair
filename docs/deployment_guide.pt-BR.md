<!-- 
[Aviso Interno de Engenharia]
Este documento 'deployment_guide.pt-BR.md' é a fusão temporária ('bruta') da base de Fases Anteriores. 
Ele será submetido a um processo de refinamento linguístico focado em maturidade Sênior, erradicação de viés Emoji, reescrita corporativa limpa e posterior paralelização para o idioma en-US.
-->

# ☁️ Guia de Implantação em Nuvem & Segurança (Docker)

Bem-vindo ao Guia Oficial de Implantação do **Sovereign Pair**. Este documento explicará detalhadamente como a nossa infraestrutura de contêineres funciona, e a "mágica" por trás do nosso roteamento Edge-Router e da Rede Zero-Trust.

---

## 🏗️ A Arquitetura de Contêineres
Quando você executa `docker compose up -d`, o nosso orquestrador levanta um exército de **6 contêineres** (em breve 7, com a conteinerização nativa do Ollama) trabalhando em uníssono dentro de uma rede virtual isolada (Ponte chamada `sovereign-net`). 

1. **`sovereign-db` (PostgreSQL):** O banco de dados relacional que gerencia usuários, histórico de conversas e configurações corporativas (Multi-Tenant).
2. **`sovereign-chroma` (ChromaDB):** O nosso "Cérebro Vetorial". É aqui que moram os Embeddings do RAG (Retrieve-Augmented Generation).
3. **`sovereign-api` (FastAPI/Python):** O núcleo da Inteligência. Hospeda a API RAG, orquestra LLMs e faz a ponte entre o Banco de Dados e as interfaces.
4. **`sovereign-web` (Vue.js/Nginx):** A nossa interface visual linda, servida de forma extremamente veloz por um Servidor Nginx estático.
5. E os dois guardiões mágicos de infraestrutura: **Caddy** e **Tailscale**.

---

## 🔒 A Mágica do Caddy (Auto-HTTPS & Proxy Reverso)

Se você já tentou subir um sistema web seguro antes, sabe a dor de cabeça que é configurar o Nginx, gerar chaves SSL via OpenSSL e tentar fazer os certificados locais funcionarem. Nós resolvemos isso usando o **Caddy** (`sovereign-caddy`).

O Caddy age como o porteiro do nosso sistema. Em vez de você precisar acessar o Frontend na porta 80 e a API na porta 8000 (sem criptografia), o Caddy resolve tudo na elegante e segura `Porta 443 (HTTPS)`.

### Como o Caddy funciona localmente?
No arquivo `Caddyfile`, nós usamos a diretiva `tls internal`. 
Isso faz com que o Caddy, no milissegundo em que é iniciado, atue como sua **própria Autoridade Certificadora (CA)**. Ele gera e assina um certificado Digital TLS sozinho, criptografando a sua conexão com o `localhost` local.

Quando você acessa `https://localhost`:
1. O Caddy intercepta a requisição, valida o SSL, e descriptografa o pacote.
2. Se a requisição for para `/api/*` ou `/docs`, ele encaminha silenciosamente para o contêiner `sovereign-api` pela rede invisível do Docker.
3. Se for qualquer outra requisição, ele entrega a página do Vue.js (`sovereign-web`).

**Resultado:** Você navega localmente com tráfego 100% criptografado e rotas unificadas, sem configurar absolutamente nenhum certificado manualmente!

---

## 🛡️ Gestão de Memória Limitada e Prevenção de OOM (Out-Of-Memory)

O Sovereign Pair foi desenhado para rodar em hardware de consumidor e não em data centers trilionários. Um dos maiores desafios na integração com orquestradores como LlamaIndex e Ollama é o gerenciamento silencioso da KV Cache (Memória de Contexto).

Modelos modernos como o `llama3.2` ou `llama3.1` possuem janelas de contexto gigantescas nativas (128.000 tokens). Se o back-end tentar instanciar um streaming de *Chat Engine* RAG sem blindar esse limite, o Ollama nativo tentará alocar **quase 60 GB de RAM/VRAM** instantaneamente para acomodar o cache inteiro, o que resulta na morte imediata do serviço no host.

Para impedir isso e garantir hardware-agnosticismo:
- **`num_ctx: 4096`**: O Sovereign Back-end injeta parâmetros hiper-rígidos (`additional_kwargs` limitando contexto a 4K) em *todas* as factories de LLM criadas. Isso proíbe o LlamaIndex de alavancar o VRAM excessivo e garante que o Meta-RAG e chats corporativos fluam tranquilamente num Dell com 16GB de RAM sem engasgar e dar o famoso *Status 500: Empty Response*.

---

## 🌐 A Mágica do Tailscale (VPN Zero-Trust com MagicDNS e HTTPS)

Imagine que você instalou o Sovereign Pair no seu computador Desktop de casa (ou em uma VPS leve da Oracle/AWS), mas você quer sacar o seu celular no 4G lá na rua e conversar com a sua IA.

A forma antiga (e extremamente perigosa) de fazer isso seria abrir a porta 443 do seu roteador para a Internet. Isso expõe seu servidor a toda sorte de hackers, bots escrutinadores russos/chineses e ataques DDoS.

**Aqui entra o `sovereign-tailscale`:**
O Tailscale é uma rede Mesh baseada no protocolo ultrasseguro **WireGuard**. Nós encapsulamos ele nativamente como um contêiner "Sidecar" no nosso Docker Compose. O Caddy, por sua vez, está configurado para compartilhar placa de rede com o Tailscale (`network_mode: service:tailscale`).

### Como ele funciona na prática (HTTPS Nativo)?
1. Quando o Compose sobe, o contêiner do Tailscale cospe uma URL nos logs. Você clica nessa URL e vincula aquele contêiner à sua conta do Tailscale.
2. A máquina ganhará um nome MagicDNS no seu painel (ex: `sovereign-rag-cloud.tail96a848.ts.net`).
3. **Gerando o Certificado HTTPS:** Vá no painel do Tailscale (`DNS` -> `HTTPS Certificates`) e ative o recurso. Em seguida, acesse o terminal do servidor e diga ao Tailscale para servir o tráfego 443 proxyando para o nosso Caddy (Porta 80) em background:
   ```bash
   docker exec sovereign-tailscale tailscale serve --bg http://localhost:80
   ```
4. **Resolução Automática:** O próprio daemon do Tailscale interceptará o tráfego HTTPS na sua porta virtual, descriptografará utilizando os seus próprios certificados Let's Encrypt gerados automaticamente e encaminhará em texto limpo para o Caddy na rede loopback do contêiner. O Caddy então faz o roteamento inteligente para a API e pro WebUI.

**O Resultado:** Do seu celular no 4G (com o App do Tailscale aberto), você acessará a URL HTTPS blindada com o Cadeado Verde. Nenhum hacker na internet consegue "ver" nem "bater" na sua API, porque as portas físicas do Docker foram estritamente blindadas para \`127.0.0.1\` e a API existe apenas na sua Dimensão Particular Zero-Trust! 🌌

> [!NOTE]
> **Sobre o erro `Authorization failed: requested tags [tag:server] are invalid`:**
> Se no passado você tentou usar a flag `--advertise-tags=tag:server` no docker-compose e recebeu esse erro, isso ocorre por causa do sistema de **ACLs (Access Control Lists)** do Tailscale. Usuários de contas gratuitas (Free/Starter) geralmente não têm permissão para auto-assumir tags corporativas. Para contas pessoais, a autorização padrão (sem tags rígidas) garante que o seu "MagicDNS" funcione perfeitamente sem bloqueios de segurança do painel administrativo.

> [!TIP]
> **Preciso autenticar de novo a cada reinicialização do Docker?**
> **Não!** O nosso `docker-compose.yml` possui um volume mapeado chamado `tailscale-state:/var/lib/tailscale`. Isso significa que (1) a identidade da máquina, (2) as chaves de pareamento e (3) os certificados HTTPS gerados são salvos permanentemente no seu disco rígido hospedeiro.

---

## 📱 O Dilema Mobile (Android vs DoH/NextDNS)

Muitos usuários avançados utilizam serviços como o **NextDNS** configurados nativamente nas configurações de "DNS Particular" (DoH/DoT) do Android ou embutidos no Chrome/Firefox, para contornar abusos de operadoras e filtrar rastreadores.

O problema é que o "DNS Particular" do Android força TODAS as requisições a irem criptografadas para a nuvem. Ele se recusa a perguntar ao DNS local da VPN (`100.100.100.100`) onde fica o domínio `sovereign-rag-cloud.tailxxxx.ts.net`. O Android não encontra a rota e o acesso falha.

Existem duas soluções para conciliar Soberania Zero-Trust com Hiper Segurança de DNS:

**A. Injeção de Rota via Tailscale Admin (Padrão)**
No painel do Tailscale, vá em **DNS**. Adicione o IP IPv4 do seu perfil NextDNS em *Global Nameservers*. Marque a opção **"Override local DNS"**. Assim, o aplicativo móvel do Tailscale vai interceptar os pedidos e direcionar o MagicDNS da forma correta mesmo usando o seu NextDNS no fundo.

**B. O Hack Limpo e Soberano (Solução Definitiva NextDNS)**
Se você não quer que o Tailscale sobrescreva nada e quer manter seu DoH ativo 24/7 no Android ditando as regras:
1. Acesse o painel do seu **NextDNS**.
2. Vá na aba **Settings** (Configurações) -> **Rewrites** (Reescritas).
3. Adicione uma regra onde o Domínio é a sua URL Exata (ex: `sovereign-rag-cloud.tail96a848.ts.net`) e a Resposta é o IP 100.x do seu Caddy (ex: `100.106.246.15`).

**A Mágica:** O seu navegador Android, via túnel hiper-secreto DoH do NextDNS, perguntará à nuvem quem é o nó do RAG. O NextDNS retornará o IP privado da Layer 3 (Tailscale). O tráfego será puxado da nuvem, jogado na sua placa de rede virtual do celular e entregue com sucesso dentro de casa, preservando o Cadeado Verde e bloqueando completamente o seu provedor de acesso físico!

---

## 🚀 Guia de Início Rápido e Pareamento (Zero-Trust)

1. Clone o repositório.
2. Crie ou copie o arquivo `.env` (insira suas chaves de API da OpenAI/Gemini/Anthropic).
3. Rode a ignição:
```bash
docker compose up -d
```
4. **Pareamento da VPN (Tailscale):** Se você não configurou a variável opcional `TS_AUTHKEY` no `.env`, o contêiner precisará da sua autorização manual na primeira vez em que subir.
   - Execute o comando abaixo no terminal para ler os logs do Tailscale:
     ```bash
     docker logs sovereign-tailscale
     ```
   - Procure nos logs por uma mensagem parecida com esta:
     `To authenticate, visit: https://login.tailscale.com/a/xxxxxxx`
   - Clique no link gerado, faça login com sua conta do Tailscale e **aprove a nova máquina** (que aparecerá listada como `sovereign-rag-cloud`).
5. **Acesso à IP/DNS:** No painel do Tailscale, copie o seu MagicDNS (ex: `sovereign-rag-cloud.tailxxxx.ts.net`).
6. **Configurando o Obsidian (Celular ou Notebook Externo):**
   - No Obsidian, vá em `Configurações > Sovereign Pair`.
   - Altere a **API URL** para a sua URL Magic DNS com HTTPS: `https://[SEU_MAGIC_DNS_AQUI]`. O Caddy servirá os certificados do Tailscale providenciando máxima segurança em trânsito.
7. **Acesso Final:** 
   - **Localmente (Mesa/Host):** Abra seu navegador e acesse **`https://localhost`** (As portas 80/443 do docker agora estão blindadas em Localhost - `127.0.0.1`).
   - **Remotamente via Tailscale:** Pelo seu smartphone ou laptop externo com a VPN ativa, navegue rigorosamente acessando o DNS HTTPS validado: `https://sovereign-rag-cloud.seu-dominio.ts.net`.
   - **Isolamento Total:** Devido a políticas exclusivas e severas do seu Storage Local no navegador, você **sempre** deve acessar pela exata string/URL com a qual realizou o Cadastro Inicial Mestre (Setup). Acessar o sistema por IP direto exibirá uma tela de Setup Nova, não o seu Login já existente.


---

# Guia Definitivo: Sobrevivendo ao Oracle Cloud Infrastructure (OCI)

A implantação do braço "Cibrid" (Sovereign Node) na Oracle Cloud Framework sofreu com gargalos corporativos severos durante os testes reais em Ashburn (us-ashburn-1). Este documento serve como post-mortem e "How-To" definitivo para não arrancarmos os cabelos no futuro.

---

## 1. O Temido Erro: `500-InternalError, Out of host capacity`

**O Problema**:
Mesmo atualizando a conta de *Always Free* para *Pay As You Go* (Pague Pelo Que Usar), a tentativa de rodar `tofu apply` para criar uma VM Ampere A1.Flex (ARM64) retornou o erro `Out of host capacity`.
Ao contrário da intuição, a Oracle **não reserva hardware físico separado para clientes pagantes nas máquinas Ampere**. Eles dividem o mesmo rack com o Free Tier. Como há milhares de robôs no mundo todo farmando IPs gratuitos, as regiões mais quentes (como Virgínia/Ashburn) ficam sem capacidade 24 horas por dia.

**O Workaround (O Script "Martelo")**:
Construímos o script `infra/terraform/retry_deploy.sh`. Ele ignora o erro 500 e bate na porta da API da Oracle a cada 2 minutos (`sleep 120`).
Quando alguém deleta uma máquina e um slot surge, o script rapidamente executa `tofu apply -auto-approve` e rouba a vaga antes de um humano conseguir clicar na interface Web.

**Importante:** Nunca apague a máquina se for mudar algo. Modifique *em cima* dela. Se você der `tofu destroy`, outro bot rouba a sua vaga em 4 segundos e você volta ao fim da fila.

---

## 2. A Incomunicação: OCI DNS Failure (Erro 502/Timeout)

**O Problema**:
Nosso código Terraform injeta um script `cloud-init.yaml` para instalar a Tailscale e o Docker assim que o Ubuntu dá o primeiro boot.
No entanto, quando a nossa máquina de 6 Cores finalmente "nasceu", a placa de rede da VCN (Virtual Cloud Network) da Oracle demorou para inicializar o resolvedor de DNS padrão. O `apt-get update` e o `curl` da Tailscale falharam (Temporary failure resolving 'ports.ubuntu.com'). A máquina ligou, mas vazia e inútil.

**O Workaround (Intervenção na Unha)**:
1. Conectamos via SSH na máquina moribunda.
2. Forçamos o DNS do Google editando os Nameservers:
   `echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf > /dev/null`
3. Executamos os comandos de instalação da Tailscale e do Ollama nativamente no bash da Oracle, resolvendo a questão sem perder a preciosa vaga.

---

## 3. O Inferno das Chaves SSH (.PEM vs RSA)

**O Problema**:
Por padrão, o Terraform/Sovereign paira em chaves de criptografia Curva Elíptica (ED25519) (`~/.ssh/id_ed25519.pub`). 
Contudo, se você for criar a máquina **manualmente pela interface Web da Oracle** (ou usar a suíte legada deles), a OCI costuma rejeitar ou formatar mal chaves recém-criadas sem o cabeçalho clássico `ssh-rsa` (o formato das antigas `.pem`).
Isso causava erro de `Permission denied (publickey)` ao tentarmos resgatar a máquina fantasma.

**O Workaround**:
Sempre use o `cloud-init.yaml` (bloco `ssh_authorized_keys:`) do Terraform para "injetar" a chave local pura. A injeção via boot-script ignora a UI da Oracle Cloud e escreve a chave correta direto na raiz do Ubuntu, garantindo que o seu par gerado via Terminal Linux funcionará.

---

## 4. Estratégias Financeiras e Tabelas de Preços

O Sovereign Pair funciona maravilhosamente bem sob a política de "Pay As You Go" para ganharmos velocidade. 

### A Grande Pergunta: Posso ter a máquina de 6 Cores e também "farmar" uma máquina Free Tier de 4 cores em outra região?
**Resposta**: Não simultaneamente. A Oracle garante um *total global* de 4 OCPUs e 24GB de RAM gratuitos por **Tenancy** (Conta/CPF).
Isso significa que, se você está usando a máquina paga de 6 OCPUs, 4 desses OCPUs e 24GB desses GBs ainda entrarão no "desconto" do Free Tier, e você *só pagará o excedente* (Neste caso, você paga apenas por 2 OCPUs e 8 GB extras num datacenter, mas não conseguirá levantar os 4 grátis do outro lado ao mesmo tempo sem pagar por 100% deles).

### Cálculo de Custos (VM.Standard.A1.Flex - 6 Cores, 32 GB RAM)
*Cotação OCI Arm Ampere Base: $0.010 por OCPU/h + $0.0015 por GB/h.*

*Porém, se a conta absorve o desconto Free Tier nos primeiros 4 Cores e 24GB, a conta fica assim:*

| Recurso | Utilizado | Coberto pelo Free Tier | Quantidade Faturável | Custo por Hora | Custo por Mês (730h) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OCPU (Cores)** | 6 | - 4 | **2 OCPUs** | $ 0.02 | **$ 14.60** |
| **Memória (RAM)**| 32 GB | - 24 GB | **8 GB** | $ 0.012 | **$ 8.76** |
| **Armazenamento**| 50 GB | - 50 GB | **0 GB** | $ 0.00 | **$ 0.00** |
| **IP Público** | 1 | - 1 | **0** | $ 0.00 | **$ 0.00** |

**Total Estimado por Mês ($ USD):** ~$23.36  
**Total Estimado por Mês (R$ BRL):** ~R$ 130,00  

Se você precisar desligar a máquina ou deixá-la parada, a cobrança cessa (exceto centavos pelo disco armazenado). Se você for rodar o Sovereign Node o mês inteiro sem parar, o custo final extraindo petróleo com 6 núcleos de processamento será de apenas **R$ 130 por mês**.

---

## 5. Como usar 100% "The Coder" na Oracle (Cibrid Network)

Agora que o *sovereign-rag-cloud* local pode ser desligado, o fluxo do Tailscale substitui o host do Doctor.
Para usar apenas a Oracle:
1. Abra o arquivo `.env` do Sovereign Pair nativo.
2. Troque as URIs locais para o IP da Tailscale de Ashburn:  
   `OLLAMA_API_BASE=http://100.116.34.115:11434`
3. Mate qualquer Ollama rodando no seu Linux (Ryzen). A partir de agora, o The Accountant e o The Coder usam 100% o OCI Cloud.


---

