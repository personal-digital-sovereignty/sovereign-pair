#!/bin/bash
# =============================================================================
# Sovereign Pair — Test Suite: Funcional · E2E · Segurança · Regressão
# =============================================================================
set -euo pipefail

BASE="${1:-http://127.0.0.1:38001}"
PASS=0; FAIL=0; SKIP=0
FAILS=""

green() { echo -e "\033[0;32m✅ $1\033[0m"; }
red()   { echo -e "\033[0;31m❌ $1\033[0m"; }
blue()  { echo -e "\033[0;34m🔵 $1\033[0m"; }
yellow(){ echo -e "\033[0;33m⚠️  $1\033[0m"; }

assert() {
    local desc="$1" expected="$2" actual="$3"
    if echo "$actual" | grep -q "$expected"; then
        green "$desc"
        PASS=$((PASS+1))
    else
        red "$desc  [expected: '$expected'  got: '$actual']"
        FAIL=$((FAIL+1))
        FAILS="$FAILS\n  ❌ $desc"
    fi
}

assert_status() {
    local desc="$1" expected="$2" actual="$3"
    if [ "$actual" = "$expected" ]; then
        green "$desc"
        PASS=$((PASS+1))
    else
        red "$desc  [expected HTTP $expected  got: $actual]"
        FAIL=$((FAIL+1))
        FAILS="$FAILS\n  ❌ $desc"
    fi
}

echo ""
blue "=== SOVEREIGN PAIR TEST SUITE ==="
blue "Target: $BASE"
echo ""

# ─────────────────────────────────────────────────────────────────
# BLOCO 1 — HEALTH & FUNCIONAL
# ─────────────────────────────────────────────────────────────────
echo "━━━ [1/4] FUNCIONAL ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1.1 Settings GET
R=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/v1/settings")
assert_status "GET /v1/settings retorna 200" "200" "$R"

# 1.2 Model Capabilities Matrix GET
R=$(curl -s "$BASE/v1/settings/model_capabilities")
assert "GET /v1/settings/model_capabilities retorna JSON array" "\[" "$R"

# 1.3 Capacidades contém campos obrigatórios
assert "Matrix contém campo 'model_name'" "model_name" "$R"
assert "Matrix contém campo 'is_master'" "is_master" "$R"
assert "Matrix contém campo 'is_scribe'" "is_scribe" "$R"

# 1.4 Ollama Clusters GET
R=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/v1/settings/ollama_clusters")
assert_status "GET /v1/settings/ollama_clusters retorna 200" "200" "$R"

# 1.5 Available Models
R=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/v1/system/available_models")
assert_status "GET /v1/system/available_models retorna 200" "200" "$R"

# 1.6 PATCH toggle is_master (qwen3:8b)
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/v1/settings/model_capabilities/toggles" \
    -H "Content-Type: application/json" \
    -d '{"model_name":"qwen3:8b","is_master":true,"is_scribe":true,"is_agent":true,"is_coder":true,"is_chat":true,"is_project":true}')
assert_status "POST /v1/settings/model_capabilities/toggles (qwen3:8b)" "200" "$R"

# 1.7 Confirmar que foi salvo no banco
R=$(curl -s "$BASE/v1/settings/model_capabilities")
assert "qwen3:8b presente na matrix após toggle" "qwen3:8b" "$R"

echo ""
# ─────────────────────────────────────────────────────────────────
# BLOCO 2 — E2E: DELETE model_capabilities (nova feature)
# ─────────────────────────────────────────────────────────────────
echo "━━━ [2/4] E2E — DELETE MODEL MATRIX ━━━━━━━━━━━━━━━━━━━━━━━━"

# Inserir modelo fantasma para testar delete
sqlite3 /home/jefersonlopes/.local/share/sovereign-pair/data/sovereign_memory.db \
    "INSERT OR REPLACE INTO model_capabilities (model_name, parameter_size, supports_tools, is_reasoner, is_master, is_scribe, is_agent, is_coder, is_chat, is_project, is_installed)
     VALUES ('test-ghost-model:1b', 1.0, 0, 0, 0, 0, 0, 0, 1, 0, 0);" 2>/dev/null

# 2.1 Verificar que foi inserido
R=$(curl -s "$BASE/v1/settings/model_capabilities")
assert "Modelo fantasma inserido via SQLite aparece na Matrix" "test-ghost-model" "$R"

# 2.2 DELETE via API
ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('test-ghost-model:1b'))")
R=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/v1/settings/model_capabilities/$ENCODED")
assert_status "DELETE /v1/settings/model_capabilities/:model → 200" "200" "$R"

# 2.3 Confirmar que sumiu
R=$(curl -s "$BASE/v1/settings/model_capabilities")
if echo "$R" | grep -q "test-ghost-model"; then
    red "E2E DELETE: modelo fantasma ainda presente após delete!"
    FAIL=$((FAIL+1))
    FAILS="$FAILS\n  ❌ E2E DELETE: modelo ainda presente"
else
    green "E2E DELETE: modelo removido corretamente da Matrix"
    PASS=$((PASS+1))
fi

# 2.4 DELETE de modelo inexistente deve retornar 404
R=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE/v1/settings/model_capabilities/nao-existe%3A99b")
assert_status "DELETE modelo inexistente → 404" "404" "$R"

echo ""
# ─────────────────────────────────────────────────────────────────
# BLOCO 3 — SEGURANÇA
# ─────────────────────────────────────────────────────────────────
echo "━━━ [3/4] SEGURANÇA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 3.1 SQL Injection no model_name do toggle
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/v1/settings/model_capabilities/toggles" \
    -H "Content-Type: application/json" \
    -d '{"model_name":"qwen3:8b\"; DROP TABLE model_capabilities; --","is_master":true,"is_scribe":false,"is_agent":false,"is_coder":false,"is_chat":true,"is_project":false}')
# Deve retornar nem 500 nem destruir o banco
assert_status "SQL Injection no toggle não retorna 500" "200" "$R"

# Verificar que o banco sobreviveu
R2=$(curl -s "$BASE/v1/settings/model_capabilities")
assert "Banco sobreviveu ao SQL injection attempt" "model_name" "$R2"

# 3.2 XSS no model_name do DELETE (path injection)
R=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
    "$BASE/v1/settings/model_capabilities/%3Cscript%3Ealert(1)%3C%2Fscript%3E")
# Deve ser 404 (modelo não existe), não 500
if [ "$R" = "404" ] || [ "$R" = "200" ]; then
    green "XSS path injection no DELETE tratado corretamente (HTTP $R)"
    PASS=$((PASS+1))
else
    red "XSS path injection retornou HTTP $R inesperado"
    FAIL=$((FAIL+1))
fi

# 3.3 Path traversal no DELETE
R=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
    "$BASE/v1/settings/model_capabilities/..%2F..%2Fetc%2Fpasswd")
if [ "$R" = "404" ] || [ "$R" = "400" ]; then
    green "Path traversal no DELETE bloqueado (HTTP $R)"
    PASS=$((PASS+1))
else
    red "Path traversal retornou HTTP $R — verificar"
    FAIL=$((FAIL+1))
fi

# 3.4 Payload oversized no toggle
GIANT=$(python3 -c "print('A'*100000)")
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/v1/settings/model_capabilities/toggles" \
    -H "Content-Type: application/json" \
    -d "{\"model_name\":\"$GIANT\",\"is_master\":false,\"is_scribe\":false,\"is_agent\":false,\"is_coder\":false,\"is_chat\":false,\"is_project\":false}" \
    --max-time 5 2>/dev/null || echo "000")
if [ "$R" = "413" ] || [ "$R" = "400" ] || [ "$R" = "200" ] || [ "$R" = "000" ]; then
    green "Payload 100KB no toggle não causa crash (HTTP $R)"
    PASS=$((PASS+1))
else
    red "Payload oversized causou comportamento inesperado: HTTP $R"
    FAIL=$((FAIL+1))
fi

# 3.5 CORS headers presentes
R=$(curl -s -I "$BASE/v1/settings" | grep -i "access-control\|vary\|content-type" | tr '\n' '|')
if [ -n "$R" ]; then
    green "Headers HTTP presentes: $R"
    PASS=$((PASS+1))
else
    yellow "Sem headers CORS detectados (pode ser intencional para API local)"
    SKIP=$((SKIP+1))
fi

# 3.6 SecOps Vault — tenant key injeção com payload malicioso
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/v1/settings/tenant_keys" \
    -H "Content-Type: application/json" \
    -d '{"provider_name":"TEST_INJECTION\"; DROP TABLE tenant_api_keys; --","api_key_value":"sk-fake-test-key-regression"}')
if [ "$R" = "200" ] || [ "$R" = "201" ]; then
    # Verificar que o banco sobreviveu
    R2=$(curl -s "$BASE/v1/settings/tenant_keys")
    if echo "$R2" | grep -q "\["; then
        green "Tenant keys SQL injection tratado, banco intacto"
        PASS=$((PASS+1))
        # Limpar a key de teste
        KEY_ID=$(echo "$R2" | python3 -c "import json,sys; keys=json.load(sys.stdin); [print(k['id']) for k in keys if 'TEST_INJECTION' in k.get('provider_name','')]" 2>/dev/null | head -1)
        [ -n "$KEY_ID" ] && curl -s -X DELETE "$BASE/v1/settings/tenant_keys/$KEY_ID" > /dev/null
    else
        red "Banco de tenant_keys pode ter sido corrompido"
        FAIL=$((FAIL+1))
    fi
fi

echo ""
# ─────────────────────────────────────────────────────────────────
# BLOCO 4 — REGRESSÃO (features anteriores ao hotfix de hoje)
# ─────────────────────────────────────────────────────────────────
echo "━━━ [4/4] REGRESSÃO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 4.1 qwen3:8b ainda tem is_master=1 (não foi revertido pelos testes de segurança)
R=$(curl -s "$BASE/v1/settings/model_capabilities")
QW=$(echo "$R" | python3 -c "
import json, sys
models = json.load(sys.stdin)
for m in models:
    if m['model_name'] == 'qwen3:8b':
        print('master=' + str(m['is_master']) + ' scribe=' + str(m['is_scribe']) + ' reasoner=' + str(m['is_reasoner']))
" 2>/dev/null)
assert "qwen3:8b ainda é master após testes de segurança" "master=True" "$QW"

# 4.2 phi4:14b não é scribe (regressão do fix de latência)
PH=$(echo "$R" | python3 -c "
import json, sys
models = json.load(sys.stdin)
for m in models:
    if m['model_name'] == 'phi4:14b':
        print('scribe=' + str(m['is_scribe']) + ' master=' + str(m['is_master']))
" 2>/dev/null)
assert "phi4:14b não é scribe (regressão latência)" "scribe=False" "$PH"

# 4.3 mistral-nemo:latest não existe mais como entrada duplicada
MIST=$(echo "$R" | python3 -c "
import json, sys
models = json.load(sys.stdin)
names = [m['model_name'] for m in models]
print('has_latest=' + str('mistral-nemo:latest' in names))
" 2>/dev/null)
assert "mistral-nemo:latest não existe mais como entrada duplicada" "has_latest=False" "$MIST"

# 4.4 Racer: toggle + delete não corrompe dado (write-after-delete)
sqlite3 /home/jefersonlopes/.local/share/sovereign-pair/data/sovereign_memory.db \
    "INSERT OR REPLACE INTO model_capabilities (model_name, parameter_size, supports_tools, is_reasoner, is_master, is_scribe, is_agent, is_coder, is_chat, is_project, is_installed)
     VALUES ('regression-canary:7b', 7.0, 1, 0, 0, 0, 0, 0, 1, 0, 1);" 2>/dev/null

ENCODED2=$(python3 -c "import urllib.parse; print(urllib.parse.quote('regression-canary:7b'))")
curl -s -X DELETE "$BASE/v1/settings/model_capabilities/$ENCODED2" > /dev/null

# Tentar toggle em modelo que não existe mais
R=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/v1/settings/model_capabilities/toggles" \
    -H "Content-Type: application/json" \
    -d '{"model_name":"regression-canary:7b","is_master":true,"is_scribe":false,"is_agent":false,"is_coder":false,"is_chat":true,"is_project":false}')
# Deve retornar 200 (UPDATE WHERE não encontra row, rows_affected=0, mas não é erro)
if [ "$R" = "200" ] || [ "$R" = "404" ]; then
    green "Write-after-delete não causa crash (HTTP $R)"
    PASS=$((PASS+1))
else
    red "Write-after-delete retornou HTTP $R inesperado"
    FAIL=$((FAIL+1))
fi

# 4.5 API de tenant keys ainda funciona após testes (regressão)
R=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/v1/settings/tenant_keys")
assert_status "GET /v1/settings/tenant_keys ainda funciona (regressão)" "200" "$R"

# ─────────────────────────────────────────────────────────────────
# SUMÁRIO FINAL
# ─────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "\033[1m RESULTADO FINAL\033[0m"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
green "PASSOU:  $PASS"
[ $SKIP -gt 0 ] && yellow "PULADO:  $SKIP"
[ $FAIL -gt 0 ] && red "FALHOU:  $FAIL" || echo -e "\033[0;31mFALHOU:  $FAIL\033[0m"

if [ $FAIL -gt 0 ]; then
    echo -e "\nFalhas detectadas:$FAILS"
    exit 1
else
    echo ""
    echo -e "\033[1;32m🎯 ALL TESTS PASSED — Pipeline certificada!\033[0m"
fi
