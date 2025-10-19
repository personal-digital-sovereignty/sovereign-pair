#!/bin/bash
# Script principal de execução de testes
# Executa suite completa de testes de validação

set -e

echo "======================================================================="
echo "🧪 EXECUÇÃO DE TESTES - SOVEREIGN PAIR RAG"
echo "======================================================================="

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Diretórios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$TEST_DIR")"
RESULTS_DIR="$TEST_DIR/results"

# Timestamp para resultados
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULT_FILE="$RESULTS_DIR/test_results_$TIMESTAMP.log"

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Função para log
log_test() {
    echo -e "$1" | tee -a "$RESULT_FILE"
}

# Função para executar teste
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    log_test "\n${BLUE}[Teste $TESTS_TOTAL]${NC} $test_name"
    log_test "Comando: $test_command"
    
    if eval "$test_command" >> "$RESULT_FILE" 2>&1; then
        log_test "${GREEN}✅ PASSOU${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_test "${RED}❌ FALHOU${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Iniciar log
mkdir -p "$RESULTS_DIR"
echo "Início dos testes: $(date)" > "$RESULT_FILE"
echo "Diretório do projeto: $PROJECT_ROOT" >> "$RESULT_FILE"
echo "" >> "$RESULT_FILE"

log_test "======================================================================="
log_test "INICIANDO SUITE DE TESTES"
log_test "======================================================================="

# Verificar ambiente virtual
log_test "\n${YELLOW}[Pré-requisito]${NC} Verificando ambiente virtual..."
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    log_test "${RED}❌ Ambiente virtual não encontrado${NC}"
    log_test "Execute: python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi
log_test "${GREEN}✓${NC} Ambiente virtual encontrado"

# Ativar ambiente virtual
source "$PROJECT_ROOT/.venv/bin/activate"

# Verificar Python
log_test "\n${YELLOW}[Pré-requisito]${NC} Verificando versão do Python..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
log_test "Versão: $PYTHON_VERSION"

# Verificar dependências
log_test "\n${YELLOW}[Pré-requisito]${NC} Verificando dependências..."
run_test "Verificar llama-index instalado" "python -c 'import llama_index'"
run_test "Verificar chromadb instalado" "python -c 'import chromadb'"

# Teste 1: Validação de Configuração
log_test "\n======================================================================="
log_test "CATEGORIA: TESTES DE CONFIGURAÇÃO"
log_test "======================================================================="

run_test "Verificar arquivo config.py" "test -f $PROJECT_ROOT/src/config.py"
run_test "Verificar CHUNK_SIZE definido" "grep -q 'CHUNK_SIZE' $PROJECT_ROOT/src/config.py"
run_test "Verificar CHUNK_OVERLAP definido" "grep -q 'CHUNK_OVERLAP' $PROJECT_ROOT/src/config.py"

# Teste 2: Estrutura de Dados de Teste
log_test "\n======================================================================="
log_test "CATEGORIA: TESTES DE ESTRUTURA DE DADOS"
log_test "======================================================================="

run_test "Verificar diretório de dados de teste" "test -d $TEST_DIR/data"
run_test "Verificar documentos de teste criados" "test -f $TEST_DIR/data/vault/test_doc_01.md"
run_test "Verificar symlink de diretório" "test -L $TEST_DIR/data/vault/symlink_dir"
run_test "Verificar symlink de arquivo" "test -L $TEST_DIR/data/vault/symlink_file.txt"

# Teste 3: Validação de Symlinks
log_test "\n======================================================================="
log_test "CATEGORIA: TESTES DE SYMLINKS"
log_test "======================================================================="

run_test "Symlink de diretório resolve corretamente" "test -d $TEST_DIR/data/vault/symlink_dir"
run_test "Symlink de arquivo resolve corretamente" "test -f $TEST_DIR/data/vault/symlink_file.txt"
run_test "Symlink circular existe" "test -L $TEST_DIR/data/symlink_test/circular_test/subdir/circular_link"
run_test "Symlink quebrado existe" "test -L $TEST_DIR/data/vault/broken_symlink"

# Teste 4: Validação de Código
log_test "\n======================================================================="
log_test "CATEGORIA: TESTES DE CÓDIGO"
log_test "======================================================================="

run_test "Importar módulo config" "cd $PROJECT_ROOT/src && python -c 'import config'"
run_test "Verificar SentenceSplitter em ingest.py" "grep -q 'SentenceSplitter' $PROJECT_ROOT/src/ingest.py"
run_test "Verificar chunk_size em ingest.py" "grep -q 'chunk_size=CHUNK_SIZE' $PROJECT_ROOT/src/ingest.py"

# Teste 5: Simulação de Ingestão (Dry Run)
log_test "\n======================================================================="
log_test "CATEGORIA: TESTES DE INGESTÃO (DRY RUN)"
log_test "======================================================================="

# Criar .env temporário para testes
TEST_ENV="$TEST_DIR/.env.test"
cat > "$TEST_ENV" << EOF
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
EMBED_MODEL=nomic-embed-text
REQUEST_TIMEOUT=120.0
CHROMA_COLLECTION_NAME=test_collection
CHUNK_SIZE=1024
CHUNK_OVERLAP=200
FOLLOW_SYMLINKS=true
ALLOWED_EXTENSIONS=.md,.txt
EOF

log_test "Arquivo .env de teste criado: $TEST_ENV"

# Teste de validação de paths (sem executar ingestão completa)
run_test "Validar função de carregamento de documentos" "cd $PROJECT_ROOT/src && python -c '
import sys
from pathlib import Path
sys.path.insert(0, str(Path(\"$TEST_DIR/data\")))
from ingest import load_documents_from_directory
docs = load_documents_from_directory(Path(\"$TEST_DIR/data/vault\"), \"test\", follow_symlinks=True)
assert len(docs) > 0, \"Nenhum documento carregado\"
print(f\"Documentos carregados: {len(docs)}\")
'"

# Resumo Final
log_test "\n======================================================================="
log_test "RESUMO DOS TESTES"
log_test "======================================================================="
log_test ""
log_test "Total de testes: $TESTS_TOTAL"
log_test "${GREEN}Testes passados: $TESTS_PASSED${NC}"
log_test "${RED}Testes falhados: $TESTS_FAILED${NC}"
log_test ""

if [ $TESTS_FAILED -eq 0 ]; then
    log_test "${GREEN}✅ TODOS OS TESTES PASSARAM!${NC}"
    EXIT_CODE=0
else
    log_test "${RED}❌ ALGUNS TESTES FALHARAM${NC}"
    EXIT_CODE=1
fi

log_test ""
log_test "Resultados salvos em: $RESULT_FILE"
log_test ""
log_test "======================================================================="

exit $EXIT_CODE
