#!/bin/bash

# ==============================================================================
# Sovereign Pair - Fast Rebuild Script
# ==============================================================================
# Use este script após pull de novas features, mudança de branch ou 
# atualizações intensivas de Frontend feitas via código/LLM.
# Evita reconstruir os Bancos de Dados e foca nos containers voláteis.

echo "==========================================================="
echo "🔄 SENSUS: Iniciando Reconstrução Quente (Hot-Rebuild)"
echo "==========================================================="

echo "⏳ 1/3: Parando serviço Web (Vue/Nginx)..."
docker-compose stop web
docker-compose rm -f web

echo "⏳ 2/3: Parando serviço API (FastAPI)..."
docker-compose stop api
docker-compose rm -f api

echo "⏳ 3/3: Recompilando imagens a partir do novo código-fonte..."
# A tag --build força o reler do package.json e requirements.txt
docker-compose up -d --build api web

echo "==========================================================="
echo "✅ SENSUS: Rebuild Completo! Os logs estarão disponíveis em instantes."
echo "💡 Dica: Rode 'docker-compose logs -f web api' para acompanhar."
echo "==========================================================="
exit 0
