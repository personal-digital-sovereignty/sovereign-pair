#!/bin/bash
# Script de preparação de ambiente de testes
# Cria estrutura de diretórios e dados de teste para validação

set -e

echo "======================================================================="
echo "🧪 PREPARAÇÃO DO AMBIENTE DE TESTES"
echo "======================================================================="

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Diretório base de testes
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$TEST_DIR/data"
RESULTS_DIR="$TEST_DIR/results"

echo -e "\n${YELLOW}[1/6]${NC} Criando estrutura de diretórios..."

# Criar diretórios
mkdir -p "$DATA_DIR"/{vault,raw_docs,symlink_test}
mkdir -p "$RESULTS_DIR"

echo -e "${GREEN}✓${NC} Diretórios criados"

echo -e "\n${YELLOW}[2/6]${NC} Criando documentos de teste..."

# Criar documentos Markdown de teste
cat > "$DATA_DIR/vault/test_doc_01.md" << 'EOF'
# Documento de Teste 01

Este é um documento de teste para validar o sistema de ingestão.

## Seção 1

Conteúdo da seção 1 com texto suficiente para testar chunking.
Lorem ipsum dolor sit amet, consectetur adipiscing elit.

## Seção 2

Conteúdo da seção 2 com mais texto para validação.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

```python
# Bloco de código de teste
def test_function():
    return "Hello, World!"
```

## Seção 3

Texto final do documento de teste.
EOF

cat > "$DATA_DIR/vault/test_doc_02.md" << 'EOF'
# Documento de Teste 02

Segundo documento para testar processamento múltiplo.

## Introdução

Este documento testa a capacidade de processar múltiplos arquivos.

## Conteúdo

Texto com informações variadas para validar chunking e embeddings.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

## Conclusão

Documento de teste concluído.
EOF

cat > "$DATA_DIR/vault/test_doc_03_long.md" << 'EOF'
# Documento de Teste 03 - Longo

Este documento testa chunks maiores.

## Seção Extensa

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.

## Outra Seção

Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur.
EOF

cat > "$DATA_DIR/raw_docs/test_pdf_placeholder.txt" << 'EOF'
# Placeholder para PDF

Este arquivo simula um documento que seria PDF.
Em testes reais, substitua por arquivos .pdf reais.
EOF

echo -e "${GREEN}✓${NC} Documentos de teste criados (4 arquivos)"

echo -e "\n${YELLOW}[3/6]${NC} Criando estrutura para testes de symlinks..."

# Criar diretório para symlink
mkdir -p "$DATA_DIR/symlink_test/source_dir"

cat > "$DATA_DIR/symlink_test/source_dir/symlinked_doc.md" << 'EOF'
# Documento Symlinked

Este documento está em um diretório que será linkado via symlink.

## Teste de Symlink

Validando que symlinks de diretórios são processados corretamente.
EOF

echo -e "${GREEN}✓${NC} Estrutura de symlinks preparada"

echo -e "\n${YELLOW}[4/6]${NC} Criando symlinks de teste..."

# Criar symlink de diretório
cd "$DATA_DIR/vault"
ln -sf ../symlink_test/source_dir symlink_dir 2>/dev/null || true

# Criar symlink de arquivo
ln -sf ../raw_docs/test_pdf_placeholder.txt symlink_file.txt 2>/dev/null || true

cd "$TEST_DIR"

echo -e "${GREEN}✓${NC} Symlinks criados"

echo -e "\n${YELLOW}[5/6]${NC} Criando casos de teste especiais..."

# Criar symlink circular (para teste de detecção)
mkdir -p "$DATA_DIR/symlink_test/circular_test/subdir"
cd "$DATA_DIR/symlink_test/circular_test/subdir"
ln -sf ../.. circular_link 2>/dev/null || true
cd "$TEST_DIR"

# Criar symlink quebrado (para teste de erro)
cd "$DATA_DIR/vault"
ln -sf /path/that/does/not/exist broken_symlink 2>/dev/null || true
cd "$TEST_DIR"

echo -e "${GREEN}✓${NC} Casos especiais criados"

echo -e "\n${YELLOW}[6/6]${NC} Gerando resumo..."

# Contar arquivos
TOTAL_FILES=$(find "$DATA_DIR" -type f -name "*.md" -o -name "*.txt" | wc -l)
TOTAL_SYMLINKS=$(find "$DATA_DIR" -type l | wc -l)

echo ""
echo "======================================================================="
echo "✅ AMBIENTE DE TESTES PREPARADO"
echo "======================================================================="
echo ""
echo "📁 Estrutura criada:"
echo "   - Diretório base: $TEST_DIR"
echo "   - Dados de teste: $DATA_DIR"
echo "   - Resultados: $RESULTS_DIR"
echo ""
echo "📊 Estatísticas:"
echo "   - Arquivos de teste: $TOTAL_FILES"
echo "   - Symlinks criados: $TOTAL_SYMLINKS"
echo ""
echo "🔗 Symlinks de teste:"
echo "   - Symlink de diretório: vault/symlink_dir -> symlink_test/source_dir"
echo "   - Symlink de arquivo: vault/symlink_file.txt -> raw_docs/test_pdf_placeholder.txt"
echo "   - Symlink circular: symlink_test/circular_test/subdir/circular_link"
echo "   - Symlink quebrado: vault/broken_symlink"
echo ""
echo "📝 Próximos passos:"
echo "   1. Execute: ./scripts/run_tests.sh"
echo "   2. Verifique resultados em: $RESULTS_DIR"
echo ""
echo "======================================================================="
