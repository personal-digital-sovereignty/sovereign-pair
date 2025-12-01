# Guia do Usuário - Ingestão Incremental

**Versão**: 2.0.0  
**Data**: 2026-02-16  
**Status**: MVP Completo

---

## 📋 Índice

1. [Introdução](#introdução)
2. [Instalação](#instalação)
3. [Configuração](#configuração)
4. [Uso Básico](#uso-básico)
5. [Uso Avançado](#uso-avançado)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Introdução

O sistema de **Ingestão Incremental** permite processar apenas arquivos novos ou modificados, economizando tempo e recursos.

### Conceitos Principais

- **Modo Full**: Processa todos os arquivos do zero
- **Modo Incremental**: Processa apenas mudanças (novos, modificados)
- **Hash SHA256**: Detecta modificações de conteúdo
- **ChromaDB**: Armazena embeddings vetoriais
- **Histórico**: Rastreia arquivos processados

### Benefícios

- ⚡ **95%+ mais rápido** que reprocessar tudo
- 💾 **Economia de recursos** (CPU, memória, disco)
- 🎯 **Detecção precisa** via hash de conteúdo
- 🧹 **Limpeza automática** de dados obsoletos

---

## Instalação

### Requisitos

- Python 3.8+
- pip ou poetry

### Dependências

```bash
pip install llama-index chromadb python-dotenv tqdm colorama
```

### Verificação

```bash
python src/ingest.py --help
```

---

## Configuração

### 1. Arquivo `.env`

Crie `.env` na raiz do projeto:

```bash
# Diretórios
VAULT_DIR=data/vault
RAW_DOCS_DIRS=docs,vault

# ChromaDB
CHROMA_DIR=data/chroma_db
CHROMA_COLLECTION_NAME=documents

# Chunking
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Modelo
EMBED_MODEL=BAAI/bge-small-en-v1.5
```

### 2. Criar Diretórios

```bash
mkdir -p data/vault data/chroma_db docs
```

### 3. Adicionar Documentos

```bash
# Copiar seus documentos
cp ~/meus-docs/*.md docs/
```

---

## Uso Básico

### Primeira Execução (Modo Full)

```bash
python src/ingest.py
```

**O que acontece**:
1. Detecta que não há histórico
2. Sugere modo "full"
3. Processa todos os arquivos
4. Cria histórico com hashes SHA256

**Saída esperada**:
```
╔══════════════════════════════════════════════════════════════════╗
║               INGESTÃO INCREMENTAL                               ║
╚══════════════════════════════════════════════════════════════════╝

🔍 Escaneando arquivos...
   Encontrados: 50 arquivos

📊 RESUMO DE MUDANÇAS
   ✨ Novos: 50
   ✏️  Modificados: 0
   🗑️  Deletados: 0

💡 Modo sugerido: full

Escolha o modo [full/incremental/skip/cancel]: full

🚀 MODO FULL: Processando todos os arquivos...
Calculando hashes: 100%|████████████| 50/50 [00:05<00:00, 9.8 arquivo/s]

✓ 50 arquivos processados
✓ 250 chunks criados
✓ Histórico atualizado

======================================================================
📊 ESTATÍSTICAS DE PROCESSAMENTO
======================================================================

⏱️  Tempo total: 1m 30s
📁 Arquivos processados: 50
📦 Chunks criados: 250
💾 Tamanho total: 5.2 MB
⚡ Velocidade: 0.56 arquivos/s
======================================================================
```

### Execuções Subsequentes (Modo Incremental)

```bash
# Modificar um arquivo
echo "\n## Nova seção" >> docs/exemplo.md

# Executar novamente
python src/ingest.py
```

**Saída esperada**:
```
🔍 Verificando 50 arquivo(s) comum(ns)...
Calculando hashes: 100%|████████████| 50/50 [00:01<00:00, 45.2 arquivo/s]

📊 RESUMO DE MUDANÇAS
   ✨ Novos: 0
   ✏️  Modificados: 1
   🗑️  Deletados: 0

💡 Modo sugerido: incremental

Escolha o modo [full/incremental/skip/cancel]: incremental

⚡ MODO INCREMENTAL: Processando mudanças...
   ✨ Novos: 0
   ✏️  Modificados: 1

🗑️  Removendo chunks obsoletos...
✅ Processando apenas arquivos modificados...

✓ 1 arquivo processado
✓ 5 chunks criados

🚀 Modo incremental:
   ✨ Novos: 0
   ✏️  Modificados: 1
   🗑️  Deletados: 0
   ⏭️  Ignorados: 49
```

---

## Uso Avançado

### Forçar Modo Full

```bash
python src/ingest.py
# Escolher "full" quando perguntado
```

**Quando usar**:
- Após mudanças no modelo de embedding
- Após mudanças no chunk_size
- Para reconstruir do zero

### Validar Estado

```bash
python tests/validate_state.py
```

**Saída**:
```
╔══════════════════════════════════════════════════════════════════╗
║               VALIDAÇÃO DO SISTEMA                               ║
╚══════════════════════════════════════════════════════════════════╝

📋 VALIDANDO HISTÓRICO
   Versão: 1.1
   Arquivos no histórico: 50
   ✅ Todos os 50 arquivos válidos

💾 VALIDANDO CHROMADB
   Total de chunks: 250
   Arquivos únicos: 50
   ✅ ChromaDB válido

🔍 VALIDANDO CONSISTÊNCIA
   Arquivos no histórico: 50
   Arquivos no ChromaDB: 50
   ✅ Histórico e ChromaDB consistentes

📊 RESUMO
   History        : ✅ PASS
   Chromadb       : ✅ PASS
   Consistency    : ✅ PASS

✅ TODAS AS VALIDAÇÕES PASSARAM
```

### Limpar e Recomeçar

```bash
# Backup (opcional)
cp -r data/chroma_db data/chroma_db.backup
cp data/.ingestion_history.json data/.ingestion_history.json.backup

# Limpar
rm -rf data/chroma_db
rm data/.ingestion_history.json

# Reprocessar
python src/ingest.py
```

---

## Troubleshooting

### Problema: "Collection not found"

**Causa**: ChromaDB não inicializado

**Solução**:
```bash
rm -rf data/chroma_db
python src/ingest.py  # modo full
```

### Problema: "Invalid history version"

**Causa**: Histórico de versão antiga

**Solução**: A migração é automática, mas se falhar:
```bash
rm data/.ingestion_history.json
python src/ingest.py  # modo full
```

### Problema: Performance lenta

**Causas e Soluções**:

1. **Muitos arquivos pequenos**
   - Solução: Já otimizado com paralelização

2. **Arquivos muito grandes**
   - Solução: Ajustar CHUNK_SIZE no .env

3. **Disco lento**
   - Solução: Usar SSD ou aumentar max_workers

### Problema: Inconsistência entre histórico e ChromaDB

**Diagnóstico**:
```bash
python tests/validate_state.py
```

**Solução**:
```bash
# Se divergências menores, reprocessar incrementalmente
python src/ingest.py  # modo incremental

# Se divergências grandes, reconstruir
rm -rf data/chroma_db data/.ingestion_history.json
python src/ingest.py  # modo full
```

---

## FAQ

### Como funciona a detecção incremental?

Usa hashes SHA256 do conteúdo dos arquivos. Se o hash mudou, o arquivo foi modificado.

### Por que usar SHA256 e não mtime?

mtime pode mudar sem o conteúdo mudar (ex: `touch`). SHA256 garante detecção baseada em conteúdo real.

### Quanto mais rápido é o modo incremental?

**95%+ mais rápido** quando há poucas mudanças. Exemplo:
- Modo full: 100 arquivos = 2 minutos
- Modo incremental: 2 modificados = 5 segundos

### O que acontece com arquivos deletados?

São detectados automaticamente e seus chunks são removidos do ChromaDB.

### Posso usar com outros modelos de embedding?

Sim! Altere `EMBED_MODEL` no `.env`. Mas precisará reprocessar tudo (modo full).

### Como debugar problemas?

1. Verificar logs no console
2. Executar `python tests/validate_state.py`
3. Verificar `.ingestion_history.json`
4. Verificar ChromaDB com `chromadb.PersistentClient`

### Posso processar múltiplos diretórios?

Sim! Configure `RAW_DOCS_DIRS` no `.env`:
```bash
RAW_DOCS_DIRS=docs,vault,notes,wiki
```

---

## Recursos Adicionais

- [API Documentation](API.md)
- [FAQ Completo](FAQ.md)
- [Testes End-to-End](../tests/manual_e2e_tests.md)
- [CHANGELOG](../CHANGELOG.md)

---

**Autor**: Jeferson Lopes  
**Data**: 2026-02-16  
**Versão**: 2.0.0
