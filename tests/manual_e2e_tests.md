# Testes End-to-End Manuais - Ingestão Incremental

**Versão**: 1.0  
**Data**: 2026-02-16  
**Objetivo**: Validar MVP completo com testes práticos

---

## 📋 Preparação

### 1. Backup do Estado Atual
```bash
# Fazer backup do ChromaDB e histórico
cp -r data/chroma_db data/chroma_db.backup
cp data/.ingestion_history.json data/.ingestion_history.json.backup
```

### 2. Estado Inicial Limpo
```bash
# Limpar para começar do zero
rm -rf data/chroma_db
rm -f data/.ingestion_history.json

# Criar alguns arquivos de teste no vault
mkdir -p vault/test
echo "# Documento Base 1" > vault/test/base1.md
echo "# Documento Base 2" > vault/test/base2.md
echo "# Documento Base 3" > vault/test/base3.md
```

### 3. Ingestão Inicial (Baseline)
```bash
python src/ingest.py
# Escolher "full" quando perguntado
```

**Validar**:
- ✅ ChromaDB criado em `data/chroma_db/`
- ✅ Histórico criado em `data/.ingestion_history.json`
- ✅ 3 arquivos processados

---

## 🧪 Cenário 1: Novo Arquivo

### Objetivo
Validar detecção e processamento de arquivo novo

### Passos
```bash
# 1. Adicionar novo arquivo
echo "# Novo Documento\n\nEste é um documento novo para teste." > vault/test/novo.md

# 2. Executar ingestão
python src/ingest.py
```

### Validações Esperadas
- [ ] **Detecção**: Mostra "1 arquivo novo"
- [ ] **Resumo**: Lista `vault/test/novo.md`
- [ ] **Modo sugerido**: "incremental"
- [ ] **Processamento**: Processa apenas o novo arquivo
- [ ] **Histórico**: Contém `vault/test/novo.md` com hash SHA256
- [ ] **ChromaDB**: Contém chunks do novo arquivo

### Verificar Histórico
```bash
cat data/.ingestion_history.json | jq '.files["vault/test/novo.md"]'
```

**Esperado**:
```json
{
  "content_hash": "<64 caracteres SHA256>",
  "modified_at": <timestamp>,
  "chunks": <número>
}
```

---

## 🧪 Cenário 2: Arquivo Modificado

### Objetivo
Validar detecção por hash e reprocessamento

### Passos
```bash
# 1. Modificar arquivo existente
echo "\n## Nova Seção\n\nConteúdo adicionado." >> vault/test/base1.md

# 2. Executar ingestão
python src/ingest.py
```

### Validações Esperadas
- [ ] **Detecção**: Mostra "1 arquivo modificado"
- [ ] **Resumo**: Lista `vault/test/base1.md`
- [ ] **Hash**: Hash diferente do anterior
- [ ] **Limpeza**: Remove chunks antigos do ChromaDB
- [ ] **Processamento**: Processa apenas o modificado
- [ ] **Histórico**: Hash atualizado, timestamp atualizado

### Verificar Hash Mudou
```bash
# Antes (do backup)
cat data/.ingestion_history.json.backup | jq '.files["vault/test/base1.md"].content_hash'

# Depois
cat data/.ingestion_history.json | jq '.files["vault/test/base1.md"].content_hash'

# Devem ser diferentes!
```

---

## 🧪 Cenário 3: Arquivo Deletado

### Objetivo
Validar limpeza de chunks obsoletos

### Passos
```bash
# 1. Deletar arquivo
rm vault/test/base2.md

# 2. Executar ingestão
python src/ingest.py
```

### Validações Esperadas
- [ ] **Detecção**: Mostra "1 arquivo deletado"
- [ ] **Resumo**: Lista `vault/test/base2.md`
- [ ] **Limpeza**: Remove chunks do ChromaDB
- [ ] **Histórico**: Arquivo removido do histórico

### Verificar Remoção
```bash
# Não deve existir no histórico
cat data/.ingestion_history.json | jq '.files["vault/test/base2.md"]'
# Esperado: null
```

---

## 🧪 Cenário 4: Múltiplas Mudanças

### Objetivo
Validar processamento de múltiplas mudanças simultâneas

### Passos
```bash
# 1. Adicionar 2 novos
echo "# Novo A" > vault/test/novo_a.md
echo "# Novo B" > vault/test/novo_b.md

# 2. Modificar 1 existente
echo "\nModificação" >> vault/test/base3.md

# 3. Deletar 1
rm vault/test/novo.md

# 4. Executar ingestão
python src/ingest.py
```

### Validações Esperadas
- [ ] **Detecção**: 
  - 2 arquivos novos
  - 1 arquivo modificado
  - 1 arquivo deletado
- [ ] **Resumo**: Lista todos corretamente
- [ ] **Processamento**: Processa apenas os 3 (2 novos + 1 modificado)
- [ ] **Limpeza**: Remove chunks do deletado
- [ ] **Histórico**: Atualizado corretamente

### Verificar Contagem
```bash
# Contar arquivos no histórico
cat data/.ingestion_history.json | jq '.files | length'
# Esperado: 5 (base1, base3, novo_a, novo_b - base2 e novo foram removidos)
```

---

## 🧪 Cenário 5: Modo Full

### Objetivo
Validar retrocompatibilidade do modo full

### Passos
```bash
# 1. Executar ingestão
python src/ingest.py

# 2. Quando perguntado, escolher "full"
```

### Validações Esperadas
- [ ] **Detecção**: Mostra todos os arquivos atuais
- [ ] **Modo**: Força modo full
- [ ] **Limpeza**: Limpa histórico
- [ ] **Processamento**: Processa TODOS os arquivos
- [ ] **Histórico**: Recriado do zero com todos

### Verificar Recriação
```bash
# Todos os arquivos devem ter timestamps recentes
cat data/.ingestion_history.json | jq '.files | to_entries[] | {file: .key, modified: .value.modified_at}'
```

---

## 📊 Teste de Performance

### Objetivo
Validar que modo incremental é 95%+ mais rápido

### Setup
```bash
# Criar muitos arquivos
for i in {1..50}; do
  echo "# Documento $i\n\nConteúdo do documento $i" > vault/test/doc_$i.md
done

# Ingestão inicial
python src/ingest.py  # modo full
```

### Teste 1: Modo Full
```bash
time python src/ingest.py
# Escolher "full"
# Anotar tempo: _____ segundos
```

### Teste 2: Modo Incremental (1 modificação)
```bash
# Modificar apenas 1 arquivo
echo "\nModificação" >> vault/test/doc_1.md

time python src/ingest.py
# Escolher "incremental"
# Anotar tempo: _____ segundos
```

### Cálculo
```
Economia = (tempo_full - tempo_incremental) / tempo_full * 100
Esperado: > 95%
```

---

## ✅ Checklist de Validação Final

### Funcionalidade
- [ ] Cenário 1: Novo arquivo ✓
- [ ] Cenário 2: Modificado ✓
- [ ] Cenário 3: Deletado ✓
- [ ] Cenário 4: Múltiplas mudanças ✓
- [ ] Cenário 5: Modo full ✓

### ChromaDB
- [ ] Chunks criados para novos
- [ ] Chunks atualizados para modificados
- [ ] Chunks removidos para deletados
- [ ] Embeddings gerados corretamente

### Histórico
- [ ] Versão v1.1
- [ ] Hashes SHA256 corretos
- [ ] Timestamps atualizados
- [ ] Contagem de chunks correta

### Performance
- [ ] Modo incremental 95%+ mais rápido
- [ ] Uso de memória controlado
- [ ] Sem erros ou warnings

---

## 🔧 Troubleshooting

### Erro: "Collection not found"
```bash
# Recriar ChromaDB
rm -rf data/chroma_db
python src/ingest.py  # modo full
```

### Erro: "Invalid history version"
```bash
# Migração automática deve funcionar
# Se não, deletar e recriar
rm data/.ingestion_history.json
python src/ingest.py  # modo full
```

### Performance não melhora
```bash
# Verificar que está usando modo incremental
# Verificar logs: deve mostrar "Processando X arquivo(s)"
# Não deve mostrar "Carregando todos os documentos"
```

---

## 📝 Relatório de Testes

Após executar todos os cenários, preencher:

**Data**: ___________  
**Executor**: ___________

| Cenário | Status | Observações |
|---------|--------|-------------|
| 1. Novo arquivo | ⬜ Pass / ⬜ Fail | |
| 2. Modificado | ⬜ Pass / ⬜ Fail | |
| 3. Deletado | ⬜ Pass / ⬜ Fail | |
| 4. Múltiplas mudanças | ⬜ Pass / ⬜ Fail | |
| 5. Modo full | ⬜ Pass / ⬜ Fail | |

**Performance**:
- Tempo modo full: _____ s
- Tempo incremental: _____ s
- Economia: _____ %

**Conclusão**: ⬜ APROVADO / ⬜ REPROVADO

---

**Autor**: Jeferson Lopes  
**Assistência**: Claude Sonnet 4.5 (Anthropic)
