<!-- 
[Aviso Interno de Engenharia]
Este documento 'api_reference.pt-BR.md' é a fusão temporária ('bruta') da base de Fases Anteriores. 
Ele será submetido a um processo de refinamento linguístico focado em maturidade Sênior, erradicação de viés Emoji, reescrita corporativa limpa e posterior paralelização para o idioma en-US.
-->

# API Documentation - Ingestão Incremental

**Versão**: 3.0.0
**Data**: 2026-02-27

---

##  Índice

1. [Módulos](#módulos)
2. [Funções Principais](#funções-principais)
3. [Classes](#classes)
4. [Exemplos de Uso](#exemplos-de-uso)

---

## Módulos

### `hash_utils.py`
Utilitários para cálculo de hashes SHA256.

### `diff.py`
Detecção de mudanças entre execuções.

### `history.py`
Gerenciamento do histórico de ingestão.

### `cleanup.py`
Limpeza de chunks obsoletos no ChromaDB.

### `ux.py`
Melhorias de experiência do usuário.

---

## Funções Principais

### hash_utils

#### `compute_file_hash(file_path: Path) -> str`

Calcula hash SHA256 de um arquivo.

**Parâmetros**:
- `file_path` (Path): Caminho do arquivo

**Retorna**:
- `str`: Hash SHA256 (64 caracteres hexadecimais)

**Exceções**:
- `FileNotFoundError`: Se arquivo não existe
- `PermissionError`: Se sem permissão de leitura

**Exemplo**:
```python
from pathlib import Path
from hash_utils import compute_file_hash

file_path = Path("docs/exemplo.md")
hash_value = compute_file_hash(file_path)
print(hash_value)  # "a3b2c1d4e5f6..."
```

---

#### `compute_hashes_parallel(files: list[Path], max_workers: int = 4, use_cache: bool = True, show_progress: bool = True) -> dict[str, str]`

Calcula hashes SHA256 em paralelo para múltiplos arquivos.

**Parâmetros**:
- `files` (list[Path]): Lista de arquivos
- `max_workers` (int): Número de threads (default: 4)
- `use_cache` (bool): Se True, usa cache LRU (default: True)
- `show_progress` (bool): Se True, mostra barra de progresso (default: True)

**Retorna**:
- `dict[str, str]`: Dict {file_path: hash}

**Exemplo**:
```python
from pathlib import Path
from hash_utils import compute_hashes_parallel

files = [Path("file1.txt"), Path("file2.txt")]
hashes = compute_hashes_parallel(files, max_workers=4)
print(hashes)
# {'file1.txt': 'abc123...', 'file2.txt': 'def456...'}
```

**Performance**: 3-4x mais rápido que sequencial

---

#### `get_file_hash_with_cache(file_path: Path) -> str`

Obtém hash do arquivo usando cache quando possível.

**Parâmetros**:
- `file_path` (Path): Caminho do arquivo

**Retorna**:
- `str`: Hash SHA256

**Exemplo**:
```python
from pathlib import Path
from hash_utils import get_file_hash_with_cache

file_path = Path("docs/exemplo.md")
hash_value = get_file_hash_with_cache(file_path)
```

**Cache**: Baseado em mtime do arquivo

---

#### `get_cache_info() -> dict`

Retorna informações sobre o cache de hashes.

**Retorna**:
- `dict`: Com hits, misses, maxsize, currsize, hit_rate

**Exemplo**:
```python
from hash_utils import get_cache_info

info = get_cache_info()
print(info)
# {'hits': 100, 'misses': 50, 'maxsize': 1000, 'currsize': 50, 'hit_rate': 0.67}
```

---

#### `clear_hash_cache()`

Limpa o cache de hashes.

**Exemplo**:
```python
from hash_utils import clear_hash_cache

clear_hash_cache()
```

---

### diff

#### `detect_new_files(current_files: Set[Path], indexed_files: Set[Path]) -> Set[Path]`

Detecta arquivos novos que não estão no histórico.

**Parâmetros**:
- `current_files` (Set[Path]): Conjunto de arquivos encontrados atualmente
- `indexed_files` (Set[Path]): Conjunto de arquivos já indexados

**Retorna**:
- `Set[Path]`: Conjunto de arquivos novos

**Exemplo**:
```python
from pathlib import Path
from diff import detect_new_files

current = {Path("a.md"), Path("b.md"), Path("c.md")}
indexed = {Path("a.md"), Path("b.md")}

new_files = detect_new_files(current, indexed)
print(new_files)  # {Path("c.md")}
```

---

#### `detect_modified_files(current_files: Set[Path], indexed_files: Set[Path], history) -> Set[Path]`

Detecta arquivos que foram modificados desde a última ingestão.

**Parâmetros**:
- `current_files` (Set[Path]): Arquivos atuais no filesystem
- `indexed_files` (Set[Path]): Arquivos no histórico
- `history`: Instância do IngestionHistory

**Retorna**:
- `Set[Path]`: Conjunto de arquivos modificados

**Exemplo**:
```python
from pathlib import Path
from diff import detect_modified_files
from history import IngestionHistory

history = IngestionHistory()
current = {Path("a.md"), Path("b.md")}
indexed = {Path("a.md"), Path("b.md")}

modified = detect_modified_files(current, indexed, history)
print(modified)  # {Path("a.md")} se foi modificado
```

**Performance**: Usa hashing paralelo (3-4x mais rápido)

---

#### `detect_deleted_files(current_files: Set[Path], indexed_files: Set[Path]) -> Set[Path]`

Detecta arquivos que foram deletados desde a última ingestão.

**Parâmetros**:
- `current_files` (Set[Path]): Arquivos atuais
- `indexed_files` (Set[Path]): Arquivos no histórico

**Retorna**:
- `Set[Path]`: Conjunto de arquivos deletados

**Exemplo**:
```python
from pathlib import Path
from diff import detect_deleted_files

current = {Path("a.md")}
indexed = {Path("a.md"), Path("b.md")}

deleted = detect_deleted_files(current, indexed)
print(deleted)  # {Path("b.md")}
```

---

### cleanup

#### `remove_obsolete_chunks(file_paths: Set[Path], chroma_collection)`

Remove chunks obsoletos do ChromaDB.

**Parâmetros**:
- `file_paths` (Set[Path]): Conjunto de arquivos cujos chunks devem ser removidos
- `chroma_collection`: Coleção do ChromaDB

**Exemplo**:
```python
from pathlib import Path
import chromadb
from cleanup import remove_obsolete_chunks

client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_collection("documents")

files_to_remove = {Path("docs/old.md")}
remove_obsolete_chunks(files_to_remove, collection)
```

---

### ux

#### `ColoredLogger`

Logger com cores para melhor legibilidade.

**Métodos**:
- `success(msg: str)`: Log de sucesso (verde)
- `info(msg: str)`: Log informativo (azul)
- `warning(msg: str)`: Log de aviso (amarelo)
- `error(msg: str)`: Log de erro (vermelho)
- `header(msg: str)`: Cabeçalho destacado (ciano)

**Exemplo**:
```python
from ux import ColoredLogger

ColoredLogger.success("Processamento completo!")
ColoredLogger.info("Processando 50 arquivos...")
ColoredLogger.warning("Arquivo grande detectado")
ColoredLogger.error("Erro ao processar arquivo")
ColoredLogger.header("INGESTÃO INCREMENTAL")
```

---

#### `estimate_processing_time(num_files: int, avg_time_per_file: float = 0.5) -> str`

Estima tempo de processamento.

**Parâmetros**:
- `num_files` (int): Número de arquivos
- `avg_time_per_file` (float): Tempo médio por arquivo (segundos)

**Retorna**:
- `str`: String formatada (ex: "~2m 30s")

**Exemplo**:
```python
from ux import estimate_processing_time

time_est = estimate_processing_time(100)
print(time_est)  # "~50s"
```

---

#### `format_bytes(bytes_value: int) -> str`

Formata bytes em formato legível.

**Parâmetros**:
- `bytes_value` (int): Valor em bytes

**Retorna**:
- `str`: String formatada (ex: "1.5 MB")

**Exemplo**:
```python
from ux import format_bytes

size = format_bytes(1536000)
print(size)  # "1.5 MB"
```

---

#### `format_duration(seconds: float) -> str`

Formata duração em formato legível.

**Parâmetros**:
- `seconds` (float): Duração em segundos

**Retorna**:
- `str`: String formatada (ex: "2m 30s")

**Exemplo**:
```python
from ux import format_duration

duration = format_duration(125)
print(duration)  # "2m 5s"
```

---

## Classes

### `ProcessingStats`

Coleta e exibe estatísticas de processamento.

**Atributos**:
- `start_time` (float): Timestamp de início
- `files_processed` (int): Número de arquivos processados
- `chunks_created` (int): Número de chunks criados
- `total_bytes` (int): Total de bytes processados
- `new_files` (int): Arquivos novos
- `modified_files` (int): Arquivos modificados
- `deleted_files` (int): Arquivos deletados
- `unchanged_files` (int): Arquivos sem mudança
- `errors` (int): Número de erros
- `is_incremental` (bool): Se é modo incremental

**Métodos**:
- `mark_start()`: Marca início do processamento
- `get_duration() -> float`: Retorna duração em segundos
- `get_files_per_second() -> float`: Retorna taxa de processamento
- `show_summary()`: Mostra resumo estatístico detalhado
- `to_dict() -> dict`: Retorna estatísticas como dicionário

**Exemplo**:
```python
from ux import ProcessingStats

stats = ProcessingStats()
stats.mark_start()

# ... processar arquivos ...
stats.files_processed = 50
stats.chunks_created = 250
stats.total_bytes = 5242880

stats.show_summary()
```

---

### `IngestionHistory`

Gerencia histórico de ingestão.

**Métodos**:
- `load() -> bool`: Carrega histórico do disco
- `save()`: Salva histórico no disco
- `get_indexed_files() -> Set[Path]`: Retorna arquivos indexados
- `update_file(file_path: Path, content_hash: str, chunks: int)`: Atualiza arquivo no histórico
- `remove_file(file_path: Path)`: Remove arquivo do histórico

**Exemplo**:
```python
from pathlib import Path
from history import IngestionHistory

history = IngestionHistory()
history.load()

# Atualizar arquivo
history.update_file(
    Path("docs/exemplo.md"),
    content_hash="abc123...",
    chunks=5
)

history.save()
```

---

## Exemplos de Uso

### Exemplo 1: Calcular Hashes em Paralelo

```python
from pathlib import Path
from hash_utils import compute_hashes_parallel

# Listar arquivos
files = list(Path("docs").glob("*.md"))

# Calcular hashes em paralelo
hashes = compute_hashes_parallel(
    files,
    max_workers=4,
    use_cache=True,
    show_progress=True
)

print(f"Processados {len(hashes)} arquivos")
```

### Exemplo 2: Detectar Mudanças

```python
from pathlib import Path
from diff import detect_new_files, detect_modified_files, detect_deleted_files
from history import IngestionHistory

# Carregar histórico
history = IngestionHistory()
history.load()

# Arquivos atuais
current_files = set(Path("docs").glob("*.md"))
indexed_files = history.get_indexed_files()

# Detectar mudanças
new = detect_new_files(current_files, indexed_files)
modified = detect_modified_files(current_files, indexed_files, history)
deleted = detect_deleted_files(current_files, indexed_files)

print(f"Novos: {len(new)}, Modificados: {len(modified)}, Deletados: {len(deleted)}")
```

### Exemplo 3: Limpar Chunks Obsoletos

```python
from pathlib import Path
import chromadb
from cleanup import remove_obsolete_chunks

# Conectar ao ChromaDB
client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_collection("documents")

# Arquivos a remover
files_to_remove = {Path("docs/old1.md"), Path("docs/old2.md")}

# Remover chunks
remove_obsolete_chunks(files_to_remove, collection)
```

### Exemplo 4: Estatísticas de Processamento

```python
from ux import ProcessingStats

stats = ProcessingStats()
stats.mark_start()
stats.is_incremental = True

# Processar...
stats.files_processed = 10
stats.chunks_created = 50
stats.new_files = 2
stats.modified_files = 3
stats.deleted_files = 1
stats.unchanged_files = 4

# Mostrar resumo
stats.show_summary()
```

---

**Autor**: Jeferson Lopes
**Data**: 2026-02-27


---

