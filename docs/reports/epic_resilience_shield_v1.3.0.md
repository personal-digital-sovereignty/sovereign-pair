# Epic: Sovereign Resilience Shield — API Health Guard & Fallback Chains

> **Target:** v1.3.0  
> **Status:** Draft  
> **Origem:** Incidente real — série SGS 800 (PTAX) descontinuada pelo BCB sem aviso, causando falha silenciosa na pipeline de dados macroeconômicos.

---

## 1. Contexto e Problema

O Sovereign Pair depende de **fontes externas de dados** (BCB SGS, Yahoo Finance, ANP) para alimentar o Symbiotic Pipeline. Estas APIs são mantidas por terceiros e podem:

- **Descontinuar séries** sem aviso (como SGS 800 → 404)
- **Alterar schemas** de resposta (JSON keys renomeadas)
- **Implementar rate-limiting** ou geo-blocking
- **Sofrer downtime** temporário (manutenção do BCB, Yahoo bloqueando IPs)

Atualmente, qualquer falha nessas APIs resulta em **artefatos vazios** sem diagnóstico claro para o usuário. O LLM tenta compensar alucinando dados — o pior cenário possível.

---

## 2. Solução Implementada (v1.2.4 — Base)

### 2.1 Fallback Chains (Runtime)

Cada indicador BCB agora possui uma cadeia ordenada de séries alternativas:

```python
FALLBACK_CHAINS = {
    "DOLAR_PTAX": [(10813, "PTAX Venda Média"), (1, "Dólar Comercial Compra"), (3698, "Dólar Livre Venda")],
    "SELIC":      [(432, "SELIC Meta"), (4189, "SELIC Diária")],
    # ...
}
```

Se a série primária retornar HTTP 404 ou erro estruturado do BCB, o sistema automaticamente tenta a próxima. O artefato final mostra `[FALLBACK — série primária indisponível]` na fonte.

### 2.2 Health Check Script

`core/python_workers/health_check_apis.py` valida todas as fontes externas:

```bash
python3 health_check_apis.py          # Visual (terminal)
python3 health_check_apis.py --json   # Machine-readable
python3 health_check_apis.py --ci     # CI/CD: exit 1 on critical failure
```

---

## 3. Épico v1.3.0 — Evolução Planejada

### 3.1 Startup Health Gate (Rust-Side)

**Descrição:** O Motor Rust executa o health check automaticamente no boot do servidor. Se APIs críticas estiverem dead, o sistema:
- Envia alerta via SSE/logs para o frontend
- Marca as tools afetadas como `degraded` na Tool Registry
- O LLM é informado via system prompt que certas ferramentas estão temporariamente indisponíveis

**Implementação:**
- `api.rs` → chamar `health_check_apis.py --json` no startup
- Parsear resultado e atualizar `model_capabilities` com flags de degradação
- Frontend: badge visual `⚠️ APIs Degradadas` na toolbar do Research

### 3.2 Cron Watchdog com Alertas

**Descrição:** Health check periódico (4h) com notificação proativa.

- Integração com systemd timer ou cron
- Se uma API que estava HEALTHY virar DEAD → log de alerta nível WARN
- Se uma API CRITICAL estiver DEAD por >24h → frontendnotification persistente
- Histórico de uptime armazenado em SQLite (`api_health_log`)

### 3.3 Schema Drift Detection

**Descrição:** Validar não apenas o HTTP status, mas a **estrutura** da resposta.

Exemplo: O BCB pode mudar de `{"data": "01/04/2026", "valor": "0.31"}` para outro formato. O health check deve validar:
- Presença das keys esperadas (`data`, `valor`)
- Formato de data parseable
- Valor numérico válido

```python
# Exemplo de schema assertion
def validate_bcb_schema(response_item):
    assert "data" in item, "Missing 'data' key"
    assert "valor" in item, "Missing 'valor' key"
    assert re.match(r'\d{2}/\d{2}/\d{4}', item["data"]), "Date format changed"
    float(item["valor"])  # Must be numeric
```

### 3.4 Yahoo Finance Redundância

**Descrição:** Yahoo Finance é a fonte mais frágil (cookies, geo-blocking, rate-limits). Adicionar fallback para fontes alternativas:

| Ativo | Primária | Fallback 1 | Fallback 2 |
|-------|----------|------------|------------|
| BRENT | Yahoo `BZ=F` | Alpha Vantage | Investing.com Scraper |
| DOLAR | Yahoo `BRL=X` | BCB PTAX (SGS 10813) | AwesomeAPI |
| PETROBRAS | Yahoo `PETR4.SA` | B3 Direct | — |

### 3.5 Rate-Limit Awareness

**Descrição:** Respeitar os limites de cada API para evitar banimentos.

- BCB SGS: sem rate-limit público, mas implementar cooldown de 1s entre requests
- Yahoo Finance: máximo ~2000 req/h → implementar token bucket
- ANP: endpoints frágeis → retry com backoff exponencial

### 3.6 Métricas de Observabilidade (Nexus Integration)

**Descrição:** Expor métricas do health check no Nexus Dashboard (ref: `nexus_llmops_brainstorm.md`).

- Latência média por API (gráfico rolling 7d)
- Uptime % por fonte
- Contagem de fallbacks ativados (alerta se >0 em 24h)
- Última data de dados disponíveis vs data atual (detectar atraso de publicação)

---

## 4. Priorização

| Item | Impacto | Esforço | Prioridade |
|------|---------|---------|------------|
| 3.1 Startup Health Gate | Alto | Baixo | P0 |
| 3.2 Cron Watchdog | Médio | Baixo | P1 |
| 3.3 Schema Drift Detection | Alto | Médio | P1 |
| 3.4 Yahoo Finance Redundância | Alto | Alto | P2 |
| 3.5 Rate-Limit Awareness | Médio | Médio | P2 |
| 3.6 Nexus Integration | Baixo | Alto | P3 |

---

## 5. Referências

- **Incidente-raiz:** SGS 800 → 404 (BCB descontinuou série PTAX sem aviso, 15/04/2026)
- **Health Check atual:** `core/python_workers/health_check_apis.py`
- **Fallback Chains:** `core/python_workers/sovereign_matrix.py` (FALLBACK_CHAINS dict)
- **Docs relacionados:** `docs/reports/nexus_llmops_brainstorm.md`, `docs/reports/agentic_workflows_roadmap.md`
