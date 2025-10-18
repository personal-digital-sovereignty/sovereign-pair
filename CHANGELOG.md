# Changelog - Sovereign Pair RAG

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [Unreleased]

### Fixed
- **Chunk Size para Embeddings** (2026-02-16)
  - Configurado `CHUNK_SIZE=1024` e `CHUNK_OVERLAP=200` para evitar erro "input length exceeds the context length"
  - Blocos de texto agora respeitam limite de contexto do modelo de embeddings
  - Adicionadas configurações em `config.py`, `.env.example` e documentação
  - Parsers (`MarkdownNodeParser` e `SimpleNodeParser`) configurados com limites seguros
  - Documentação de troubleshooting para erro de contexto excedido

- **Suporte a Symlinks de Diretórios** (2026-02-16)
  - Corrigido problema onde symlinks de diretórios não eram processados recursivamente
  - `load_documents_from_directory()` agora escaneia e resolve symlinks corretamente
  - Suporte a symlinks de arquivos e diretórios
  - Detecção de loops infinitos (symlinks circulares)
  - Logs melhorados mostrando quando symlinks são seguidos
  - Documentação completa em `docs/FILE_FORMATS.md` sobre uso de symlinks

### Added
- **Instruções para Arch Linux** (2026-02-16)
  - Adicionadas instruções de instalação Python 3.12 via AUR (yay/paru)
  - Opção alternativa usando pyenv
  - Troubleshooting específico para Arch Linux
  - Cobertura completa de sistemas: Ubuntu/Debian, Arch Linux, macOS

### Changed
- **Requisitos de Versão Python** (2026-02-16)
  - Especificado Python 3.11 ou 3.12 como versões recomendadas
  - Nota sobre incompatibilidade Python 3.14+ com ChromaDB/Pydantic V1
  - Troubleshooting para erro "Pydantic V1 isn't compatible with Python 3.14"
  - Instruções para criar ambiente virtual com Python 3.12

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [1.1.0] - 2026-02-16

### 🎉 Sistema de Configuração Interativa

Implementado sistema completo de configuração interativa com assistência do **Claude Sonnet 4.5**.

#### ✨ Adicionado

**Novos Arquivos:**
- `setup.py` (471 linhas) - Script de configuração interativa
  - Detecção automática de Ollama (localhost ou URL customizada)
  - Listagem de modelos disponíveis com seleção interativa
  - Mapeamento inteligente LLM → Embed Model recomendado
  - Cálculo automático de timeout baseado em categoria do modelo
  - Personalização completa de todas variáveis do agente
  - Geração automática de arquivo `.env`
  - Interface colorida com emojis e feedback visual
  - Backup automático de `.env` existente

- `docs/CONFIGURATION.md` (368 linhas) - Guia completo de configuração
  - Referência detalhada de todas as variáveis
  - Tabelas comparativas de modelos LLM e embed models
  - Recomendações de timeout por categoria de modelo
  - Exemplos de configuração para diferentes cenários
  - Seção de troubleshooting
  - Guias de uso para configuração rápida e manual

**Funcionalidades:**
- Seleção interativa de modelos Ollama disponíveis
- Mapeamento automático de 9+ modelos LLM para embed models
- Timeout dinâmico com 3 categorias (small: 60s, medium: 120s, large: 180s)
- Validação de conexão com Ollama antes de prosseguir
- Suporte a Ollama remoto (não apenas localhost)

#### 📝 Modificado

- `.env.example` (13 → 93 linhas)
  - Adicionados comentários explicativos detalhados para cada variável
  - Exemplos de valores para diferentes cenários
  - Recomendações específicas por categoria de modelo
  - Documentação inline de modelos populares
  - Explicação de trade-offs de configuração

- `README.md`
  - Nova seção "Configure o Projeto" com duas opções:
    - Opção A: Configuração Interativa (Recomendado) com `python setup.py`
    - Opção B: Configuração Manual tradicional
  - Link para documentação completa em `docs/CONFIGURATION.md`
  - Instruções detalhadas do processo de setup interativo

#### 🔧 Melhorias

**Experiência do Usuário:**
- Processo de configuração reduzido de manual para ~2 minutos guiados
- Recomendações automáticas eliminam necessidade de pesquisa
- Validações previnem erros de configuração
- Interface visual melhora compreensão do processo

**Documentação:**
- Guia completo de 368 linhas cobrindo todos os aspectos de configuração
- Exemplos práticos para 4 cenários diferentes (GPU potente, balanceado, leve, remoto)
- Tabelas comparativas facilitam escolha de modelos
- Troubleshooting cobre problemas comuns

**Flexibilidade:**
- Suporte a Ollama local e remoto
- Personalização completa mantida
- Configuração manual ainda disponível
- Backup automático protege configurações existentes

---

## [1.0.0] - 2026-02-16

### 🚀 Lançamento Inicial - Refatoração Completa

Refatoração completa do projeto com assistência do **Claude Sonnet 4.5**.

#### ✨ Adicionado

**Arquivos Principais:**
- `src/config.py` (191 linhas) - Configurações centralizadas
  - Paths absolutos usando `pathlib.Path`
  - Suporte a variáveis de ambiente com `python-dotenv`
  - Validação de conexão e modelos Ollama
  - Configuração global do LlamaIndex Settings
  - Funções auxiliares de validação

- `src/ingest.py` (165 linhas) - Sistema de ingestão robusto
  - Tratamento completo de erros
  - Logging estruturado com emojis
  - Validação de diretórios e arquivos
  - Progress bar para feedback visual
  - Função modular `load_documents_from_directory()`
  - Retorno do índice criado

- `src/agent.py` (284 linhas) - Agente modular
  - Arquitetura modular com funções separadas
  - Validações pré-execução (Ollama, modelos, ChromaDB)
  - Comandos especiais (`/help`, `/clear`, `sair`)
  - Tratamento robusto de erros
  - Busca web melhorada com formatação
  - Interface visual aprimorada

**Documentação:**
- `README.md` (296 linhas) - Documentação completa
  - Guia de instalação passo a passo
  - Instruções de uso detalhadas
  - Seção de troubleshooting
  - Exemplos práticos
  - Estrutura do projeto

- `requirements.txt` - Dependências organizadas
  - Core RAG Framework
  - Vector Store
  - Web Search
  - Utilities
  - Development Tools

- `.env.example` - Template de configuração
- `.gitignore` - Ignorar arquivos desnecessários

#### 🔧 Melhorias

**Arquitetura:**
- Caminhos relativos → Paths absolutos
- Código no nível de módulo → Funções `main()`
- Configurações duplicadas → Centralizadas em `config.py`
- Sem tratamento de erros → Try/except em operações críticas

**Qualidade de Código:**
- 0% → 100% type hints
- 0 → 11 docstrings
- 0 → 15+ blocos de tratamento de erros
- 84 → 640 linhas de código (+662%)

**Experiência do Usuário:**
- Prints simples → Logging estruturado
- Sem validações → Validações completas
- Sem feedback → Progress bars e emojis
- Mensagens genéricas → Mensagens claras e úteis

---

## Créditos

Desenvolvimento e refatoração realizados com assistência de **Claude Sonnet 4.5** (Anthropic).
