# Sovereign Pair - Estudo de Arquitetura Custo Zero (Zero-Cost Infra)

**Fase do Projeto:** 42 (Orquestração e Integração Cíbrida)
**Objetivo:** Elaborar o plano arquitetural para implantação de um ecossistema de automação (N8N) suportado por cache em memória (Redis) com custo computacional estritamente igual a zero ($0.00), utilizando malhas seguras fechadas (Tailscale).

---

## 1. Premissas de Engenharia

Para satisfazer o requerimento absoluto de `Custo Zero`, a topologia descarta PaaS (Platform as a Service) gerenciadas como RedisLabs, AWS ElastiCache ou N8N Cloud. A arquitetura recairá inteiramente sob o paradigma *Self-Hosted* sobre fatias gratuitas de Nuvem Pública (*Always Free Tiers*).

*   **Poder Computacional:** Oracle Cloud Infrastructure (OCI).
*   **Rede e Segurança:** Tailscale (WireGuard Mesh VPN).
*   **Orquestração de Containers:** Docker Compose Nativo.
*   **Aplicações Alvo:** N8N (Community Edition) e Redis (Alpine/Docker).

---

## 2. A Escolha de Hardware (OCI Free Tier)

A Oracle Cloud fornece o plano `Always Free` mais generoso do mercado para processadores ARM64 (Ampere). 

**Especificações Alocadas (Nó Orquestrador):**
*   **Instância:** `VM.Standard.A1.Flex`
*   **CPU:** 4 OCPUs (Equivalente a 4 vCPUs robustas).
*   **RAM:** 24 GB unificados.
*   **Armazenamento:** 50 GB de Block Volume (SSD).
*   **Custo Contratual:** $0.00/mês perpetuamente.

*SRE Note:* 24GB de RAM são exponencialmente suficientes para rodar o motor NodeJS do N8N na sua plenitude (que sofre gargalos críticos em instâncias T2.Micro da AWS com apenas 1GB) e acomodar a persistência em memória transacional do Redis.

---

## 3. Topologia Zero-Trust (Rede Tailscale)

Uma das maiores armadilhas de soluções *Self-Hosted* é expor interfaces administrativas (como a porta `5678` do N8N ou `6379` do Redis) diretamente à Internet pública (`0.0.0.0`), atraindo scanners e bots maliciosos nativos de provedores Cloud.

**A Solução Cíbrida:**
1.  **Isolamento IPV4:** No `docker-compose.yml`, o Redis e o N8N não farão bind na rede host pública.
2.  **Tailnet Exclusiva:** A máquina OCI será anexada à malha Tailscale corporativa através de Auth Keys efêmeras no provisionamento (Cloud-Init).
3.  **Comunicação N8N ↔ Redis:** Ocorrerá isolada dentro da *Bridge Network* interna do Docker (`sovereign-net`). O N8N enxergará o Redis pelo hostname do container (`redis:6379`).
4.  **Acesso de Usuário ao N8N:** O Sovereign Interface ou o Desenvolvedor só poderão acessar a GUI do N8N conectando-se à VPN Tailscale de seus próprios dispositivos. O acesso ao painel do N8N será mapeado via proxy reverso (Caddy) exclusivamente escutando o tráfego entrante oriundo da interface virtual do Tailscale (`tailscale0`).

*   **Custo do Tailscale:** O Plano Personal atende até 100 dispositivos virtuais, sem restrição de tráfego (P2P nativo), por $0.00.

---

## 4. Estratégia de Cache e Persistência (Redis e N8N)

### 4.1 N8N Queue Mode vs Regular Mode
O N8N permite escalar via Redis (Queue Mode) delegando execuções complexas para Workers paralelos.
Para o RAG Sovereign Pair, adotaremos primeiramente a arquitetura **Regular (Standalone)** visando economia de overhead, mas o Redis atuará em duas frentes vitais:
1.  Armazenamento e rate-limiting das chaves/Sessões (Sovereign API limiters).
2.  Armazenamento temporário de payloads Webhook de grande porte transitando entre o N8N e a FastAPI.

### 4.2 Restrições Redis (Ephemeral Bind)
O Redis será implementado pela imagem leve `redis:alpine` no Docker. A persistência em disco (`AOF/RDB`) não será forçada, garantindo I/O veloz (Efêmero), já que a "Verdade Absoluta" dos dados vive nos arquivos de *Vault* da máquina do usuário.

---

## 5. Matriz de Custos Comprovada

| Serviço/Infra | Fornecedor | Componente | Custo Mensal (USD) |
| :--- | :--- | :--- | :--- |
| Cloud Compute | Oracle Cloud (OCI) | VM A1.Flex (4 Core/24GB) | $0.00 |
| Criptografia / VPN | Tailscale | Plano Personal (Zero-Trust) | $0.00 |
| Proxy e TLS | Caddy via Docker | Certificados Let's Encrypt | $0.00 |
| Workflow Engine | N8N | Docker Community Edition | $0.00 |
| Queue & Cache | Redis | Docker Alpine | $0.00 |
| **Custo Total** | --- | TCO Mensal Estimado | **$0.00** |

---

## 6. Próximos Passos (Plano de Execução)

Para concretizar este estudo nas esteiras CI/CD e nos nodes locais:
1. Aprimorar o manifesto IaC (`infra/terraform/compute.tf`) para validar comportamentos estritos da máquina Oracle.
2. Escrever o script anexo `docker-compose.n8n.yml` declarando as dependências do Redis.
3. Testar localmente simulando o ambiente Prod, invocando webhooks simples do N8N que chamam a rota API `/v1/chat` do Sovereign Pair, atestando o isolamento.
