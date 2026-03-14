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

echo "🔥 Destruindo containers Sensus antigos..."
docker compose -f infra/docker/docker-compose.yml stop web
docker compose -f infra/docker/docker-compose.yml rm -f web

echo "⏳ Refazendo Backend..."
docker compose -f infra/docker/docker-compose.yml stop api
docker compose -f infra/docker/docker-compose.yml rm -f api

echo "🚀 Subindo Sensus Vault Atualizado (Forçando Novo Build)..."
# O --build garante que as cópias na etapa "COPY web-ui/" recompilem seu SPA.
docker compose -f infra/docker/docker-compose.yml up -d --build api web

echo "✅ Integração O.S finalizada com sucesso."
echo "💡 Dica: Rode 'docker compose -f infra/docker/docker-compose.yml logs -f web api' para acompanhar."leto! Os logs estarão disponíveis em instantes."
echo "💡 Dica: Rode 'docker-compose logs -f web api' para acompanhar."
echo "==========================================================="
exit 0
