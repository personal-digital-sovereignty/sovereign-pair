# Tratado II: Implantação e Operações de Infraestrutura

## 1. Arquitetura Onipresente Zero-Cost (Oracle Cloud OCI)

O Sovereign Pair foi forjado para ser financeiramente invisível. Enquanto o seu motor central (o raciocínio da IA) exige processamento brutal e intensivo, o orquestrador (API, Roteador RAG, Autenticação e Gateway de Webhooks do N8N) foi estruturado para rodar sobre **arquiteturas ARM64 com recursos severamente limitados**.

Você pode orquestrar o seu cérebro digital inteiro em uma **Instância Ampere A1 Compute da Oracle Cloud Infrastructure (OCI)**, que fornece 4 núcleos OCPUs ARM e 24GB de RAM perpetuamente por R$0,00/mês.

### 1.1 A Sinfonia do Docker-Compose

Toda a pilha tecnológica (Stack) é containerizada. Não existe dependência física (Node, Python, Linux) instalada na máquina matriz além de `Docker` e uma VPN Mesh.

1.  **Backend FastAPI (`sovereign-api`):** O coração da besta. Recebe consultas em Linguagem Natural, faz a mágica matemática dos *Tokens RAG* no Python 3.12, e orquestra usuários Múltiplos separados.
2.  **Banco de Dados ChromaDB (`chroma`):** A memória fotográfica e espacial. Armazena as fatias do seu cérebro em arquivos lisos imutáveis mapeados direto no HD/SSD.
3.  **Automações N8N (`n8n`):** Os braços e pernas. Conecta-se com o mundo real (Lê seus e-mails, acessa bancos do sistema legado web, trigga calendários automáticos), e avisa a API Soberana quando algo requer cérebro.
4.  **Redis (`redis`):** O cache efêmero ultra-rápido usado exclusivamente para mediar a Escala Horizontal do modo Queue (Fila) do N8N.
5.  **PostgreSQL (`postgres`):** A camada de persistência chata do dia a dia. Guarda logs, senhas sistêmicas e configuração nativa do framework de webhooks.

> [!TIP]
> **Acelerador Juniores (Glossário Rápido):**
> *Docker* é apenas uma "caixa mágica". Em vez de baixar Node.JS, Python, Postgres e dezenas de bibliotecas no seu Windows/Linux (e inevitavelmente enfrentar dores de cabeça com versões conflitantes em um update no futuro), o Docker roda um mini-PC para cada serviço de forma isolada e segura. Para o seu PC, eles não existem. Para rodar a arquitetura inteira corporativa abaixo, você só precisa digitar `docker-compose up -d`. O terminal fará a magia.

---

## 2. Redes de Confiança Zero (Zero-Trust) e Gatekeepers

Ao implantar a aplicação na Internet selvagem (como num Servidor Oracle Cloud padrão), **nunca** abra ou exponha as portas `8000` (API), `5678` (N8N) ou `8000` (Banco Chroma) para a rede pública (IGW / WAN). Relatórios de telemetria de Honeypots cibernéticos (como os dados da SANS Internet Storm Center e da Palo Alto Networks) demonstram consistentemente que scanners automatizados descobrem IPs expostos e portas padrão em questão de minutos após o primeiro Boot, podendo sequestrar o seu banco de dados com Ransomware.

O Sovereign Pair descansa sobre uma VPN Mesh (Hardware Peer-to-Peer, como **Tailscale** ou ZeroTier) que age como *Gatekeeper* criptográfico invisível.

### 2.1 A Conexão Cíbrida (Da Nuvem para Casa)
1. Instale o Tailscale no seu Servidor Nuvem Oracle (O Orquestrador).
2. Instale o Tailscale no seu Desktop Gamer em Casa/Escritório (O Nó de Inferência c/ a Placa de Vídeo).
3. Após fazer login com o mesmo e-mail, ambas receberão um IP Privado da rede profunda P2P iniciado com `100.x.x.x`.
4. No arquivo `docker-compose.yml` da sua Nuvem, amarre (faça o Bind) das portas **estritamente** naquele IP seguro.
   * *Exemplo:* `ports: ["100.x.x.x:8000:8000"]`
5. Como o N8N está rodando na Nuvem e o seu Llama/Ollama de 15GB está físico no conforto da sua casa consumindo sua eletricidade, altere o arquivo `.env` da Nuvem setando a variável `OLLAMA_BASE_URL` para apontar cravado pro IP do Tailscale do seu PC Físico de Casa (`http://100.y.y.y:11434`).

> [!WARNING]
> Hackers Corporativos atencão: Por segurança brutal de fábrica, o daemon/aplicativo do `ollama` instalado em computadores normais atende apenas a porta "Localhost 127.0.0.1". Se a sua Nuvem bater na porta de casa, o PC rejeita. Você é OBRIGADO a configurar o Ollama de casa para ser acessível globalmente inserindo a variável extra `OLLAMA_HOST=0.0.0.0 ollama serve`. E, você **só fará isso** se o roteador do seu quarto não tiver essa porta configurada para Forwarding no seu Roteador, ou seu modem da provedora ISP tiver firewalls rígidos. Senão a vizinhança na rua conversará com sua IA. O Tailscale já resolverá o roteamento de NAT.

---

## 3. Limites Físicos de Inferência de Hardware (Trade-offs Corporativos)

### O Orquestrador em Nuvem (OCI ARM A1 Flex OCPU)
- **O Papel:** Interpretações HTTP pesadas (Text parsing rápido), pontes de Webhooks e Hospedagem de UI de Vue.JS.
- **O Limite:** Inteiramente e comicamente incompetente e incapaz de realizar qualquer cálculo de Inferência Local `nomic-embed`, `cuda` de rede neural em qualquer tempo razoável por não possuir NPU (Neural Processing Unit).
- **A Operação:** Cospem e analisam Sistema de Prompts gigantescos (ex: 16 mil tokens do `The Doctor`) pela rede da FastAPI em menos de `< 200 milissegundos`.

### O Nó de Cérebro/Inferência (PC de Casa / Xeon Server x86_64 Ryzen / RTX)
- **O Papel:** Rodar cálculos brutos puramente pesados e caríssimos (`Ollama` em rede isolada).
- **O Limite:** Físicamente emparedado e agrilhoado ao ÚNICO tamanho da memória VRAM que você tem dinheiro pra comprar.
- **A Operação:** 
   - *Se as restrições orçamentárias de Hardware forem altas (8GB a 12GB VRAM Ex: RTX 3060/4060):* Recomenda-se a adoção de modelos altamente otimizados e Quantizados, como o eficiente `qwen2.5:0.5b` (Roda em dispositivos móveis modernos), `llama3.2:1b` ou os eficientes da Mistral/Google (Gemma).
   - *Se houver robustez Corporativa/Enterprise (24GB a 48GB VRAM Ex: RTX 3090/4090 ou MAC Studios M2 Max Ultra de 128GB unificado):* O sistema ganha tração para processar modelos titânicos próximos do estado-da-arte (Ex: `llama-3-70b-instruct`) com janelas contextuais massivas, garantindo raciocínio denso e analítico sem condensação severa.

> [!NOTE]
> Regra de ouro: Arquiteturas de Orquestração costumam derrubar chamadas de webhooks que demoram após 2 minutos de forma genérica para evitar sobrecarga de memória do Windows (o famoso Axios Timeout). Assim... se o Servidor da Nuvem chamar seu PC Gamer velhinho, e ele demorar 4 minutos matutando pra cuspir o Parágrafo do OLLAMA e enviar, a Nuvem já mandou seu PC pastar. Para contornar e resolver esta limitação arquitetural, nós injetamos um limite superior elástico passivo no back-end (Variável `REQUEST_TIMEOUT="300.0"`). Isso impõe e obriga o servidor Nuvem do N8N a aguardar pacientemente pelo processamento do LLM Local por até 5 minutos, sem travar e sem retornar falhas assíncronas de `500 Internal Server Error`. Abrace o tempo de inferência do Local-First.
