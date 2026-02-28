# ☁️ Guia de Implantação em Nuvem & Segurança (Docker)

Bem-vindo ao Guia Oficial de Implantação do **Sovereign Pair**. Este documento explicará detalhadamente como a nossa infraestrutura de contêineres funciona, e a "mágica" por trás do nosso roteamento Edge-Router e da Rede Zero-Trust.

---

## 🏗️ A Arquitetura de Contêineres
Quando você executa `docker compose up -d`, o nosso orquestrador levanta um exército de **6 contêineres** trabalhando em uníssono dentro de uma rede virtual isolada (Ponte chamada `sovereign-net`). 

1. **`sovereign-db` (PostgreSQL):** O banco de dados relacional que gerencia usuários, histórico de conversas e configurações corporativas.
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
