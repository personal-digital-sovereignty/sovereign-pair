# Pipeline RAG e Estrutura de Indexação

A arquitetura do Sovereign Pair utiliza um framework padronizado para coordenar a recuperação precisa de informações baseadas no processamento de Geração Aumentada por Recuperação (RAG). 

## 1. Processos de Ingestão e Preparação de Dados

A extração das pastas nativas e arquivos em texto (como os formatos `.md` e `.pdf`) alocados dentro do Sensus Vault obedece às seguintes rotinas encadeadas:

1.  **Parsing de Documentos:** Etapa inicial para uniformizar e consolidar o conteúdo bruto a ser formatado. A função responsável extrai formatações HTML extras e artefatos de marcação, normalizando os parágrafos convertendo-os em bytes e cadeias textuais semânticas puras com integridade Markdown (UTF-8).
2.  **Fragmentação (Chunking):** A inserção direta de artigos nativos gigantes nos contextos do backend LLM causa saturação, estourando limites do modelo na verificação local. Todo documento ingerido será fragmentado de acordo com uma janela limite estabelecida estaticamente pela plataforma na sintaxe (`CHUNK_SIZE`), delimitada usualmente aos níveis normativos em 512 a 1024 tokens por partição base. A política de sobreposição residual (`CHUNK_OVERLAP`) atua paralelamente copiando um número fixo das ultimas instâncias (ex: 200 tokens do término anterior) preservando ligações temáticas semânticas coesas e reduzindo interrupções disjuntas dos fragmentos criados.
3.  **Matriz Vetorial Numérica (Embeddings):** Transforma o componente estruturado (Chunks) numa identificação posicional com plano hiperdimensional gerido por uma malha vetorial contínua (~1024 pontos). Processado de preferência através da rede nativa de suporte a processamento natural (NLP Engine / `bge-m3`), torna possível a inferência multi-idioma desprendendo sua correlação matemática ao texto em múltiplos idiomas. 
4.  **Gravação no Banco Relacional O.S:** Registro nativamente estruturado acoplando atributos no banco contínuo SQL. Utiliza a biblioteca modular SQLite provida na aplicação física (tabela unificada de persistência Vector Support) consolidando instâncias do conhecimento no drive.

> [!NOTE] 
> ▫️ **Serviço de Processamento de Ingestão (Python):** `src/ingest.py`
> ▫️ **Serviço Monitor de Sistema de Arquivos (OS Watcher):** `src/core/watcher.py`

---

## 2. Padrões de Busca Híbrida 

Durante os acessos externos (API e PWA Web UI), realiza-se o pareamento simultâneo com motores paralelos operando avaliações independentes em recuperadores (Retrievers) variados. 

### 2.1 Busca Vetorial Semântica (Aproximação Espacial)
Calcula métricas e distância cossenoidal do prompt inserido com correspondências já existentes na malha do banco de dados (SQLite Vector). Esse parâmetro extrai documentos que compartilhem relação de ideias contextuais com a requisição, ignorando palavras-chave exatas semânticas não mapeadas que divergem literamente de sinônimos idênticos.

> [!NOTE] 
> ▫️ **Construtor de Roteamento RAG:** Referenciado metodicamente pelo arquivo `src/engine_builder.py`

### 2.2 Controle de Especificidades Lexicais (Busca por Termos BM25)
Equilibra imprecisões e amplificações provocadas exclusivamente pelas matrizes relacionais abstratas do motor Vetorial. Foca especificamente pelo sistema de frequência do algoritmo nativo para referenciar os caracteres literais providos sem alteração ao prompt (Busca clássica Keyword ex: Pesquisa unicamente do status "Erro IPv4 429"). Combinadas na saída logada inicial, ambas métricas sofrem atribuições baseadas em ranqueamento combinando score das metodologias pela infraestrutura integrativa via RRF (Reciprocal Rank Fusion).

> [!NOTE] 
> ▫️ **Retriever Lexical Auxiliar (Implementação CustomBM25):** Classe utilitária registrada referencialmente baseada no arquivo `src/custom_retrievers.py`.
> ▫️ **Processador RRF Combinado:** Integrador nativo construcionado internamente dentro de instâncias associativas do motor de compilação `src/engine_builder.py`.

---

## 3. Glossário Topológico 

Definições sistêmicas e terminologias de uso recorrente para alinhar as rotinas de back-end ao domínio de regras organizacionais da solução.

| Terminologia Técnica | Escopo Operacional e Descrição |
|---|---|
| **Host ou Vault Directory** | Trata-se do diretório matriz de hospedagem isolada atrelada aos manifestos literários primários da aplicação (Arquivos Origem TXT/MD). A gestão nativa confina esses insumos preservando estabilidade em edições de arquivos sem substituição O.S acidental. |
| **Node / Chunk** | Definição sistêmica que agrupa o fragmento sequencial lógico individual, segmentado pelo motor estrutural referenciado nas integrações base da framework do "llama_index". |
| **Workstation Local (Nó Central Híbrido)** | Hardware primário do desenvolvedor local executando e persistindo instâncias de bases do PWA nativa, Roteador HTTP Integrador Relacional RAG SQLite Matrix O.S e File Watchers.  |
| **Servidor em Nuvem (Assistente ARM OCI Node)** | VPS gerenciada provendo isolamento parcial nas execuções nativas da Engine inferencial Ollama em serviços cloud Oracle baseados na topologia Ampere O.S. Auxilia restritamente no I/O O.S pesado atinente ao carregamento via Kernel Model Models Complexos limitativos ("qwen" etc), limitados e restritos ao tunelamento peer base (mTLS). |
| **System Prompt Config Settings** | Condiciona o comportamento de formatação O.S das respostas primárias que controlam a estrutura da predição através da variável O.S declarada nas APIs originadoras. (Gera formatações limitadas a contextos profissionais ou Json puro). |
| **Overlay VPN Peer-to-Peer Tunneling** | Infraestrutura abstrata e arquitetônica provedora de isolamento relacional encapsulada no sistema (Tailscale Overlay Model). Remove tráfego HTTP TCP passível base de porta conectada em mapeamento local web padrão O.S em Nuvem Public WAN Internet Addresses Routing. |
