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

## 🌐 A Mágica do Tailscale (VPN Zero-Trust)

Imagine que você instalou o Sovereign Pair no seu computador Desktop de casa (ou em uma VPS leve da Oracle/AWS), mas você quer sacar o seu celular no 4G lá na rua e conversar com a sua IA.

A forma antiga (e extremamente perigosa) de fazer isso seria abrir a porta 443 do seu roteador para a Internet. Isso expõe seu servidor a toda sorte de hackers, bots escrutinadores russos/chineses e ataques DDoS.

**Aqui entra o `sovereign-tailscale`:**
O Tailscale é uma VPN Mesh baseada no protocolo ultrasseguro **WireGuard**. Nós encapsulamos ele nativamente como um contêiner "Sidecar" no nosso Docker Compose.

### Como ele funciona na prática?
1. Quando o Compose sobe, o contêiner do Tailscale cospe uma URL nos logs (`docker logs sovereign-tailscale`).
2. Você clica nessa URL e vincula aquele contêiner à sua conta do Tailscale.
3. **A Mágica:** Você não precisa abrir *nenhuma* porta no seu roteador. O Tailscale fura o NAT do seu provedor (NAT Traversal) usando conexões de saída (Outbound) e cria um túnel criptografado Ponto-a-Ponto diretamente para os servidores de "coordenação" deles.
4. O contêiner anuncia a *Subrede* do Docker (a rede virtual onde a API e o DB vivem) para o seu túnel privado.

**O Resultado:** Do seu celular no 4G (com o App do Tailscale instalado), você acessa algo como `https://sovereign-api` do seu navegador. O tráfego "voa" criptografado da ponta do seu fone, passa invisível pela infraestrutura da internet aberta, e "pousa" de forma ultra-segura decodificado dentro da ponte virtual do Docker na sua casa.

Nenhum hacker na internet consegue "ver" nem "bater" na sua API, porque ela literalmente *não existe* no mapa de IPs públicos mundiais. Ela existe apenas na sua Dimensão Particular Zero-Trust! 🌌

> [!NOTE]
> **Sobre o erro `Authorization failed: requested tags [tag:server] are invalid`:**
> Se no passado você tentou usar a flag `--advertise-tags=tag:server` no docker-compose e recebeu esse erro, isso ocorre por causa do sistema de **ACLs (Access Control Lists)** do Tailscale. Usuários de contas gratuitas (Free/Starter) geralmente não têm permissão para auto-assumir tags corporativas. Para contas pessoais, a autorização padrão (sem tags rígidas) garante que o seu "MagicDNS" funcione perfeitamente sem bloqueios de segurança do painel administrativo.

---

## 🚀 Guia de Início Rápido

1. Clone o repositório.
2. Crie ou copie o arquivo `.env` (insira suas chaves de API da OpenAI/Gemini/Anthropic).
3. (Opcional) Gere uma Key de Autenticação Efêmera no seu painel Tailscale e insira em `TS_AUTHKEY=` no `.env` para automatizar o pareamento da VPN.
4. Rode a ignição:
```bash
docker compose up -d
```
5. Abra o navegador em `https://localhost` e surpreenda-se!

Se estiver acessando via Tailscale, use o "MagicDNS" injetado pela rede (`https://[ip-do-tailscale-do-container]`).
