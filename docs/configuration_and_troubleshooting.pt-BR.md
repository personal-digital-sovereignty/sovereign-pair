# Guia Corporativo de Configuração e Troubleshooting

**Status:** Produção (Cibrid & Zero-Trust)
**Engine:** Sovereign API (FastAPI) & Sensus Vault
**Requisitos Básicos:** Python `3.11` ou `3.12` (Python 3.14 não suportado devido à pydantic V1). 

Este manual destina-se a Engenheiros SRE e Administradores de Sistema responsáveis pela configuração e sustentação do Sovereign Pair RAG, cobrindo o particionamento de variáveis de ambiente (`.env`) e os protocolos de mitigação de falhas comuns.

---

## 1. Topologia de Variáveis de Ambiente (`.env`)

O projeto não rastreia arquivos de ambiente. Toda a segurança criptográfica e alinhamento de infraestrutura devem ser declarados via um `.env` estrito alocado na raiz do projeto.

### 1.1 Configuração de Modelos (Inteligência Central)
| Variável | Escopo | Uso Padrão | Observações SRE |
|---|---|---|---|
| `OLLAMA_BASE_URL` | Rede | `http://localhost:11434` | Se operado remotamente num *Local Node* da rede Tailscale, use o IPv4 da Tailnet (Ex: `http://100.x.x.x:11434`). Lembre-se de configurar `OLLAMA_HOST="0.0.0.0"` no daemon alvo. |
| `LLM_MODEL` | Inferência | `llama3.2` ou `qwen` | Define o peso computacional primário. O modelo escolhido deve ser previamente injetado no cache do Docker/Daemon (`ollama pull [name]`). |
| `EMBED_MODEL` | Vetorização | `nomic-embed-text` | Responsável pelo mapeamento em hiper-espaço de 768 dimensões. O modelo de *Embedding* nunca deve ser alterado após a subida do ChromaDB, caso contrário, hashes corrompidos anularão o banco. |
| `REQUEST_TIMEOUT` | Networking | `120.0` | Defina `180.0` para *Hardware On-Premises* ou em nuvens Free Tier da Oracle (A1.Flex de baixo processamento genérico). |

### 1.2 Mecânica Vector Database e Contexto
| Variável | Escopo | Recomendado | Comportamento |
|---|---|---|---|
| `CHROMA_COLLECTION_NAME` | RAG | `sovereign_knowledge` | Isolação por *namespaces*. Permite RAGs multi-tenant num mesmo nó apontando IPs distintos. |
| `CHUNK_SIZE` | Parsing Text | `1024` | Físico de Tokens absorvidos antes do fracionamento. Ideal para `nomic`. |
| `CHUNK_OVERLAP` | Parsing Text | `200` | Memória elástica marginal para não decepar tópicos lógicos na transição Vetorial. |
| `MAX_WEB_SEARCH_RESULTS` | Cibrid | `3` | Define volume de Scraping para injeção via Web Search. Volumes maiores demandam Timeouts superiores. |

### 1.3 Personalização de Identidade Parametrizada
| Variável | Uso e Injeção no Prompt de Sistema |
|---|---|
| `OWNER_NAME` | Seu nome corporativo. Aciona um cumprimento formal do RAG. |
| `OWNER_NICKNAME` | Apelido ou *Callsign*. O assistente referenciará comandos diretos desta forma. |
| `SOVEREIGN_NAME` | Nome da I.A (Ex: *Sovereign*, *Jarvis*). Regula a biografia com base na entidade. |
| `LANGUAGE` | Regula o output. Force `Português do Brasil` ou `US English` para suprimir a volatilidade natural de Modelos LLM multilíngues. |
| `GEOLOCATION` | Base estática para Search Queries. Ex: `São Paulo, Brasil`. Substitui a necessidade do envio nativo via Browser de coordenadas. |
| `OCCUPATION` | Formata o jargão. Ex: `SRE Senior` obriga a máquina a adotar tom técnico elevado. |

---

## 2. Padrões Ouro de Solução de Problemas (Troubleshooting)

Problemas de rede e colapsos Vetoriais são mitigáveis seguindo matrizes de rastreio estritas. Nunca exclua bancos sem o isolamento prévio de logs.

### 2.1 Colapso Vectorial (`input length exceeds the context length`)
*Erro Status 400 no ChromaDB.*
- **Incidente:** O modelo de Embedding rejeita pacotes densos cujos caracteres embutidos violaram o Token Limit do modelo local (Comum em documentos convertidos de PDF/OCR).
- **Resolução de Engenharia:** 
  1. No `.env`, reduza a volumetria estourando `CHUNK_SIZE` (Rolete para trás para `512` em casos piores, e recaia para `128` se o modelo assim pedir, como no caso do `all-minilm`).
  2. Submeta nova varredura de Ingestão após limpar o flag `data/.ingestion_history.json`.

### 2.2 Desconexão Zero-Trust com Ollama (Timeout ou TCP Refusal)
*A UI congela tentando invocar o endpoint FastAPI gerando `500 Internal Server`.*
- **Incidente:** O nó Inference (Máquina Gamer Ryzen) se desatrela do Nó Orchestrator (Oracle Cloud) ou vice-versa.
- **Resolução de Engenharia:**
  1. Obtenha *shell* via `tailscale ping [Node]`. Se não pingar, a barreira subjacente foi exporádicamente cortada por refrigeração, erro ISP ou ACL.
  2. Garanta que o servidor Inferência iniciou o Docker Ollama mapeando o Gateway. O parâmetro padrão `OLLAMA_HOST` em distribuições SystemD inviabiliza NATing externo.
  3. No Linux de Inferência: Adicione um arquivo `/etc/systemd/system/ollama.service.d/override.conf` contendo `Environment="OLLAMA_HOST=0.0.0.0"`.

### 2.3 Problemas de Mismatch no Python
*Warnings na sintaxe do Pydantic no Boot up do backend uvicorn.*
- **Incidente:** O projeto tentou rodar nativamente em Python `>= 3.13` ou superior, forçando quebra em livrarias *Legacy* (como o motor ChromaDB).
- **Resolução de Engenharia:** O ambiente corporativo rege isolacionismo completo de pacotes. Aborte ambientes em falho, invoque `pyenv` instalando a ramificação *patch* 3.12.x estrita, e recrie seu V-Env `python3.12 -m venv .venv` ignorando a máquina Host global.

### 2.4 Corrupção de Estado Incremental (Hashes Divergentes)
*A varredura diz que o arquivo não existe, mas visualizador Markdown na UI prova o contrário.*
- **Incidente:** Descolamento entre o banco `.json` Histórico e a indexação nativa do `ChromaDB`. (Geralmente causado por *Hard Resets* acidentais durante vetorização).
- **Resolução de Engenharia:** Resete o cérebro vetorial.
```bash
# SRE Runbook: Purmagem Absoluta de Vetor DB.
rm -rf data/chroma_db
rm data/.ingestion_history.json
python src/ingest.py # Reforce o parâmetro Manual Full
```

## 3. Logs Analíticos
Toda telemetria do Motor da API rola por `stdout`. Encadeie com gerenciadores de *Log-Rotation* corporativos. Para logs densificados de Raciocínio (Agent *Thoughts*), injete `AGENT_VERBOSE=true` no env. A I.A passará a "Falar consigo mesma" na saída de consola, expondo o seu fluxograma do *ReAct* para depuração avançada Cíbrida.

---

## 4. Integração Model Context Protocol (MCP)

O Sovereign Pair expõe nativamente seus motores internos (The Doctor, The Nurse) e o contexto da `Sensus Vault` através do **Padrão MCP** da Anthropic. Esta capacidade transforma o backend num "Módulo de Expansão Cognitiva Local-First" para IDEs corporativos como VSCode, Cursor e Cline (OpenCode).

### 4.1. Soberania Local-First Absoluta
O esquema de conexão opera estritamente via **Stdio** (Standard Input/Output) Inter-Process Communication (IPC). O IDE (como o OpenCode) inicia um socket silencioso em memória. Nenhuma informação de telemetria ou log **transita pela rede**, garantindo uma arquitetura de código Zero-Trust.

### 4.2. Configuração do Cliente IDE (VSCode / Cline)
Para injetar a Sovereign Vault diretamente no seu fluxo de trabalho de programação, anexe o bloco a seguir na configuração JSON do seu cliente MCP (`settings.json` ou painel do Cline/OpenCode):

```json
"mcpServers": {
  "sovereign-pair": {
    "command": "python",
    "args": ["-m", "src.mcp_stdio"],
    "env": {
      "PYTHONPATH": "/caminho/absoluto/do/sovereign-pair"
    }
  }
}
```

### 4.3. Utilização Prática (O Cérebro Corporativo)
Uma vez conectado, o Agente de IA dentro do seu Editor de Código lerá automaticamente seus arquivos Markdown do diretório `VAULT_DIR` (*Resources*) **antes** de propor arquiteturas. Além disso, a IA passará a ser capaz de interrogar dinamicamente o seu Banco Vetorial (*via ferramenta sensus_vault_search*) para buscar as suas regras de negócios fechadas, escudando e blindando o seu projeto proprietário de "alucinações genéricas" encontradas na internet.
