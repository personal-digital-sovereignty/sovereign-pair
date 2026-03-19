# Manual do Arquiteto B2B: Conectando a Oracle Cloud (OCI) ao Sovereign Pair

O Sovereign Pair possui a capacidade "Bring Your Own Compute" (BYOC) através do módulo **Sovereign Fleet**. Isso permite que você expanda seu Motor RAG para fora do seu hardware local (Ryzen/Mac), despachando a carga inferencial pesada para instâncias robustas e gratuitas (como a ARM Ampere A1 na Oracle Cloud), mantendo a integridade lógica e os *seus dados seguros na sua própria máquina local*.

Neste guia, passaremos pelo processo de Aterramento (Setup do Node) e Conexão (Handshake) entre a sua Cloud Pessoal e a sua Interface Local.

---

## Passo 1: O Nódulo na Orcale Cloud (OCI)

1. Crie uma conta na Oracle Cloud (Elegível ao *Always Free*).
2. Lance uma **Instância VM (Compute)**. Sugere-se a `VM.Standard.A1.Flex` (ARM) com 4 OCPUs e 24GB de RAM (Excelente para modelos `llama3.2` ou `phi3`).
3. Instale o Sistema Operacional **Ubuntu 22.04** ou **24.04**.

## Passo 2: O Despertar do Motor Ollama
Acesse via SSH o terminal do seu servidor recém-criado:
```bash
ssh -i sua_chave.key ubuntu@<IP_PUBLICO_DA_ORACLE>
```

Instale o motor Ollama via script oficial:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### O Desafio do BIND ABERTO
Por padrão, o Ollama roda atrelado ao `127.0.0.1` (localhost), ou seja, fechado para o mundo. Você deve dizer ao motor para "escutar" portas externas.

1. Crie um arquivo override para o `systemd`:
```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo nano /etc/systemd/system/ollama.service.d/environment.conf
```

2. Cole este conteúdo dentro (Isso permite host externo e tira limitadores de CORS pro Sovereign Pair funcionar perfeitamente):
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_ORIGINS=*"
```

3. Recarregue os processos O.S:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

---

## Passo 3: O Elo de Fogo (Tailscale VPN)
Você não deve simplesmente abrir a porta 11434 na Internet (VCN Ingress) para todos usarem sua GPU de graça. Usaremos uma VPN Mesh Zero-Config: **Tailscale**.

1. Crie sua conta em [Tailscale.com](https://tailscale.com)
2. **Na Máquina Local (Seu Notebook/Sovereign Master)**, instale e logue no Tailscale. Ele te dará um IP interno da VPN (Ex: `100.80.y.z`).
3. **Na Oracle Cloud (SSH)**, instale e logue na mesma conta:
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Perfeito! O Tailscale dará à sua Oracle Cloud um IP mágico intocável pela Internet Cívil (Ex: `100.116.x.y`).

---

## Passo 3.5: Inicialização do Cérebro Cíbrido (Systemd Service)

Caso o Cloud-Init não consiga completar o Boot automatizado pela falta da sua chave (ou falhas na internet nativa), o Sovereign Pair dispõe de um script salva-vidas. Após a instância criar vida:

1. **Preencha sua Chave (Tailscale Auth) nas Variáveis de Ambiente:**
Como as chaves sensíveis não são enviadas para o Github, você precisa declarar sua identidade na nuvem:
```bash
sudo nano /opt/sovereign-pair/.env
# Edite a linha TS_AUTHKEY=tskey-auth-... colocando a sua chave real do Tailscale
```

2. **Ative o Túnel Invisível:**
Trave a máquina virtual na sua malha neural Tailscale privada:
```bash
sudo tailscale up --ssh --hostname=sovereign-coder
```

3. **Permissão de Execução do Motor Standalone Binary:**
Por padrão (segurança estrutural), o usuário `ubuntu` não possui acesso direto ao socket central do Standalone Binary (`unix:///var/run/docker.sock`), o que lançará um erro "permission denied" se você rodar comandos limpos. Liberte o seu usuário:
```bash
sudo gpasswd -a ubuntu docker
# Reinicie o terminal ou reconecte (SSH) para o grupo Standalone Binary entrar em vigor
```

4. **Estruture os Cofres de Dados O.S (Evite Crash do RAG API):**
A API do Sovereign roda com extrema segurança via `soveruser` (UID 1000). Se o Standalone Binary compor as pastas vazias no Host primeiro, ele o fará como `root` e a API travará tentando escrever os bancos de dados SQLite e vetores. Crie e delegue os domínios:
```bash
sudo mkdir -p /opt/sovereign-pair/data/raw_docs /opt/sovereign-pair/data/vault
sudo chown -R 1000:1000 /opt/sovereign-pair/data
```

5. **Suba os Motores de RAG / N8N:**
Inicie o enxame Standalone Binary para orquestrar o motor vetorial e os fluxos lógicos!
```bash
cd /opt/sovereign-pair/infra/docker/
sudo docker compose up -d
```

---

## Passo 4: O Handshake B2B (No Sovereign Pair)

Por fim, vamos ensinar sua Inteligência o mapa de roteamento exato:

1. Abra seu Sovereign Pair Local.
2. Navegue até Configurações (A engrenagem ⚙️ no canto inferior esquerdo).
3. Na Tab `Identidade Digital`, no item "Provedor LLM", garanta que **Ollama** esteja assinalado.
4. No card **Roteamento do Motor RAG**, clique em `Gerenciar Nós`.

![](/home/jefersonlopes/.gemini/antigravity/brain/77acd940-20d7-43e2-898e-a77f69abe81c/media__1773349211344.png)

5. Preencha:
   - **Nome:** "Oracle Cloud A1"
   - **URL:** `http://<IP_DO_SEU_TAILSCALE_DA_ORACLE>:11434` (Exemplo: *http://100.116.32.41:11434*)
6. Conclua clicando em **Adicionar à Frota** e selecione-o na combobox principal.

### Conclusão e Teste de Pulso
Digite `llama3.2` ou `deepseek-r1:8b` na caixa "Baixar nova extração" e clique em **Baixar**. 

Observe a mágica acontecer: O seu navegador, através da ponte do Sovereign Pair, orquestrará um _PULL_ na sua máquina alojada nos datacenters corporativos da Oracle Cloud. O peso de processamento está oficialmente Exilado do seu Notebook! 🛡️

*Seja bem vindo à Soberania Estrutural.*
