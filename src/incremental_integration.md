# Código para Integração no ingest.py

## Passo 1: Adicionar função scan_all_files()

Adicione esta função ANTES da função `ingest_data()` (aproximadamente linha 210):

```python
def scan_all_files() -> set[Path]:
    """
    Escaneia todos os arquivos nos diretórios configurados.

    Retorna conjunto de Paths absolutos de todos os arquivos encontrados,
    sem carregá-los. Usado para detecção de mudanças na ingestão incremental.

    Returns:
        Conjunto de Paths absolutos
    """
    all_files = set()

    # Escanear vault
    if VAULT_DIR.exists():
        for ext in ALLOWED_EXTENSIONS:
            all_files.update(VAULT_DIR.rglob(f"*{ext}"))

    # Escanear raw_docs
    for raw_docs_dir in RAW_DOCS_DIRS:
        if raw_docs_dir.exists():
            for ext in ALLOWED_EXTENSIONS:
                all_files.update(raw_docs_dir.rglob(f"*{ext}"))

    # Resolver symlinks se configurado
    if FOLLOW_SYMLINKS:
        resolved_files = set()
        for file_path in all_files:
            try:
                resolved = file_path.resolve(strict=True)
                resolved_files.add(resolved)
            except (OSError, RuntimeError):
                logger.warning(f"  Ignorando arquivo com erro: {file_path}")
        return resolved_files

    return all_files
```

## Status

 Função criada e testada
 Aguardando integração manual no ingest.py

## Próximo Passo

Após adicionar a função, o MVP estará 100% funcional para testes básicos.
A modificação completa da main() pode ser feita na Fase 2.
