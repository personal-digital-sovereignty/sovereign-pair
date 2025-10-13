# 🤖 Sovereign Pair - Agente RAG Local

Um sistema de **Retrieval-Augmented Generation (RAG)** completamente local e offline, que combina busca em documentos pessoais com acesso à internet quando necessário.

## 🌟 Características

- ✅ **100% Local**: Usa Ollama para rodar modelos de IA localmente
- 🔒 **Privacidade Total**: Seus documentos nunca saem da sua máquina
- 🧠 **RAG Inteligente**: Indexa e busca em PDFs, Markdown, DOCX, CSV e mais
- 🌐 **Busca Web**: Acesso a informações atualizadas via DuckDuckGo
- 🤖 **Agente ReAct**: Escolhe automaticamente entre busca local ou web
- 📦 **ChromaDB**: Vector store persistente para embeddings

---

## 📋 Pré-requisitos

### 1. Ollama Instalado

Instale o Ollama seguindo as instruções em: https://ollama.ai

```bash
# Verificar se está instalado
ollama --version
```

### 2. Modelos Necessários

Baixe os modelos que serão usados:

```bash
# Modelo de linguagem (LLM)
ollama pull llama3.2

# Modelo de embeddings
ollama pull nomic-embed-text
```

### 3. Python 3.11 ou 3.12 (Recomendado)

```bash
python --version  # Deve ser 3.11 ou 3.12
```

**Nota**: Python 3.14+ ainda não é totalmente compatível com as dependências (ChromaDB/Pydantic V1). Use Python 3.11 ou 3.12 para melhor compatibilidade.

---

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone <seu-repositorio>
cd sovereign-pair
```

### 2. Crie um Ambiente Virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\\Scripts\\activate  # Windows
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o Projeto

#### Opção A: Configuração Interativa (Recomendado) 🌟

Execute o script de configuração que irá guiá-lo através de todas as opções:

```bash
python setup.py
```

O script irá:
- ✅ Detectar automaticamente sua instalação do Ollama
- ✅ Listar todos os modelos disponíveis para seleção
- ✅ Recomendar embed model ideal para o LLM escolhido
- ✅ Calcular timeout automaticamente baseado no modelo
- ✅ Permitir personalização completa de todas as configurações
- ✅ Gerar arquivo `.env` automaticamente

#### Opção B: Configuração Manual

```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

📖 **Documentação Completa de Configuração**: Veja [docs/CONFIGURATION.md](docs/CONFIGURATION.md) para referência detalhada de todas as variáveis, valores recomendados e troubleshooting.

---

## 📚 Uso

### Passo 1: Adicionar Documentos

Coloque seus documentos nas pastas:

```
data/
├── raw_docs/     # PDFs, documentações, etc.
└── vault/        # Anotações em Markdown
```

Formatos suportados: `.md`, `.pdf`, `.docx`, `.csv`, `.txt`, e mais.

### Passo 2: Indexar Documentos

Execute o script de ingestão para criar os embeddings:

```bash
cd src
python ingest.py
```

Isso irá:
- ✅ Carregar todos os documentos de `raw_docs/` e `vault/`
- ✅ Gerar embeddings usando `nomic-embed-text`
- ✅ Armazenar no ChromaDB em `data/chromadb/`

### Passo 3: Iniciar o Agente

```bash
cd src
python agent.py
```

Agora você pode fazer perguntas! O agente escolherá automaticamente entre:
- 📂 **Busca Local**: Para informações nos seus documentos
- 🌐 **Busca Web**: Para informações atualizadas da internet

---

## 💬 Comandos do Agente

Dentro do chat com o agente:

| Comando | Descrição |
|---------|-----------|
| `sair` | Encerra o programa |
| `/help` | Mostra ajuda e comandos disponíveis |
| `/clear` | Limpa o histórico de conversação |

---

## ⚙️ Configuração

### Variáveis de Ambiente

Edite o arquivo `.env` para personalizar:

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
EMBED_MODEL=nomic-embed-text
REQUEST_TIMEOUT=120.0

# ChromaDB
CHROMA_COLLECTION_NAME=sovereign_knowledge

# Agente
USER_NAME=Jeferson
AGENT_VERBOSE=true
MAX_WEB_SEARCH_RESULTS=3
```

### Alterar Modelos

Para usar modelos diferentes:

1. Baixe o modelo: `ollama pull <nome-do-modelo>`
2. Atualize o `.env` com o nome do modelo
3. Reinicie o agente

---

## 🏗️ Estrutura do Projeto

```
sovereign-pair/
├── src/
│   ├── config.py       # Configurações centralizadas
│   ├── ingest.py       # Script de indexação de documentos
│   └── agent.py        # Agente de chat principal
├── data/
│   ├── raw_docs/       # Documentos para indexar
│   ├── vault/          # Anotações em Markdown
│   └── chromadb/       # Banco de dados vetorial (gerado)
├── .env.example        # Template de configuração
├── requirements.txt    # Dependências Python
└── README.md          # Este arquivo
```

---

## 🔧 Troubleshooting

### Erro: "Não foi possível conectar ao Ollama"

**Solução**: Certifique-se de que o Ollama está rodando:

```bash
ollama serve
```

### Erro: "Modelos faltando no Ollama"

**Solução**: Baixe os modelos necessários:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Erro: "Diretório ChromaDB não encontrado"

**Solução**: Execute primeiro o script de ingestão:

```bash
cd src
python ingest.py
```

### Erro: "Nenhum documento encontrado"

**Solução**: Adicione documentos nas pastas `data/raw_docs/` ou `data/vault/`

---

## 📝 Exemplos de Uso

### Busca Local

```
Jeferson > O que há nas minhas anotações sobre Python?
```

O agente irá buscar nos seus documentos indexados.

### Busca Web

```
Jeferson > Qual é a temperatura atual em São Paulo?
```

O agente irá buscar informações atualizadas na internet.

### Combinação

```
Jeferson > Compare minhas anotações sobre React com as melhores práticas atuais
```

O agente pode usar ambas as ferramentas para responder.

---

## 🛠️ Desenvolvimento

### Instalar Dependências de Desenvolvimento

```bash
pip install pytest black ruff
```

### Formatar Código

```bash
black src/
```

### Linting

```bash
ruff check src/
```

---

## 📄 Licença

Este projeto é de código aberto. Sinta-se livre para usar e modificar conforme necessário.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

---

## 🙏 Agradecimentos

- [Ollama](https://ollama.ai) - Modelos de IA locais
- [LlamaIndex](https://www.llamaindex.ai/) - Framework RAG
- [ChromaDB](https://www.trychroma.com/) - Vector store
- [DuckDuckGo](https://duckduckgo.com/) - Busca web

---

**Desenvolvido com ❤️ para pair programming local e privado**
