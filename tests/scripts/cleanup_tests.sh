#!/bin/bash
# Script de limpeza do ambiente de testes
# Remove dados de teste e resultados, mantendo scripts

set -e

echo "======================================================================="
echo "🧹 LIMPEZA DO AMBIENTE DE TESTES"
echo "======================================================================="

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Diretórios
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$TEST_DIR/data"
RESULTS_DIR="$TEST_DIR/results"

echo -e "\n${YELLOW}Atenção:${NC} Este script irá remover:"
echo "  - Todos os dados de teste em: $DATA_DIR"
echo "  - Todos os resultados em: $RESULTS_DIR"
echo ""
read -p "Deseja continuar? (s/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}Operação cancelada${NC}"
    exit 0
fi

echo -e "\n${YELLOW}[1/2]${NC} Removendo dados de teste..."

if [ -d "$DATA_DIR" ]; then
    rm -rf "$DATA_DIR"
    echo -e "${GREEN}✓${NC} Dados de teste removidos"
else
    echo -e "${YELLOW}⚠${NC}  Diretório de dados não encontrado"
fi

echo -e "\n${YELLOW}[2/2]${NC} Removendo resultados..."

if [ -d "$RESULTS_DIR" ]; then
    rm -rf "$RESULTS_DIR"
    echo -e "${GREEN}✓${NC} Resultados removidos"
else
    echo -e "${YELLOW}⚠${NC}  Diretório de resultados não encontrado"
fi

echo ""
echo "======================================================================="
echo "✅ LIMPEZA CONCLUÍDA"
echo "======================================================================="
echo ""
echo "Scripts de teste preservados em: $TEST_DIR/scripts"
echo ""
echo "Para executar novos testes:"
echo "  1. ./scripts/prepare_test_env.sh"
echo "  2. ./scripts/run_tests.sh"
echo ""
echo "======================================================================="
