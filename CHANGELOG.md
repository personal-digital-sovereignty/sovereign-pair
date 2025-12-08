# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [2.1.0] - 2026-02-17

### Adicionado
- **Busca Híbrida (Hybrid Search)**: Implementação de recuperação combinada usando `Vector Store` (ChromaDB) e `BM25` (rank-bm25).
- **Recuperação de Datas e Termos Exatos**: O agente agora encontra documentos por datas específicas (ex: "18/10/2007") e palavras-chave que a busca semântica perdia.
- **Carregamento Robusto**: Fallback para carregar documentos diretamente do ChromaDB se o docstore local estiver vazio.
- **Streaming de Respostas**: Respostas são exibidas token a token (streaming), eliminando a percepção de travamento em modelos locais lentos.

### Corrigido
- **Bug de Inicialização**: Correção na carga de nós para o índice BM25 quando o sistema reinicia.
- **Timeout em Respostas Longas**: `REQUEST_TIMEOUT` aumentado de 120s para 300s no `.env` para modelos locais CPU-bound.

### Otimizado
- **Top-K Conservador**: Redução do Top-K de fusão (15→3) e dos retrievers individuais (20→5) para diminuir drasticamente o tempo de processamento do LLM local, eliminando timeouts.

---

## [2.0.0] - 2026-02-16

### 🎉 Major Release - MVP Completo com Otimizações

**Commit**: `81406a3`

### Added
- **Fase 3**: Refatoração 100% incremental
  - `ingest_data()` aceita documentos opcionais
  - Modo incremental não recarrega arquivos desnecessariamente
- **Fase 4**: Testes end-to-end completos
  - `tests/manual_e2e_tests.md` - Guia com 5 cenários
  - `tests/validate_state.py` - Validação automática
  - `tests/README.md` - Documentação de testes
- **Fase 5.1**: Otimizações de performance
  - `hash_utils.py` v2.0 com paralelização (ThreadPoolExecutor)
  - Cache LRU de hashes (functools.lru_cache)
  - `ux.py` - Logs coloridos (colorama)
  - Barras de progresso (tqdm)
  - Estatísticas detalhadas de processamento
- **Fase 5.2**: Documentação completa
  - `docs/USER_GUIDE.md` (366 linhas)
  - `docs/API.md` (503 linhas)
  - `docs/FAQ.md` (434 linhas)
  - `README.md` atualizado e completo

### Changed
- `ingest_data()` refatorado para aceitar `documents: Optional[list]`
- `diff.py` usa `compute_hashes_parallel()` para detecção mais rápida
- `hash_utils.py` completamente reescrito (v2.0)

### Performance
- ⚡ **95%+ mais rápido** em modo incremental vs full
- ⚡ **3-4x mais rápido** no cálculo de hashes (paralelização)
- 💾 Cache LRU reduz recálculo desnecessário
- 📊 Estatísticas detalhadas de performance

### Documentation
- 📚 **1303 linhas** de documentação nova
- 📖 Guia do usuário completo
- 🔧 API documentada
- ❓ FAQ abrangente

---

## [1.1.0] - 2026-02-16

### 🚀 Minor Release - Ingestão Incremental (Fases 1 e 2)

**Commits**: `5d9435c` até `f9dd82e`

### Added
- **Fase 1**: Detecção de novos arquivos
  - `history.py` - Gerenciamento de histórico de ingestão
  - `diff.py` - Detecção de mudanças
  - Integração com `ingest.py`
- **Fase 2**: Detecção completa + limpeza
  - `hash_utils.py` - Cálculo de hashes SHA256
  - Histórico v1.1 com campo `content_hash`
  - Detecção de arquivos modificados (via hash)
  - Detecção de arquivos deletados
  - `cleanup.py` - Limpeza automática de chunks obsoletos
  - `interactive.py` - Interface interativa (full/incremental/skip/cancel)

### Changed
- Histórico migrado de v1.0 para v1.1 (adição de `content_hash`)
- `ingest.py` integrado com sistema incremental

### Performance
- 🎯 Processa apenas arquivos novos ou modificados
- 🗑️ Limpeza automática de chunks obsoletos
- 📊 Detecção precisa via hash SHA256

---

## [1.0.0] - 2026-02-16

### 🎊 Major Release - Primeira Versão Estável

**Commit**: `9d64dbf`

### Added
- Sistema RAG básico funcional
- Ingestão de documentos (PDF, Markdown, DOCX, CSV, etc.)
- Busca vetorial com ChromaDB
- Agente ReAct com ferramentas
- Configuração via `.env`
- Tratamento robusto de erros
- Logging estruturado

### Changed
- `src/agent.py` - Melhorias significativas (+314 linhas)
- `src/config.py` - Configuração robusta (+191 linhas)
- `src/ingest.py` - Ingestão otimizada (+175 linhas)

### Fixed
- Diversos tratamentos de erros
- Validações de configuração
- Robustez geral do sistema

---

## Tipos de Mudanças

- `Added` - Novas funcionalidades
- `Changed` - Mudanças em funcionalidades existentes
- `Deprecated` - Funcionalidades que serão removidas
- `Removed` - Funcionalidades removidas
- `Fixed` - Correções de bugs
- `Security` - Correções de vulnerabilidades
- `Performance` - Melhorias de performance
- `Documentation` - Mudanças na documentação

---

## Links

| Version | URL |
|---------|-----|
| [2.0.0](https://github.com/Personal-Digital-Sovereignty/sovereign-pair/commit/2d97e65) | https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/tag/v2.0.0 |
| [1.1.0](https://github.com/Personal-Digital-Sovereignty/sovereign-pair/commit/8a3046d) | https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/tag/v1.1.0 |
| [1.0.0](https://github.com/Personal-Digital-Sovereignty/sovereign-pair/commit/9d64dbf) | https://github.com/Personal-Digital-Sovereignty/sovereign-pair/releases/tag/v1.0.0 |
