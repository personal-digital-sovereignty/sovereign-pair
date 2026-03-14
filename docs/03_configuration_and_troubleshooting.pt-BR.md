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

## 3. Dependência Legada: A Vulnerabilidade "Empty Response" LlamaIndex
Versões experimentais primárias relativas do Sovereign Pair acoplaram-se ao framework `LlamaIndex` para instanciamento analógico. Procedimentos isolativos testados auditaram comportamentos arbitrários nocivos restritivos do instanciador base.

- **Motivo Arquitetural:** Tal ocorrência nativa referia-se ao design restritivo contido na biblioteca base do provedor `LlamaIndex` (Classes contextuais Python). Se as operações baseadas no input aos bancos apontassem "0 nodes", a Engine Python declinava a execução e devolvia falhas estruturais fixas "Empty Response" impossibilitando conversações triviais (Ou tentava, via Silent Fallbacks, alcançar nós comerciais OpenAI transpondo o cerco privativo da rede local).  
- **Resolução Cíbrida Definitiva (Adoção Rust/Axum):** Visando prover comunicação e isolação total da infraestrutura, elaborou-se primeiramente o conceito interceptativo `Sovereign Bypass` (via Python log hooks). No entanto, o nível de restrição exigido no formato Zero-Trust forçou a eliminação absoluta das abstrações comerciais de dependência Python (`LangGraph`, `LlamaIndex`). As execuções primárias restritas RAG transicionaram ao domínio das implementações compiladas via **Rust (`Axum` e `Tokio`)**, com matrizes SQLite (`sqlite-vec`) lidadas primariamente no terminal direto com o inferenciador `Ollama`. O sistema não apresenta mais bloqueios sistêmicos decorrentes de ambientes operacionais vazios (New Startups).

> [!NOTE] 
> ▫️ **Antigo Bypass HTTP API (Obsoleto):** Anteriormente localizado estruturalmente na raiz do Handler Rest: `src/api/routes.py` (Python FastAPI). Padrão reescrito sobre Core Rust e devidamente removido da arquitetura limitante legada.
