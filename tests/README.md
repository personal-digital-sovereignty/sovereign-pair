# Testes - Ingestão Incremental

Este diretório contém testes para validar o sistema de ingestão incremental.

---

## 📋 Arquivos de Teste

### 1. `manual_e2e_tests.md`
**Guia completo de testes end-to-end manuais**

Contém 5 cenários principais:
- Cenário 1: Novo arquivo
- Cenário 2: Arquivo modificado
- Cenário 3: Arquivo deletado
- Cenário 4: Múltiplas mudanças simultâneas
- Cenário 5: Modo full (retrocompatibilidade)

**Como usar**:
```bash
# Seguir o guia passo a passo
cat tests/manual_e2e_tests.md
```

### 2. `validate_state.py`
**Script de validação automática**

Valida:
- Histórico de ingestão (`.ingestion_history.json`)
- ChromaDB (chunks e metadados)
- Consistência entre histórico e ChromaDB

**Como usar**:
```bash
# Executar validação
python tests/validate_state.py

# Ou tornar executável
chmod +x tests/validate_state.py
./tests/validate_state.py
```

**Saída esperada**:
```
╔══════════════════════════════════════════════════════════════════╗
║               VALIDAÇÃO DO SISTEMA                               ║
╚══════════════════════════════════════════════════════════════════╝

======================================================================
📋 VALIDANDO HISTÓRICO
======================================================================
   Versão: 1.1
   Arquivos no histórico: 5
   ✅ Todos os 5 arquivos válidos

======================================================================
💾 VALIDANDO CHROMADB
======================================================================
   Total de chunks: 42
   Arquivos únicos: 5
   ✅ ChromaDB válido

======================================================================
🔍 VALIDANDO CONSISTÊNCIA
======================================================================
   Arquivos no histórico: 5
   Arquivos no ChromaDB: 5
   ✅ Histórico e ChromaDB consistentes

======================================================================
📊 RESUMO
======================================================================
   History        : ✅ PASS
   Chromadb       : ✅ PASS
   Consistency    : ✅ PASS

======================================================================
✅ TODAS AS VALIDAÇÕES PASSARAM
======================================================================
```

### 3. `test_incremental_modules.py`
**Testes unitários dos módulos**

Testa módulos individuais:
- `history.py`
- `diff.py`
- `interactive.py`
- `hash_utils.py`
- `cleanup.py`

**Como usar**:
```bash
python tests/test_incremental_modules.py
```

---

## 🚀 Execução Rápida

### Validação Completa
```bash
# 1. Validar estado atual
python tests/validate_state.py

# 2. Se tudo OK, sistema está consistente
# 3. Se houver erros, verificar logs e corrigir
```

### Testes End-to-End
```bash
# Seguir guia manual
cat tests/manual_e2e_tests.md

# Executar cada cenário
# Validar após cada cenário
python tests/validate_state.py
```

---

## 📊 Critérios de Aceitação

### Funcionalidade ✅
- [ ] Todos os 5 cenários passam
- [ ] ChromaDB consistente
- [ ] Histórico correto
- [ ] Sem erros ou warnings

### Performance ✅
- [ ] Modo incremental 95%+ mais rápido
- [ ] Processamento linear
- [ ] Uso de memória controlado

### Qualidade ✅
- [ ] Código sem erros
- [ ] Logs claros
- [ ] Tratamento de erros robusto

---

## 🔧 Troubleshooting

### Erro: "Collection not found"
```bash
rm -rf data/chroma_db
python src/ingest.py  # modo full
```

### Erro: "Invalid history version"
```bash
rm data/.ingestion_history.json
python src/ingest.py  # modo full
```

### Inconsistência entre histórico e ChromaDB
```bash
# Validar estado
python tests/validate_state.py

# Se necessário, recriar do zero
rm -rf data/chroma_db
rm data/.ingestion_history.json
python src/ingest.py  # modo full
```

---

## 📝 Relatório de Testes

Após executar todos os testes, documentar resultados em:
- `tests/results/test_report_YYYY-MM-DD.md`

---

**Autor**: Jeferson Lopes  
**Data**: 2026-02-16
