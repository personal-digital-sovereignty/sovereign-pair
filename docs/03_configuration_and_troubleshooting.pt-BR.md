# Configuração, Operações e Troubleshooting

## 1. Topologia de Variáveis de Ambiente (`.env`)

A arquitetura do projeto isola informações e chaves restritas mantendo-as estritamente no arquivo `.env`. Por se tratar de configuração crítica, o arquivo `.env` não é controlado pelo versionamento Git (regra disposta no `.gitignore`). Todos os parâmetros que coordenam o comportamento e a identidade da instância devem ser definidos no diretório base a partir de um *.env.template*.

### 1.1 Configuração de Endpoints Primários e Modelos
| Variável | Escopo de Configuração | Uso e Definição |
|---|---|---|
| `OLLAMA_BASE_URL` | Roteamento HTTPS / Rede | Define o endereço do serviço de inferência Ollama. Em nuvens sob a VPN Tailscale, informar o correspondente IP seguro (Ex: `http://100.x.x.x:11434`). A máquina host necessita autorizar escuta em `0.0.0.0` para prover a comunicação de rede P2P de forma adequada. |
| `LLM_MODEL` | Processamento / Inferência | Identifica o modelo carregado no raciocínio conversacional (Ex: `qwen2.5:0.5b`). O modelo precisa ser instanciado via CLI através de: `ollama pull [nome-do-modelo]`. |
| `EMBED_MODEL` | Transformação Matemática | Trilha o nome do pacote de processamento de *Embeddings*, responsável por converter arquivos literários em vetores do banco de dados relacional. O padrão semântico multi-idioma recomendado é o `bge-m3` (1024 dimensões). Caso o projeto restrinja-se ao idioma inglês e possua limitações de disco O.S, a troca referencial voltada para `nomic-embed-text` (768 dimensões) é permitida antes da indexação primária. |
| `REQUEST_TIMEOUT` | Escala de Tráfego HTTP | Tempo (em segundos) limite de espera assíncrona tolerado pela API nas chamadas externas. Em hosts com tempo de latência não usual nas interações de embeddings ou instâncias de Ollama hospedadas sem auxílios CUDA, é coerente calibrar a variável padrão entre `120.0` até `300.0` para estabilizar consultas com falhas prematuras 504. |

> [!NOTE] 
> ▫️ **Loader Paramétrico Pydantic:** `src/api/config.py`
> ▫️ **Gerenciador de Módulos (Builder):** `src/engine_builder.py`

### 1.2 Customização Parametrizada de Sistema (System Prompt)
Os artefatos abstratos submetidos ao Agente Base na primeira solicitação contêm atributos comportamentais descritivos baseados nos parâmetros lidos via Sistema Operacional.
| Variável | Efeito Sistêmico no Fluxo LLM |
|---|---|
| `OWNER_NICKNAME` | Nome utilizado pela inferência para designar o locutor padrão nas operações. |
| `SOVEREIGN_NAME` | Parametriza de forma técnica como a API irá formalizar respostas diretas sobre a própria identidade. |
| `LANGUAGE` | Impõe controle explícito limitando os desvios de gramática do bot (mantendo sempre em PT-BR ou EN), estabilizando iterações subsequentes e processos determinísticos com requisições JSON. |
| `OCCUPATION` | Formata o formato das respostas priorizando campos específicos de atuação (Ex: Assumir `Engenharia DevOps SRE` adequará respostas longas contendo formatação Shell Script/YAML ao invés de propostas genéricas e não aplicáveis). |

> [!NOTE] 
> ▫️ **Inicialização de Prompt Base Contextual:** Controlado pela função `build_chat_engine()` dentro de `src/engine_builder.py`. 

---

## 2. Manutenção Operacional Vetorial

### 2.1 Resolução de Inconsistência Analítica entre Hashes
- **Natureza do Problema:** Alertas categorizados apontando exceções como *NotFoundException* ao longo da rotina RAG no Web Frontend demonstram perda ou conflito entre o histórico cacheado na interface O.S (`.ingestion_history.json`) e os IDs reais indexados nas partições SQLite.
- **Causa Potencial:** Este desvio da fidelidade métrica do arquivo perante banco é resultado usual de scripts em rotinas seriais que foram abortados ou corrompidos durante operações sistêmicas na máquina host. (Ex: Perda abrupta de energia ou paradas via `Ctrl+C` no CLI de inserção sem o sync apropriado de log).
- **Procedimento Limpo de Restauração:** Pela integridade base preservada e lastreada nos originais do sistema de arquivos O.S físico (Suas notas Markdown não são afetadas), a exclusão total do esquema vetorial SQLite contido no subdiretório local garante imediata re-sincronia coerente sem risco de dados perdidos. Ao reiniciar a instância do Worker (File Watcher), todos os diretórios voltam a ser percorridos e salvos em tabelas estáveis.

```bash
# Workflow de Manutenção: Remoção de DB e Index Logs Corrompidos
rm -rf data/chroma_db
rm -rf data/sovereign_memory.db 
rm data/.ingestion_history.json

# Remapeamento Completo Limpo de Rotinas I/O Locais
python src/ingest.py 
```

> [!NOTE] 
> ▫️ **Script de Tratamento de Dados:** Centralizado através da interface `src/ingest.py`.

---

## 3. Tratamento de Retornos RAG Sem Resultados

- **Sintomas da Requisição:** Clientes integrados comunicando-se via N8N ou na API Direta recebem resposta regular via Payload com conteúdo sintático de predefinição nula (`Empty Response`), que oculta e encerra o fluxo conversacional inesperadamente.
- **Motivo Arquitetural RAG:** Tal ocorrência faz menção técnica aos design nativos submetidos a ferramentas referenciadas do provedor principal `LlamaIndex` perante classes contextuais de chat engine. Se a semelhança dos logs submetida no input em direção aos bancos SQlite constatar relevância correspondente a zero ("0 nodes"), a Engine declinará envios da consulta para poupar recursos, devolvendo respostas nulas imediatas sem envolver a conversação final com o processador LLM base. Frequentemente documentado no estágio Zero (início do usuário no fluxo) por falta de histórico nas tabelas.
- **Fallbacks Restritivos e Roteamento Bypass:** Visando prover comunicação em todas as consultas da rede independentemente de erros RAG (especialmente para consultas abertas e generativas de uso padrão LLM Livre), criou-se a implementação interceptativa logada como **Sovereign Bypass**. Identificada a diretiva limitante e vazia associada ao LlamaIndex no ciclo da FastAPI route handler (`routes.py`), ela re-roteará pontualmente seu log transacional num Request Alternativo Puro isento de validação no SQlite e que invoca respostas interativas padrão do bot diretamente. Essa intervenção garante fluidez irrestrita das interações a partir de serviços N8N e previne telas silenciosas no Frontend decorrentes do ambiente vetorial limitado O.S em startups iniciais.

> [!NOTE] 
> ▫️ **Bypass HTTP Operativo API:** Direcionamento e verificação localizados estruturalmente na raiz do Handler Rest: `src/api/routes.py`.
