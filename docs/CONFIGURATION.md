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

### USER_NAME

**Descrição**: Seu nome, usado no prompt do chat

**Padrão**: Nome do usuário do sistema

**Exemplo**:
```env
USER_NAME=João
```

Aparecerá como:
```
João > Qual é a temperatura hoje?
```

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
**Data**: 2026-02-17
**Versão**: 2.0.0