# Configurações, Operações SRE e Troubleshooting

## 1. Topologia de Variáveis de Ambiente (`.env`)

A arquitetura do projeto aplica isolamento seguro versionando os arquivos `.env` exclusivamente através do repositório ignorado (`.gitignore`), garantindo proteção modular a configurações críticas de infraestrutura. Todos os parâmetros relacionados à autenticação sistêmica e endereçamento de rede devem ser alocados no arquivo passivo `.env` na raiz do host executivo.

### 1.1 Configuração de Modelos e Endpoints Primários (Core)
| Variável | Escopo de Configuração | Definição Requerida |
|---|---|---|
| `OLLAMA_BASE_URL` | Roteamento HTTPS / Rede | Endereço do Servidor Inferencial Ollama. Em implantações isoladas na nuvem conectadas à malha VPN Tailscale, o roteamento deverá utilizar o IP da interface segura privada (Ex: `http://100.x.x.x:11434`). Na máquina que hospeda as GPUs, o serviço deve obrigatoriamente operar com Listener `0.0.0.0` para aceitar a conexão P2P (`OLLAMA_HOST="0.0.0.0"`). |
| `LLM_MODEL` | Processamento / Inferência | Define a tag de modelo neural base do raciocínio local (Ex: `qwen2.5:0.5b`). O binário deve ser baixado previamente executando as rotinas `ollama pull [nome-do-modelo]`. |
| `EMBED_MODEL` | Transformação Matemática | Determina a dependência nativa do motor de *Embeddings*, responsável por projetar vetores textuais no plano dimensional do Vector DB. O modelo padrão focado em semântica multilíngue de alta carga é o `bge-m3` (1024 dimensões). Aplicações com limitações severas de hardware (I/O Lógico) ou com finalidade exclusiva em idioma Inglês podem sofrer downgrade funcional definindo `nomic-embed-text` (768 dimensões) para otimizar velocidade no File-System local. É expressamente impedida a alteração dessa variável após a primeira inicialização vetorial (Requer Drop Completo do Banco de Dados para efetivar troca). |
| `REQUEST_TIMEOUT` | Escala de Tráfego HTTP | Padrão default `120.0`. Em arranjos de provisionamento que processam contexto massivo (128K em requisições N8N iteradas via Cloud Oracle ARM ou host CPUs fracamente unificadas), estabelece-se elevar este referencial de timeout global a `300.0` (segundos), dilatando o limite de persistência das chamadas para evitar retornos precoces de 504 Gateway Timeout e/ou 500 Internals. |

> [!NOTE] 
> ▫️ **Loader Paramétrico Pydantic:** `src/api/config.py`
> ▫️ **Bootstrap Físico dos Modelos:** `src/engine_builder.py`

### 1.2 Customização Parametrizada da Identidade do Sistema
O sistema preenche as definições de escopo abstrato do LLM base (System Prompt) automaticamente através de variáveis de comportamento restritivas carregadas na Engine.
| Variável | Propósito Sistêmico no Fluxo Inferencial LLM |
|---|---|
| `OWNER_NICKNAME` | Termo referencial embutido que condiciona a nominalidade das validações durante sessões diretas do sistema. |
| `SOVEREIGN_NAME` | Parametriza nativamente a identificação estrutural assumida da inteligência instanciada pela biografia mestre. |
| `LANGUAGE` | Regra restritiva acoplada ao System Prompt que estabiliza o padrão gramatical e de saída, evitando degradação ocasional para idiomas concorrentes nos processos generativos base do LLM, fixando as resoluções da resposta JSON e fluxos N8N. |
| `OCCUPATION` | Formata restritamente o jargão técnico esperado em chamadas generalizadas RAG (Ex: Assumir um escopo voltado como `SRE Engineer DevOps` garante respostas pautadas sumariamente na área exata da sintaxe requisitada, coibindo prolixidade informal do LLM). |

> [!NOTE] 
> ▫️ **Construtor Condicional e Inicialização do Prompt Local:** Bloco da função `build_chat_engine()` referenciada estritamente no `src/engine_builder.py`. 

---

## 2. Procedimentos Operacionais Básicos para Integridade Vetorial

### 2.1 Resolução de Estado Assíncrono (Inconsistência Analítica entre Hashes)
- **Cenário de Fuga Estrita de Hashes:** Alertas ativados de *NotFoundException* atestados em arquivos persistentes pelo Dashboard Web Frontend, explicitando descasamento explícito da indexação atestando em metadados (`.ingestion_history.json`) contrastando com estado efetivo SQL local.
- **Root Cause Indexação/Gravação Rápida:** Roturas severas no framework indexacional serial de I/O em banco SQLite (modos de commit WAL interrompidos) gerados por Desligamentos Intempestivos O.S (SIGKILL/Kernel Panics), paradas por timeouts em shells estritos na Ingestão, ou falhas latentes processando volumes massivos de sub-pastas (Batch process at Night via CLI).
- **Procedimento Limpo de Restauro da Malha SQLite:** Atendendo que o padrão persistido raiz permanece blindado isoladamente nas notas literais *Markdown* ou *Arquivos Brutos (Vault)*, opera-se o saneamento da falha realizando *Drop Databases* integrais de todas instâncias vetoriais ou relacionais vinculantes. Devido pauta do VectorDB, na posterior ascensão executiva do *File Watcher* OS o repositório é completamente percorrido validado recriando as matrizes coerentes de alta fidelidade sem corrompimentos.

```bash
# SRE Local Runbook: Exclusão Segura Completa da Indexação de Vectors e LogHistória
rm -rf data/chroma_db
rm -rf data/sovereign_memory.db 
rm data/.ingestion_history.json

# Processo disparado via Python puramente serializado reconstruindo I/O.
python src/ingest.py 
```

> [!NOTE] 
> ▫️ **Script Processual Recuperativo:** Utilitário contido estritamente em `src/ingest.py`.

---

## 3. Tratamento Sistêmico de Retornos Vazios RAG ("Empty Response")

- **Sintomas da Requisição:** Clientes lógicos, como Webhooks de integrações externas (N8N) e API endpoints (FastAPI Rest), são respondidos sob status regular (Code HTTP Success) encapsulando estritamente formato devoluto fixo `Empty Response`, providenciando execução rápida mascarando paralização silenciosa RAG.
- **Root Cause Exata Identificada:** Paradigma sistêmico intencional provocado pela modelagem base LlamaIndex `CondensePlusContextChatEngine`. A ferramenta emite interrupções arbitrárias nos processos das Threads base LLM se a contagem do índice validador de correspondência na query perante às alocações vetoriais do Vector DB instanciar valores precisos exatos contendo $0$ nós ou `nodes` disponíveis no cálculo logístico. Manifesta-se geralmente originado entre Requisições textuais cujo escopo alvo desrespeite acuracidade métrica dos metadados atrelados, ou, essencialmente durante *Onboarding Users* nos sistemas RAG Corporativos que demandem o primeiríssimo acesso desprovidos de bases históricas populadas (Tenants Empty Initial State), finalizando execução sem enviar consulta limpa do prompt diretamente ao chat natural base LLM.
- **Tática Mitigadora Interna (Conversão RAG para Non-RAG API Bypass):** Rescindindo as deficiências de bibliotecas engessadas open-source lidas no formato original (Empty Flow), integrou-se à raiz nativa o sub-sistema validacional ativo **Sovereign Bypass** na lógica nativa. Rotina de controle (alocada estritamente na árvore `routes.py`) capta retornos restritos com a String morta pré-formatada do LlamaIndex e defere instantaneamente fallback de execução via injeção sintética nos construtores padrões LLM puros (`_llm.astream_chat(messages)`), preenchedo-o via acúmulo de memórias temporais associando ao System Prompt. Expurga o motor Vetorial isolado limitativo na etapa específica, salvaguardando uso contínuo da Interface da Inteligência Computacional livre, prevenindo interrupção sistêmica (Blank Pages) provindas do frontend N8N ou falhas lógicas perante tenants neófitos em infra.

> [!NOTE] 
> ▫️ **Implementação Estrita Bypass (FastAPI HTTP Routing):** Invocação restritiva validativa orientada pelo bloco comparativo da variável string avaliando falhas de retorno instanciadas na rotina de base `src/api/routes.py`.
