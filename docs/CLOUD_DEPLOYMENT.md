# Sovereign Pair: Implantação na Nuvem (Cloud Deployment)

Este guia cobre o processo de montagem e hospedagem do Sovereign Pair em ambientes de Nuvem Pública (AWS, Google Cloud, Oracle Cloud, VPS genérico) utilizando as melhores práticas Cloud-Native e Zero-Trust.

## Arquitetura Cloud-Native

O repositório já vem com uma orquestração Docker Compose completa que encapsula:
1. **Frontend Vue.js:** Multi-estágio servido via `nginx:alpine` super veloz.
2. **Backend FastAPI:** Imagem enxuta baseada em `python:3.12-slim` rodando com usuário *não-root*.
3. **Persistência Vetorial & Relacional:** Usa a imagem oficial do ChromaDB e PostgreSQL 15 nativo.
4. **Caddy Edge Router (Auto-HTTPS):** Substituto moderno do Nginx/Cert-Manager que auto-assina o TLS para tráfego em rede privada, ou usa Let's Encrypt para domínios reais, com zero esforço de configuração manual.
5. **Tailscale VPN Sidecar:** (Opcional) Expõe a API e o App apenas dentro de uma VPN WireGuard mesh mTLS, sem precisar abrir portas 80/443 para a internet, barrando scanners da nuvem instantaneamente.

---

## 🚀 Passo a Passo de Implantação

### 1. Preparando a VM (Host)
Você precisará de uma máquina com pelo menos 4GB de RAM (Recomendamos 8GB se for gerenciar documentos muito extensos).
Instale os pré-requisitos fundamentais:
- Git
- Docker Engine & Docker Compose Compose V2

### 2. Configurando o Ambiente e API Keys
Clone o repositório e crie seu arquivo `.env` definitivo:
```bash
git clone https://github.com/Sovereign-Pair/sovereign-pair.git
cd sovereign-pair
cp .env.example .env
```
Preencha o `.env` seguindo dicas de segurança:
- Defina senhas fortes para `POSTGRES_PASSWORD`.
- *Opcionalmente* insira o `TS_AUTHKEY` caso queira a malha Zero-Trust ativada.
- Adicione as API Keys de Nuvem (Ex: `GEMINI_API_KEY` ou `OPENAI_API_KEY`). **O backend cuidará da redação dessas chaves em logs automaticamente graças ao nosso Filtro de Segurança.**

### 3. HTTPS e Domínio (Edge Router Automático)
O Sovereign Pair usa **Caddy** para fazer a ponte e terminação SSL/TLS:
- Dê uma olhada no arquivo `Caddyfile` na raiz.
- **Se não tiver domínio (Uso Tailscale ou IP):** Deixe o arquivo como está. O Caddy forçará HTTPS local auto-assinado.
- **Se TIVER domínio próprio publico:** Descomente a Sessão 1 do `Caddyfile` e substitua `seudominio.com.br` pelo seu domínio real. O Caddy emitirá o SSL via Let's Encrypt para você.

### 4. Inicialização Segura (Run)
Suba todos os containers e construa os assets do Vue com um comando só:
```bash
docker compose up -d --build
```
Após o build (que demorará de 2 a 5 minutos na primeira vez para baixar imagens DB, compilar NPM e instalar Libs de Machine Learning do Python), o seu RAG Pessoal estará vivo rodando em portas blindadas atrás do Caddy.

Acesse a interface pelo navegador: `https://[SEU-DOMINIO-OU-IP-TAILSCALE]`
