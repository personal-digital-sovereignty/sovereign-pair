# FAQ - Perguntas Frequentes

**Versão**: 2.0.0  
**Data**: 2026-02-16

---

## 📋 Índice

1. [Conceitos Básicos](#conceitos-básicos)
2. [Performance](#performance)
3. [Detecção de Mudanças](#detecção-de-mudanças)
4. [ChromaDB](#chromadb)
5. [Histórico](#histórico)
6. [Troubleshooting](#troubleshooting)
7. [Configuração](#configuração)

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
  "last_updated": "2026-02-16T20:00:00",
  "files": {
    "/path/to/file.md": {
      "content_hash": "abc123...",
      "modified_at": "2026-02-16T19:00:00",
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
**Data**: 2026-02-16  
**Versão**: 2.0.0
