<!-- 
[Aviso Interno de Engenharia]
Este documento 'configuration_and_troubleshooting.pt-BR.md' é a fusão temporária ('bruta') da base de Fases Anteriores. 
Ele será submetido a um processo de refinamento linguístico focado em maturidade Sênior, erradicação de viés Emoji, reescrita corporativa limpa e posterior paralelização para o idioma en-US.
-->

# Guia de Configuração - Sovereign Pair RAG

Este guia explica como configurar o Sovereign Pair RAG para seu ambiente.

---

## Pré-requisitos

### Python 3.11 ou 3.12

O projeto requer **Python 3.11 ou 3.12** para compatibilidade com todas as dependências.

```bash
python --version  # Deve retornar 3.11.x ou 3.12.x
```

**Importante**:
-  Python 3.11 e 3.12 são totalmente compatíveis
-  Python 3.10 pode funcionar mas não é oficialmente testado
-  Python 3.14+ não é compatível (problemas com ChromaDB/Pydantic V1)

Se você tem Python 3.14+, crie um ambiente virtual com Python 3.12:

#### Ubuntu/Debian

```bash
# Instalar Python 3.12
sudo apt install python3.12 python3.12-venv

# Criar ambiente virtual
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Arch Linux

**Opção 1: Usando AUR (yay ou paru)**

```bash
# Com yay
yay -S python312

# Ou com paru
paru -S python312

# Criar ambiente virtual
cd ~/Developer/local-repositories/sovereign-pair
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Opção 2: Usando pyenv (mais flexível)**

```bash
# Instalar pyenv via AUR
yay -S pyenv

# Configurar pyenv no shell
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Recarregar configuração
source ~/.bashrc

# Instalar Python 3.12
pyenv install 3.12

# Usar localmente no projeto
cd ~/Developer/local-repositories/sovereign-pair
pyenv local 3.12

# Criar ambiente virtual
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### macOS

```bash
# Instalar Python 3.12
brew install python@3.12

# Criar ambiente virtual
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

##  Configuração Rápida (Recomendado)

A maneira mais fácil de configurar o projeto é usando o script interativo:

```bash
python setup.py
```

O script irá:
1.  Detectar automaticamente sua instalação do Ollama
2.  Listar todos os modelos disponíveis
3.  Recomendar embed model baseado no LLM escolhido
4.  Calcular timeout ideal para o modelo
5.  Permitir personalização de todas as configurações
6.  Gerar arquivo `.env` automaticamente

---

##  Configuração Manual

Se preferir configurar manualmente:

### 1. Criar Arquivo de Configuração

```bash
cp .env.example .env
```

### 2. Editar Variáveis

Abra o arquivo `.env` e ajuste as variáveis conforme necessário.

---

##  Referência de Variáveis

### OLLAMA_BASE_URL

**Descrição**: URL do servidor Ollama

**Valores Comuns**:
- `http://localhost:11434` - Ollama local (padrão)
- `http://192.168.1.100:11434` - Ollama em outra máquina na rede
- `http://host.docker.internal:11434` - Ollama do host quando rodando em Docker

**Acesso Remoto (Importante!)**:
Se você vai usar o Ollama rodando em outra máquina (como o IP `192.168.1.100`), garanta que no **servidor onde o Ollama roda**, ele tenha sido iniciado aceitando conexões externas definindo a variável `OLLAMA_HOST`:
```bash
# Na máquina servidora:
OLLAMA_HOST="0.0.0.0" ollama serve
```

**Como Verificar a Conexão**:
```bash
curl http://localhost:11434/api/tags
# Ou remotamente:
curl http://192.168.1.100:11434/api/tags
```

---

### LLM_MODEL

**Descrição**: Modelo de linguagem usado para chat e geração de respostas

**Modelos Recomendados**:

| Modelo | Tamanho | Velocidade | Qualidade | Uso Recomendado |
|--------|---------|------------|-----------|-----------------|
| `llama3.2` | ~4.7GB |  |  | **Recomendado** - Melhor balanço |
| `llama3.1` | ~4.7GB |  |  | Versão anterior, muito capaz |
| `mistral` | ~4.1GB |  |  | Excelente para tarefas gerais |
| `phi` | ~1.6GB |  |  | Rápido, bom para hardware limitado |
| `mixtral` | ~26GB |  |  | Muito poderoso, requer GPU |
| `gemma` | ~5.0GB |  |  | Modelo do Google, muito capaz |

**Como Listar Modelos Disponíveis**:
```bash
ollama list
```

**Como Baixar um Modelo**:
```bash
ollama pull llama3.2
```

---

### EMBED_MODEL

**Descrição**: Modelo usado para gerar embeddings (vetorização) dos documentos

**Modelos Disponíveis**:

| Modelo | Tamanho | Qualidade | Velocidade | Notas |
|--------|---------|-----------|------------|-------|
| `nomic-embed-text` | ~274MB |  |  | **Recomendado** - Melhor balanço |
| `mxbai-embed-large` | ~670MB |  |  | Maior qualidade, mais lento |
| `all-minilm` | ~45MB |  |  | Muito rápido, menor qualidade |

**IMPORTANTE**: O embed model deve estar instalado:
```bash
ollama pull nomic-embed-text
```

**Recomendação**: Use `nomic-embed-text` para todos os LLMs. Funciona muito bem e é eficiente.

---

### REQUEST_TIMEOUT

**Descrição**: Tempo máximo (em segundos) para aguardar resposta do Ollama

**Recomendações por Categoria**:

#### Modelos Pequenos (<7B parâmetros)
- **Timeout**: 60-90 segundos
- **Exemplos**: `phi`, `gemma:2b`, `llama3.2:1b`
- **Hardware**: CPU suficiente

#### Modelos Médios (7B-13B parâmetros)
- **Timeout**: 120-150 segundos
- **Exemplos**: `llama3.2`, `llama3.1`, `mistral`, `gemma:7b`
- **Hardware**: CPU ou GPU básica

#### Modelos Grandes (>13B parâmetros)
- **Timeout**: 180-240 segundos
- **Exemplos**: `mixtral`, `llama3:70b`, `qwen:72b`
- **Hardware**: GPU recomendada

**Ajustes por Hardware**:
- **GPU Potente** (RTX 3080+): Pode reduzir em 30-50%
- **CPU Apenas**: Pode precisar aumentar em 50-100%
- **Hardware Antigo**: Considere dobrar os valores

---

### CHROMA_COLLECTION_NAME

**Descrição**: Nome da coleção no ChromaDB onde os documentos são armazenados

**Padrão**: `sovereign_knowledge`

**Casos de Uso**:
- Use nomes descritivos para diferentes projetos
- Cada coleção é completamente independente
- Você pode ter múltiplas coleções

**Exemplos**:
```env
# Projeto pessoal
CHROMA_COLLECTION_NAME=my_notes

# Documentação de projeto
CHROMA_COLLECTION_NAME=project_x_docs

# Artigos de pesquisa
CHROMA_COLLECTION_NAME=research_papers
```

---

### USER_NAME / OWNER_NAME

**Descrição**: O nome formal do mestre e dono da máquina, usado para estruturação e saudação técnica.
**Padrão**: Nome do usuário do sistema
**Exemplo**:
```env
OWNER_NAME=Jeferson Lopes
```

---

### Perfil Biográfico e Injeção de Contexto (v3.0+)

Para garantir uma verdadeira experiência soberana (onde o RAG já sabe quem você é e a sua realidade sem você ter que repetir prompts constantes), adicione essas variáveis. Elas preenchem automaticamente o **System Prompt** do RAG e da inferência Web.

#### `OWNER_NICKNAME`
**Descrição**: Seu apelido ou como gostaria que o RAG lhe chamasse confortavelmente. Padrão ao `OWNER_NAME`.

#### `SOVEREIGN_NAME`
**Descrição**: Como você batizou a sua própria Inteligência Artificial.
**Exemplo**: `Jarvis`, `Neuromancer`, `Sovereign Pair`.

#### `LANGUAGE`
**Descrição**: Garante que mesmo modelos de língua inglesa (`mixtral`, `qwen`) priorizem respostas na sua gramática regional.
**Exemplo**: `Português do Brasil`.

#### `GEOLOCATION`
**Descrição**: Fornece ancoragem geográfica nativa. Quando você perguntar "Qual a previsão do tempo pra amanhã" ou "Locais para passear", a IA e o Web Search herdarão sua origem sem que você necessite soletrar a cidade.
**Exemplo**: `São Paulo, Brasil`.

#### `OCCUPATION`
**Descrição**: Direciona o jargão da resposta para o seu campo de proficiência. Respostas a consultas de programação serão formatadas visando `Senior Software Engineers`, por exemplo.

#### `ABOUT_USER`
**Descrição**: Traços fixos da sua biografia, preferências rígidas ("Sempre responda em tabelas", "Não use emojis artificiais", "Sou intolerante a lactose"). Isso funciona como um Custom Instruction persistente por baixo dos panos.

---

### AGENT_VERBOSE

**Descrição**: Controla se o agente mostra seu raciocínio

**Valores**:
- `true`: Mostra o raciocínio completo do agente (útil para debug)
- `false`: Mostra apenas a resposta final (interface mais limpa)

**Recomendação**:
- **Desenvolvimento**: `true` - Ajuda a entender como o agente pensa
- **Uso Diário**: `false` - Interface mais limpa e rápida

**Exemplo com `verbose=true`**:
```
Thought: O usuário quer saber sobre Python. Vou buscar nos arquivos locais.
Action: arquivos_pessoais
Action Input: Python
Observation: [resultados da busca]
Thought: Encontrei informações relevantes...
Answer: Python é uma linguagem...
```

**Exemplo com `verbose=false`**:
```
Python é uma linguagem...
```

---

### MAX_WEB_SEARCH_RESULTS

**Descrição**: Quantidade máxima de resultados retornados pela busca web

**Valores Recomendados**:
- `3`: Rápido, suficiente para maioria dos casos  **Recomendado**
- `5`: Mais contexto, um pouco mais lento
- `10`: Máximo contexto, mais lento

**Trade-offs**:
- **Mais resultados**: Mais contexto, mas processamento mais lento
- **Menos resultados**: Mais rápido, mas pod**Recomendação**: 3 para maioria dos casos

---

### CHUNK_SIZE

**Descrição**: Tamanho máximo de cada bloco de texto (em caracteres)

**Padrão**: `1024`

**Valores recomendados por modelo de embeddings**:

| Modelo | Chunk Size | Motivo |
|--------|-----------|--------|
| `nomic-embed-text` | 1024 | Padrão, compatível com ~2048 tokens |
| `mxbai-embed-large` | 512 | Modelo com limite menor |
| `all-minilm` | 256 | Modelo compacto |

**Exemplo**:
```env
# Para nomic-embed-text (padrão)
CHUNK_SIZE=1024

# Para modelos menores
CHUNK_SIZE=512
```

**Importante**: Chunks muito grandes causam erro `"input length exceeds the context length"` durante a geração de embeddings.

---

### CHUNK_OVERLAP

**Descrição**: Sobreposição entre chunks consecutivos (em caracteres)

**Padrão**: `200`

**Benefícios**:
- Preserva informações nas bordas dos chunks
- Melhora recuperação de informações
- Evita perda de contexto entre blocos

**Exemplo**:
```env
CHUNK_OVERLAP=200
```

**Recomendação**: Use ~20% do `CHUNK_SIZE` como overlap

---

##  Troubleshooting

### Erro: "Não foi possível conectar ao Ollama"

**Causa**: Ollama não está rodando ou URL incorreta

**Solução**:
```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se não estiver, iniciar Ollama
ollama serve
```

---

### Erro: "input length exceeds the context length"

**Sintoma**:
```
 Erro durante indexação: the input length exceeds the context length (status code: 400)
 Tamanho médio: 3598 caracteres
```

**Causa**: Blocos de texto muito grandes excedem limite do modelo de embeddings

**Solução**: Reduzir `CHUNK_SIZE` no `.env`

```env
# Antes (muito grande)
CHUNK_SIZE=2048

# Depois (seguro para nomic-embed-text)
CHUNK_SIZE=1024
```

**Valores seguros por modelo**:
- `nomic-embed-text`: 1024
- `mxbai-embed-large`: 512
- `all-minilm`: 256

**Após ajustar**: Execute novamente `python ingest.py`

---

### Erro: "Modelos faltando no Ollama"

**Causa**: Modelos especificados no `.env` não estão instalados

**Solução**:
```bash
# Baixar modelo LLM
ollama pull llama3.2

# Baixar modelo de embeddings
ollama pull nomic-embed-text
```

---

### Erro: "Pydantic V1 isn't compatible with Python 3.14"

**Sintoma**:
```
pydantic.v1.errors.ConfigError: unable to infer type for attribute "chroma_server_nofile"
```

**Causa**: Python 3.14+ não é compatível com ChromaDB/Pydantic V1

**Solução**: Usar Python 3.11 ou 3.12

#### Ubuntu/Debian

```bash
# 1. Verificar versão atual
python --version

# 2. Instalar Python 3.12
sudo apt install python3.12 python3.12-venv

# 3. Remover ambiente virtual antigo
cd /caminho/do/projeto
rm -rf .venv

# 4. Criar novo ambiente com Python 3.12
python3.12 -m venv .venv

# 5. Ativar ambiente
source .venv/bin/activate

# 6. Reinstalar dependências
pip install -r requirements.txt

# 7. Verificar instalação
python --version  # Deve mostrar 3.12.x
```

#### Arch Linux

**Opção 1: Usando AUR**

```bash
# 1. Verificar versão atual
python --version

# 2. Instalar Python 3.12 via AUR
yay -S python312
# ou
paru -S python312

# 3. Remover ambiente virtual antigo
cd ~/Developer/local-repositories/sovereign-pair
rm -rf .venv

# 4. Criar novo ambiente com Python 3.12
python3.12 -m venv .venv

# 5. Ativar ambiente
source .venv/bin/activate

# 6. Reinstalar dependências
pip install -r requirements.txt

# 7. Verificar instalação
python --version  # Deve mostrar 3.12.x
```

**Opção 2: Usando pyenv**

```bash
# 1. Instalar pyenv (se ainda não tiver)
yay -S pyenv

# 2. Configurar pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# 3. Instalar Python 3.12
pyenv install 3.12

# 4. Definir como versão local do projeto
cd ~/Developer/local-repositories/sovereign-pair
pyenv local 3.12

# 5. Remover ambiente virtual antigo
rm -rf .venv

# 6. Criar novo ambiente
python -m venv .venv
source .venv/bin/activate

# 7. Reinstalar dependências
pip install -r requirements.txt

# 8. Verificar instalação
python --version  # Deve mostrar 3.12.x
```

#### macOS

```bash
# 1. Verificar versão atual
python --version

# 2. Instalar Python 3.12
brew install python@3.12

# 3. Remover ambiente virtual antigo
cd /caminho/do/projeto
rm -rf .venv

# 4. Criar novo ambiente com Python 3.12
python3.12 -m venv .venv

# 5. Ativar ambiente
source .venv/bin/activate

# 6. Reinstalar dependências
pip install -r requirements.txt

# 7. Verificar instalação
python --version  # Deve mostrar 3.12.x
```

---

### Timeout Muito Curto

**Sintoma**: Erros de timeout frequentes

**Solução**: Aumentar `REQUEST_TIMEOUT` no `.env`
```env
# Era
REQUEST_TIMEOUT=120.0

# Aumentar para
REQUEST_TIMEOUT=180.0
```

---

### Respostas Muito Lentas

**Causas Possíveis**:
1. Modelo muito grande para o hardware
2. Timeout muito alto (aguarda muito tempo)
3. CPU apenas (sem GPU)

**Soluções**:
1. Usar modelo menor (ex: `phi` ao invés de `mixtral`)
2. Reduzir `REQUEST_TIMEOUT` se tiver GPU
3. Considerar usar GPU ou modelo menor

---

##  Exemplos de Configuração

### Configuração Rápida (GPU Potente)

```env
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=mixtral
EMBED_MODEL=nomic-embed-text
REQUEST_TIMEOUT=90.0
CHROMA_COLLECTION_NAME=sovereign_knowledge
USER_NAME=João
AGENT_VERBOSE=false
MAX_WEB_SEARCH_RESULTS=5
```

### Configuração Balanceada (CPU/GPU Básica)

```env
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
EMBED_MODEL=nomic-embed-text
REQUEST_TIMEOUT=120.0
CHROMA_COLLECTION_NAME=sovereign_knowledge
USER_NAME=Maria
AGENT_VERBOSE=true
MAX_WEB_SEARCH_RESULTS=3
```

### Configuração Leve (CPU Apenas)

```env
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=phi
EMBED_MODEL=nomic-embed-text
REQUEST_TIMEOUT=180.0
CHROMA_COLLECTION_NAME=sovereign_knowledge
USER_NAME=Pedro
AGENT_VERBOSE=false
MAX_WEB_SEARCH_RESULTS=3
```

### Configuração Remota

```env
OLLAMA_BASE_URL=http://192.168.1.100:11434
LLM_MODEL=llama3.2
EMBED_MODEL=nomic-embed-text
REQUEST_TIMEOUT=150.0
CHROMA_COLLECTION_NAME=team_docs
USER_NAME=Ana
AGENT_VERBOSE=true
MAX_WEB_SEARCH_RESULTS=3
```

---

##  Próximos Passos

Após configurar o `.env`:

1. **Adicionar Documentos**:
   ```bash
   # Copie seus documentos para:
   cp ~/meus-docs/*.pdf data/raw_docs/
   cp ~/minhas-notas/*.md data/vault/
   ```

2. **Executar Ingestão**:
   ```bash
   cd src
   python ingest.py
   ```

3. **Iniciar Agente**:
   ```bash
   cd src
   python agent.py
   ```

---

##  Recursos Adicionais

- [Documentação do Ollama](https://ollama.ai/docs)
- [Lista de Modelos Ollama](https://ollama.ai/library)
- [README Principal](../README.md)

---

**Autor**: Jeferson Lopes
**Data**: 2026-02-27


---

# FAQ - Perguntas Frequentes

**Versão**: 3.0.0
**Data**: 2026-02-27

---

##  Índice

1. [Conceitos Básicos](#conceitos-básicos)
2. [Performance](#performance)
3. [Detecção de Mudanças](#detecção-de-mudanças)
4. [ChromaDB](#chromadb)
5. [Histórico](#histórico)
6. [Privacidade e Segurança](#privacidade-e-segurança)
7. [Troubleshooting](#troubleshooting)
8. [Configuração](#configuração)

---

## Conceitos Básicos

### O que é ingestão incremental?

Ingestão incremental é processar apenas arquivos novos ou modificados, ao invés de reprocessar tudo do zero. Economiza tempo e recursos.

### Qual a diferença entre modo full e incremental?

- **Modo Full**: Processa todos os arquivos, recria ChromaDB do zero
- **Modo Incremental**: Processa apenas mudanças (novos, modificados), mantém dados existentes

### Quando devo usar cada modo?

**Modo Full**:
- Primeira execução
- Após mudar modelo de embedding
- Após mudar chunk_size
- Para reconstruir do zero

**Modo Incremental**:
- Execuções normais
- Após adicionar/modificar poucos arquivos
- Para economizar tempo

---

## Performance

### Quanto mais rápido é o modo incremental?

**95%+ mais rápido** quando há poucas mudanças.

**Exemplo real**:
- 100 arquivos, modo full: 2 minutos
- 2 arquivos modificados, modo incremental: 5 segundos
- **Economia: 96%**

### Como a paralelização funciona?

Usa `ThreadPoolExecutor` para calcular hashes de múltiplos arquivos simultaneamente.

**Configuração**:
- Default: 4 workers
- Ajustável em `compute_hashes_parallel(max_workers=N)`

**Ganho**: 3-4x mais rápido em sistemas multi-core

### O que é o cache LRU?

Cache em memória que armazena hashes calculados recentemente.

**Funcionamento**:
- Chave: file_path + mtime
- Se arquivo não mudou (mesmo mtime), usa hash do cache
- Maxsize: 1000 arquivos

**Benefício**: Evita recálculo desnecessário

### Como otimizar para muitos arquivos?

1. **Aumentar workers**:
   ```python
   compute_hashes_parallel(files, max_workers=8)
   ```

2. **Usar SSD**: Disco rápido ajuda muito

3. **Ajustar chunk_size**: Chunks maiores = menos chunks = mais rápido

---

## Detecção de Mudanças

### Como funciona a detecção de modificações?

Usa **hash SHA256 do conteúdo** do arquivo.

**Processo**:
1. Calcula hash atual do arquivo
2. Compara com hash armazenado no histórico
3. Se diferente, arquivo foi modificado

### Por que usar SHA256 e não mtime?

**mtime** (modification time) pode mudar sem o conteúdo mudar:
- Comando `touch arquivo.md`
- Copiar arquivo
- Sincronização de nuvem

**SHA256** garante detecção baseada em **conteúdo real**.

### O que acontece se eu renomear um arquivo?

É tratado como:
- **Deletado**: arquivo antigo
- **Novo**: arquivo com novo nome

Os chunks do arquivo antigo são removidos e novos são criados.

### E se eu mover um arquivo entre diretórios?

Mesmo comportamento de renomear:
- Deletado do diretório antigo
- Novo no diretório novo

**Nota**: Não há detecção de "move" - é sempre delete + add.

---

## ChromaDB

### O que é ChromaDB?

Banco de dados vetorial que armazena embeddings dos chunks de documentos.

**Usado para**:
- Busca semântica
- Recuperação de contexto
- RAG (Retrieval-Augmented Generation)

### Como os chunks são organizados?

Cada chunk tem:
- **ID**: Único (ex: `docs/exemplo.md_chunk_0`)
- **Embedding**: Vetor numérico
- **Metadata**: `{"file_path": "docs/exemplo.md"}`
- **Document**: Texto do chunk

### O que acontece com chunks de arquivos deletados?

São **removidos automaticamente** do ChromaDB.

**Processo**:
1. Detecta arquivo deletado
2. Busca todos os chunks com `file_path` do arquivo
3. Remove chunks do ChromaDB
4. Remove arquivo do histórico

### Posso usar outro banco vetorial?

Sim, mas requer modificação do código. ChromaDB é usado por ser:
- Fácil de usar
- Sem servidor externo
- Persistente em disco
- Integrado com LlamaIndex

---

## Histórico

### O que é o arquivo `.ingestion_history.json`?

Arquivo que rastreia:
- Quais arquivos foram processados
- Hash SHA256 de cada arquivo
- Número de chunks criados
- Timestamp de modificação

**Localização**: `data/.ingestion_history.json`

### Qual a estrutura do histórico?

```json
{
  "version": "1.1",
  "last_updated": "2026-02-27T20:00:00",
  "files": {
    "/path/to/file.md": {
      "content_hash": "abc123...",
      "modified_at": "2026-02-27T19:00:00",
      "chunks": 5
    }
  }
}
```

### O que acontece se eu deletar o histórico?

O sistema detecta ausência de histórico e sugere **modo full**.

**Consequência**: Todos os arquivos serão reprocessados.

### Como migrar de versão antiga?

A migração é **automática**:
- Detecta versão antiga (v1.0 sem `content_hash`)
- Adiciona campo `content_hash` para cada arquivo
- Atualiza versão para v1.1

**Nota**: Primeira execução após migração pode ser lenta (calcula todos os hashes).

---

## Privacidade e Segurança

### O que é enviado para a nuvem quando uso um provedor Cloud (Ex: Anthropic/OpenAI)?

**Seus documentos e o banco de dados ChromaDB NUNCA são enviados para a nuvem.**

A arquitetura RAG (Retrieval-Augmented Generation) do Sovereign Pair garante **Zero-Trust**:

1. **Ingestão Local:** Todos os seus PDFs e arquivos Markdown são indexados e convertidos em vetores matemáticos localmente no seu computador (seja via *bge-m3* no Ollama ou outro provider Embed). Tudo fica salvo na pasta `data/chromadb` do seu disco rígido (ou NVMe).
2. **Busca e Recuperação:** Quando você faz uma pergunta, o sistema procura os trechos de texto (`chunks`) e documentos inteiramente de forma local no seu banco de dados (BM25 + Choma Vector).
3. **Comunicação Ativa com a Nuvem:** O único dado que viaja para os servidores da Anthropic/Google/OpenAI **é a sua pergunta exata** + **os pequenos fragmentos de texto estritamente necessários** que o sistema encontrou nos seus arquivos locais para responder àquela dúvida específica. Todo o resto do seu Cofre (Vault) continua 100% offline e intocável.

É literalmente o equivalente a você pinçar o parágrafo 3 da página 10 de um livro secreto, transcrever isso num Post-it, e enviar esse Post-it por cima do balcão para o Analista ler, emitir a opinião dele sobre o parágrafo, e devolver sua resposta. Ele nunca verá sua biblioteca real de Alexandria inteira.

### Se o RAG local é tão bom, por que eu usaria um Provedor Cloud (Gemini, Claude, GPT-4) ao invés do Ollama 100% offline?

O Sovereign Pair nasceu para ser agnóstico. **Acreditamos que 80% do trabalho diário de busca, indexação e resumo de documentos (RAG) deve ser feito gratuitamente, offline e com privacidade infinita pelo Ollama (como o Llama 3 8B).**

Porém, para os 20% restantes que exigem "Raciocínio de Engenheiro Sênior", os modelos de fronteira (Frontier Models) das Big Techs possuem vantagens arquitetônicas que um computador doméstico simplesmente não consegue rodar. As 5 principais diferenças técnicas reais são:

1. **Orçamento Bilionário de Alinhamento (RLHF):** Após serem treinados, LLMs em nuvem passam meses sendo exaustivamente refinados por Ph.Ds e especialistas de domínio para entender sarcasmo legal, física quântica e arquitetura de software complexa, com orçamentos que ultrapassam dezenas de milhões de dólares *apenas no alinhamento fino*.
2. **"Self-Correction" Numérico Inerente:** Modelos recentes (como a série `o1` ou Gemini pesados) gastam processamento (*Test-Time Compute*) simulando mentalmente milhares de passos antes de lhe responder. Um modelo de 8B no Ollama geralmente lhe entrega a primeira resposta probabilística imediatamente.
3. **Pós-Treinamento em Agenciamento (Tool Use):** Cloud LLMs raramente quebram a sintaxe JSON, perdem o foco da missão ou falham ao recuperar erros complexos de Terminal/Código, pois foram afinados contra milhões de repositórios reais e validadores sistêmicos internos.
4. **Gigante "Mix of Experts" (MoE):** Por trás de uma API do Google ou Anthropic, você não fala com "uma" IA pesando 4GB. Você fala com um comitê de Gênios de dezenas de redes neurais especializadas que pesam trilhões de parâmetros.
5. **Atenção em Contextos Infinitos:** Conseguir achar "uma agulha num palheiro" com 99.9% de precisão dentro de 2 Milhões de Tokens é um desafio matemático massivo (*Ring Attention*), que os *Frontier Models* dominam amplamente hoje.

**Nossa Visão Estratégica:**
Com o Sovereign Pair, a sua CLI permite alternar entre os mundos: Use a força bruta local (Ollama) para tarefas estruturais diárias. No dia em que você precisar planejar uma fusão empresarial baseada num relatório de 40 páginas, você dá "2 cliques" na Web-UI, ativa o Cérebro de Fronteira (Cloud), e a injeção RAG passa a enviar cirurgicamente *apenas os parágrafos cruciais* para esse gigante raciocinar - preservando tanto seu orçamento quanto sua Soberania plena sobre o documento master, que jamais sairá da sua máquina.

---

## Troubleshooting

### "Collection not found" - O que fazer?

**Causa**: ChromaDB não inicializado

**Solução**:
```bash
rm -rf data/chroma_db
python src/ingest.py  # modo full
```

### "Invalid history version" - Como resolver?

**Causa**: Histórico de versão muito antiga ou corrompido

**Solução**:
```bash
rm data/.ingestion_history.json
python src/ingest.py  # modo full
```

### Performance está lenta - Como debugar?

1. **Verificar número de arquivos**:
   ```bash
   find docs vault -type f | wc -l
   ```

2. **Verificar tamanho dos arquivos**:
   ```bash
   du -sh docs vault
   ```

3. **Testar com poucos arquivos**:
   ```bash
   # Mover arquivos temporariamente
   mkdir temp_backup
   mv docs/* temp_backup/
   cp temp_backup/file1.md docs/
   python src/ingest.py
   ```

### Inconsistência entre histórico e ChromaDB - Como resolver?

**Diagnóstico**:
```bash
python tests/validate_state.py
```

**Soluções**:

1. **Divergências menores** (< 5%):
   ```bash
   python src/ingest.py  # modo incremental
   ```

2. **Divergências grandes** (> 10%):
   ```bash
   rm -rf data/chroma_db data/.ingestion_history.json
   python src/ingest.py  # modo full
   ```

### Erro "docx2txt is required" - Como resolver?

**Causa**: Falta a biblioteca necessária para processar arquivos `.docx` (Microsoft Word).

**Solução**:
```bash
pip install docx2txt
# ou
pip install -r requirements.txt
```

### Erro "Permission denied" - O que fazer?

**Causa**: Sem permissão para ler arquivo ou escrever no ChromaDB

**Soluções**:

1. **Verificar permissões**:
   ```bash
   ls -la data/
   ls -la docs/
   ```

2. **Corrigir permissões**:
   ```bash
   chmod -R u+rw data/
   chmod -R u+r docs/
   ```

---

## Configuração

### Quais variáveis de ambiente são necessárias?

**Obrigatórias**:
- `VAULT_DIR`: Diretório principal de documentos
- `RAW_DOCS_DIRS`: Diretórios adicionais (separados por vírgula)
- `CHROMA_DIR`: Diretório do ChromaDB
- `CHROMA_COLLECTION_NAME`: Nome da coleção

**Opcionais**:
- `CHUNK_SIZE`: Tamanho dos chunks (default: 512)
- `CHUNK_OVERLAP`: Sobreposição (default: 50)
- `EMBED_MODEL`: Modelo de embedding (default: BAAI/bge-small-en-v1.5)

### Como processar múltiplos diretórios?

Configure `RAW_DOCS_DIRS` no `.env`:

```bash
RAW_DOCS_DIRS=docs,vault,notes,wiki,knowledge
```

**Nota**: Separar por vírgula, sem espaços.

### Posso mudar o modelo de embedding?

Sim, mas **requer reprocessamento completo**.

**Processo**:
1. Alterar `EMBED_MODEL` no `.env`
2. Deletar ChromaDB e histórico
3. Executar modo full

```bash
# .env
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Terminal
rm -rf data/chroma_db data/.ingestion_history.json
python src/ingest.py  # modo full
```

### Como ajustar o tamanho dos chunks?

Edite `.env`:

```bash
CHUNK_SIZE=1024  # Chunks maiores
CHUNK_OVERLAP=100  # Mais sobreposição
```

**Trade-offs**:
- **Chunks maiores**: Menos chunks, mais rápido, menos granular
- **Chunks menores**: Mais chunks, mais lento, mais granular

**Nota**: Requer reprocessamento completo.

### Posso usar symlinks?

Sim! Configure `FOLLOW_SYMLINKS` no `.env`:

```bash
FOLLOW_SYMLINKS=true
```

**Cuidado**: Evite loops (symlink A → B → A).

---

## Casos de Uso

### Como usar com Obsidian?

1. **Configurar vault**:
   ```bash
   VAULT_DIR=/path/to/obsidian/vault
   ```

2. **Executar**:
   ```bash
   python src/ingest.py
   ```

3. **Workflow**:
   - Editar notas no Obsidian
   - Executar ingestão incremental
   - Apenas notas modificadas são reprocessadas

### Como usar com múltiplos projetos?

Crie `.env` separados:

```bash
# projeto1/.env
VAULT_DIR=data/projeto1
CHROMA_DIR=data/chroma_projeto1

# projeto2/.env
VAULT_DIR=data/projeto2
CHROMA_DIR=data/chroma_projeto2
```

Execute com:
```bash
cd projeto1 && python ../src/ingest.py
cd projeto2 && python ../src/ingest.py
```

### Como automatizar a ingestão?

**Cron (Linux/Mac)**:
```bash
# Executar a cada hora
0 * * * * cd /path/to/project && python src/ingest.py

# Executar diariamente às 2am
0 2 * * * cd /path/to/project && python src/ingest.py
```

**Task Scheduler (Windows)**:
1. Criar tarefa agendada
2. Ação: `python C:\path\to\project\src\ingest.py`
3. Gatilho: Diário/Horário

---

## Recursos Adicionais

- [Guia do Usuário](USER_GUIDE.md)
- [Documentação de API](API.md)
- [Testes End-to-End](../tests/manual_e2e_tests.md)
- [CHANGELOG](../CHANGELOG.md)

---

**Autor**: Jeferson Lopes
**Data**: 2026-02-27


---

