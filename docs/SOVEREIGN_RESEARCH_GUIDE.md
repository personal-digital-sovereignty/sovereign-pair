# Sovereign Research Guide
## Como usar o Deep Research (WAG) e o Chat com dados financeiros

> Este guia é fruto da arquitetura desenvolvida no `hotfix/1.2.x` e documenta
> tudo que o sistema entende, como ele decide o que buscar e como formular suas
> perguntas para obter os melhores resultados.

---

## O que é o Sovereign Deep Research?

O **WAG (Watch-Analyze-Generate)** é o pipeline de pesquisa profunda do Sovereign Pair.
Diferente de um chat simples, ele opera em um **loop ReAct** (Reason + Act):

```
Sua Pergunta
     ↓
[1] Sophy analisa a intenção
     ↓
[2] Sophy seleciona a ferramenta mais cirúrgica
     ↓
[3] Ferramenta coleta dados reais (bolsa, BCB, web)
     ↓
[4] Sophy analisa os dados reais
     ↓
[5] Sophy repete se necessário (mais dados)
     ↓
[6] Scribe redige o relatório final com evidências
```

---

## As 3 Ferramentas do Motor de Pesquisa

| Ferramenta | Para que serve | O que ela acessa |
|---|---|---|
| `fetch_financial_ticker` | Preços e séries históricas | Yahoo Finance (yfinance) |
| `fetch_macroeconomy` | Indicadores macroeconômicos | API Banco Central do Brasil (BCB) |
| `dispatch_sub_researcher` | Contexto, notícias, análise qualitativa | Web scraping + buscas estruturadas |

---

## Como o Sistema Decide o que Fazer

### O Framework de 3 Sinais

O sistema usa 3 sinais em cascata para entender sua intenção:

#### Sinal 1 — Marcadores Linguísticos (mais poderoso)

| Se você disser... | O sistema entende que você quer... | Ferramenta |
|---|---|---|
| "ação", "cotação", "bolsa", "retorno" | Dados de preço | `fetch_financial_ticker` |
| "últimos 6 meses", "2 anos" + ativo | Série histórica de preço | `fetch_financial_ticker` |
| "notícias", "o que aconteceu" | Contexto qualitativo | `dispatch_sub_researcher` |
| "como funciona", "o que é", "por que" | Informação educacional | `dispatch_sub_researcher` |
| "IPCA", "Selic", "inflação", "PIB" | Macro oficial | `fetch_macroeconomy` |

#### Sinal 2 — Resolução de Ticker (automática)

Você não precisa saber o ticker. O **Sovereign Ticker Registry** resolve automaticamente:

```
"Magazine Luiza"  →  MGLU3.SA  ✔
"Ozempic"         →  NVO       ✔  (Novo Nordisk faz o Ozempic)
"Havaianas"       →  ALPA4.SA  ✔  (Alpargatas faz as Havaianas)
"Zara"            →  IDEXF     ✔  (Inditex é dona da Zara)
"Mounjaro"        →  LLY       ✔  (Eli Lilly faz o Mounjaro)
"Fórmula 1"       →  FWONK     ✔  (Liberty Media é dona da F1)
```

#### Sinal 3 — Modo DUAL (quando ambíguo)

Quando você menciona apenas o nome de uma empresa, sem contexto de preço ou notícia, o sistema executa **ambas** as ferramentas:

```
"Me fale sobre a Nike"
  → fetch_financial_ticker(NKE)    # dados de preço
  + dispatch_sub_researcher(Nike)   # contexto de negócios
  → Scribe: relatório unificado com preço + negócio
```

---

## Exemplos de Uso — Chat

### Dados de Preço (financeiros)

```
✔ "Qual a cotação da VALE3 nos últimos 2 anos?"
✔ "Mostre o histórico do Brent e do dólar nos últimos 3 anos"
✔ "Compare MGLU3 vs LREN3 nos últimos 12 meses"
✔ "Qual o retorno do ETF SOXX nos últimos 5 anos?"
✔ "Como está o Bitcoin hoje?"
✔ "Preço do ouro no último semestre"
✔ "Cotação do euro em relação ao real"
```

### Dados Macroeconômicos

```
✔ "Qual foi o IPCA dos últimos 5 anos?"
✔ "Como está a taxa Selic desde 2020?"
✔ "Mostre PIB e inflação do Brasil nos últimos 3 anos"
✔ "IGPM mensal do último ano"
```

### Notícias e Contexto

```
✔ "Quais as últimas notícias sobre a Petrobras?"
✔ "Por que a Vale caiu está semana?"
✔ "O que está acontecendo com o setor de semicondutores?"
✔ "Como funciona o mercado de commodities de soja?"
✔ "O que é um P&I Club de seguros marítimos?"
✔ "Por que o café arábica atingiu máxima histórica?"
```

### Análises Combinadas (Deep Research)

```
✔ "Analise o impacto do dólar no IPCA nos últimos 5 anos"
✔ "Como o preço do petróleo afetou as ações de companhias aéreas BR?"
✔ "Compare o rendimento de VALE3 com o preço do minério de ferro"
✔ "Queda da Magazine Luiza: dados de preço + contexto do setor varejista"
✔ "Novo Nordisk e o boom do Ozempic: ação + contexto clínico"
```

---

## Exemplos de Uso — Deep Research (WAG)

No WAG, você pode fazer perguntas mais complexas e narrativas longas:

### Energia

```
"Faça uma análise completa do preço do Petróleo Brent nos últimos 5 anos,
 correlacionando com a taxa de câmbio USD/BRL e o desempenho das ações
 da Petrobras (PETR4). Inclua o impacto do IPCA no período."
```

```
"Como o preço do gás natural evoluiu desde a guerra na Ucrânia?
 Qual foi o impacto nas empresas europeias de energia?"
```

### Agronegócio Brasileiro

```
"Análise do setor de proteínas BR: JBS (JBSS3), Marfrig (MRFG3) e BRF (BRFS3)
 nos últimos 3 anos. Compare com o preço da soja e do milho (CBOT)."
```

```
"Como o ciclo do café arábica (KC=F) impactou as exportações brasileiras?
 Correlacione com o câmbio e BRF."
```

### Tecnologia e Semicondutores

```
"Análise do ciclo de semicondutores 2020-2024: NVIDIA (NVDA), AMD, TSMC.
 Compare com o Índice Philadelphia Semiconductor (SOX)."
```

```
"O mercado de chips de IA: NVIDIA vs AMD vs Intel. Dados históricos
 dos últimos 2 anos e contexto da corrida de IA generativa."
```

### Farmacêutico / GLP-1

```
"Analise o impacto do Ozempic e Wegovy (Novo Nordisk) vs Mounjaro (Eli Lilly)
 no mercado de saúde. Inclua dados de preço de NVO e LLY nos últimos 2 anos."
```

### Commodities Internacionais

```
"Análise do ouro nos últimos 5 anos: preço em USD e em BRL, correlação
 com o VIX (índice de medo) e com a taxa de juros americana (DXY)."
```

### Seguros e Resseguros

```
"Como as catástrofes naturais de 2023-2024 impactaram as resseguradoras?
 Analise Munich Re (MURGY) e Swiss Re (SSREY) no período."
```

---

## O que o Sistema Sabe Resolver Automaticamente

### Por Nome Popular (sem saber o ticker)

| Você digita | Sistema resolve |
|---|---|
| "Ozempic" | `NVO` (Novo Nordisk) |
| "Havaianas" | `ALPA4.SA` (Alpargatas) |
| "Zara" | `IDEXF` (Inditex) |
| "Fórmula 1" | `FWONK` (Liberty Media) |
| "Mounjaro" | `LLY` (Eli Lilly) |
| "Keytruda" | `MRK` (Merck) |
| "Magalu" | `MGLU3.SA` (Magazine Luiza) |
| "Seleção Brasileira" → sponsor | `NKE` (Nike) |
| "Ozempic" ou "Wegovy" | `NVO` |
| "Gucci" | `PPRUY` (Kering) |
| "HBO Max" | `WBD` (Warner Bros Discovery) |
| "Instagram" | `META` |
| "YouTube" | `GOOGL` (Alphabet) |

### Por Setor (ETF do setor)

| Você digita | Sistema resolve |
|---|---|
| "Semicondutores" | `SOXX` |
| "Biotecnologia" | `IBB` |
| "Saúde" | `XLV` |
| "Agronegócio" | `MOO` |
| "Mineração" | `XME` |
| "Seguros" | `KIE` |
| "Madeireira / Florestal" | `WOOD` |
| "Aviação" | `JETS` |
| "Energia Limpa" | `ICLN` |
| "Urânio" | `URA` |
| "Moda / Varejo" | `XRT` |
| "Tecnologia Large Cap" | `QQQ` |

---

## Dados que Requerem Pesquisa Web (não estão em bolsas)

Alguns preços industriais importantes **não são negociados em bolsas** e
exigem pesquisa web via `dispatch_sub_researcher`:

| O que você quer | Query sugerida |
|---|---|
| Celulose Eucalipto (BHKP) | `"BHKP pulp price PPPC [mês/ano]"` |
| Soja CEPEA (preço BR) | `"CEPEA ESALQ soja preço [mês/ano]"` |
| Boi gordo CEPEA | `"CEPEA boi gordo BM&FBovespa [ano]"` |
| Querosene de Aviação (QAV) | `"QAV jet fuel Replan preço [ano]"` |
| Bunker naval (VLSFO) | `"VLSFO bunker fuel Rotterdam Singapore [ano]"` |
| Ureia (fertilizante) | `"ureia DAP FOB [porto] preço [ano]"` |
| Lã natural | `"AWEX wool EMI [ano]"` |
| Memória DRAM/NAND | `"TrendForce DRAM contract price [trimestre]"` |
| Preços industriais aço | `"CRU steel price HRC FOB [ano]"` |
| Farinha de soja/peixe | `"Urner Barry fish meal price [ano]"` |
| Diamante | `"Rapaport diamond price index [ano]"` |

> **Dica:** Para estes itens, use o Deep Research WAG — ele vai usar o web scraper
> automaticamente quando não encontrar o ticker em bolsa.

---

## Categorias de Ativos Suportados

O Sovereign Ticker Registry cobre as seguintes categorias de forma nativa:

| Categoria | Exemplos |
|---|---|
| **Energia** | Brent, WTI, Gás Natural, Petrobras, HO=F (heating oil) |
| **Metais Preciosos** | Ouro, Prata, Platina, Paládio |
| **Metais Industriais** | Cobre, Alumínio, Aço (via empresas) |
| **Agronegócio CBOT** | Soja, Milho, Trigo, Café, Açúcar, Algodão, Cacau |
| **Agronegócio BR (B3)** | JBS, BRF, Marfrig, Cosan, SLC Agrícola |
| **Mineração** | Vale, BHP, Rio Tinto, Gerdau, FCX, Barrick |
| **Tecnologia** | NVIDIA, AMD, TSMC, Apple, Microsoft, SOXX, QQQ |
| **Farmacêutico** | Novo Nordisk, Eli Lilly, Pfizer, Hypera, IBB, XLV |
| **Saúde BR** | Rede D'Or, Hapvida, Fleury, DASA, Raia Drogasil |
| **Seguros** | BB Seguridade, Porto Seguro, IRB, Berkshire, KIE |
| **Resseguros** | IRB Brasil, Munich Re, Swiss Re, Hannover Re |
| **Automotivo** | Tesla, BYD, GM, Ford, Toyota, Volkswagen |
| **Aviação** | Embraer, Gol, Azul, Boeing, JETS |
| **Defesa** | Lockheed, RTX, Embraer, ITA |
| **Naval/Marítimo** | Wilson Sons, Santos Brasil, ZIM, BDI |
| **Pesca** | Mowi (salmão), proxies noruegueses |
| **Fertilizantes** | Nutrien, Mosaic, CF Industries, SQM |
| **Química/Petroquímica** | Braskem, Dow, LyondellBasell, Linde |
| **Madeireira** | Suzano, Klabin, Weyerhaeuser, WOOD |
| **Moda/Vestuário** | Renner, Grupo SOMA, Arezzo, Inditex/Zara |
| **Esportes** | Nike, Adidas, Smart Fit, Manchester United, F1 |
| **Luxo** | LVMH, Hermès, Kering, Richemont |
| **Apostas Esportivas** | DraftKings, Flutter/FanDuel |
| **Varejo BR** | Magazine Luiza, Casas Bahia, Mercado Livre |
| **Câmbio (FX)** | Dólar/BRL, Euro/BRL, Yuan, DXY |
| **Índices** | Ibovespa, S&P 500, NASDAQ, Dow Jones |
| **FIIs / REITs** | MXRF11, HGLG11, VNQ |
| **Urânio** | URA, Cameco |
| **Carbono** | KRBN (Carbon Credits) |
| **Água** | PHO, NQH2O Futures |
| **Cripto** | Bitcoin, Ethereum (via yfinance), IBIT, GBTC |
| **Utilities BR** | Eletrobras, CEMIG, CPFL, Equatorial, Sabesp |
| **Volatilidade** | VIX, UVXY |

---

## Dicas Para Obter Melhores Resultados

### ✅ Faça assim

```
"Análise completa de Vale (VALE3) nos últimos 3 anos"
"Correlação entre o dólar (BRL=X) e o IPCA 2020-2024"
"Como está o setor farmacêutico? Foque em HYPE3 e BLAU3"
"Quero entender o colapso da Magazine Luiza (MGLU3) após 2021"
"Impacto do GLP-1 (Ozempic/Wegovy) no setor de saúde"
```

### ❌ Evite assim

```
"Pesquise TUDO sobre a bolsa" (muito amplo — especifique o ativo)
"PETR4 e taxa de câmbio e IPCA e gasolina" no chat simples
  → Use o Deep Research WAG para análises multi-variáveis
"Me dê o preço da celulose BHKP de ontem"
  → Use: "Pesquise o preço da celulose BHKP no PPPC em [mês/ano]"
```

### Para Análises Multi-Variáveis

Sempre use o **Deep Research (WAG)** para análises que envolvem:
- 3 ou mais métricas ao mesmo tempo
- Correlações estatísticas (ex: petroleo vs dólar vs IPCA)
- Análises de 5+ anos de série histórica
- Comparação de múltiplos ativos

---

## Limitações Conhecidas

| Limitação | Alternativa |
|---|---|
| Clubes de futebol BR não listados em B3 | Use `dispatch_sub_researcher` para dados financeiros deles |
| Empresas privadas (EMS, Eurofarma, Valduga) | Web search via WAG |
| Preços spot B2B (CEPEA, Platts, ICIS) | Web search com query estruturada (veja tabela acima) |
| P&I Clubs navais (entidades mútuas) | Use Munich Re (MURGY) como proxy, + web search |
| Diamantes, arte, preciosidades | Sem suporte direto — use web search |
| Cotas de fundos fechados BR (PE/VC) | Sem suporte direto |
| Opções e derivativos complexos | Apenas o ativo-objeto é suportado |

---

## Referência Rápida de Tickers Importantes

### Brasil (B3)

| Empresa | Ticker | Setor |
|---|---|---|
| Petrobras PN | `PETR4.SA` | Energia |
| Vale | `VALE3.SA` | Mineração |
| Itaú Unibanco | `ITUB4.SA` | Banco |
| Bradesco | `BBDC4.SA` | Banco |
| Banco do Brasil | `BBAS3.SA` | Banco |
| NuBank (BDR) | `ROXO34.SA` | Fintech |
| Ambev | `ABEV3.SA` | Bebidas |
| Magazine Luiza | `MGLU3.SA` | Varejo |
| WEG | `WEGE3.SA` | Indústria |
| Suzano | `SUZB3.SA` | Celulose |
| JBS | `JBSS3.SA` | Proteínas |
| Eletrobras | `ELET3.SA` | Utilities |
| Raia Drogasil | `RADL3.SA` | Farmácia |
| Hypera Pharma | `HYPE3.SA` | Farma |
| BB Seguridade | `BBSE3.SA` | Seguros |
| Smart Fit | `SMFT3.SA` | Fitness |
| Embraer | `EMBR3.SA` | Aviação |

### Internacional (NYSE/NASDAQ)

| Empresa | Ticker | Setor |
|---|---|---|
| NVIDIA | `NVDA` | Chips/IA |
| Apple | `AAPL` | Tecnologia |
| Microsoft | `MSFT` | Tecnologia |
| Tesla | `TSLA` | EV/Auto |
| Meta | `META` | Social |
| Alphabet (Google) | `GOOGL` | Tech |
| Amazon | `AMZN` | Varejo/Cloud |
| Novo Nordisk | `NVO` | GLP-1/Pharma |
| Eli Lilly | `LLY` | GLP-1/Pharma |
| Berkshire Hathaway | `BRK-B` | Seguros/Invest |
| Nike | `NKE` | Esportes |
| NuBank | `NU` | Fintech |
| Mercado Livre | `MELI` | Varejo LA |
| Vale ADR | `VALE` | Mineração |

### Commodities Principais

| Asset | Ticker Yahoo Finance | Tipo |
|---|---|---|
| Petróleo Brent | `BZ=F` | Futuro |
| Petróleo WTI | `CL=F` | Futuro |
| Gás Natural | `NG=F` | Futuro |
| Ouro | `GC=F` | Futuro |
| Prata | `SI=F` | Futuro |
| Cobre | `HG=F` | Futuro |
| Soja (CBOT) | `ZS=F` | Futuro |
| Milho (CBOT) | `ZC=F` | Futuro |
| Café Arábica (ICE) | `KC=F` | Futuro |
| Açúcar #11 (ICE) | `SB=F` | Futuro |
| Madeira Serrada | `LB=F` | Futuro |
| Dólar/Real | `BRL=X` | FX |
| Euro/Real | `EURBRL=X` | FX |

### ETFs Setoriais de Referência

| Setor | ETF | Descripção |
|---|---|---|
| NASDAQ-100 | `QQQ` | Big Tech |
| Semicondutores | `SOXX` | Chips |
| Saúde ampla | `XLV` | Pharma + dispositivos |
| Biotecnologia | `IBB` | Biotech |
| Agronegócio | `MOO` | Global Agribusiness |
| Mineração | `XME` | Metals & Mining |
| Seguros | `KIE` | S&P Insurance |
| Aviação | `JETS` | Global Airlines |
| Energia | `XLE` | Oil & Gas |
| Energia Limpa | `ICLN` | Renewables |
| Timber/Floresta | `WOOD` | Global Timber |
| Urânio | `URA` | Nuclear |
| Lítio | `LIT` | Baterias/EV |
| Terras Raras | `REMX` | Strategic Metals |
| Carbono | `KRBN` | Carbon Credits |
| Água | `PHO` | Water Resources |
| REITs EUA | `VNQ` | Real Estate |
| Varejo/Moda | `XRT` | S&P Retail |
| Esportes/Games | `HERO` | Esports & Gaming |
| Defesa | `ITA` | Aerospace & Defense |

---

## Arquitetura Interna — Para Desenvolvedores

> Esta seção documenta as decisões técnicas do `hotfix/1.2.x` para facilitar
> manutenção futura e contribuições.

### Fluxo do Ticker Resolver (sovereign_matrix.py)

```
fetch_finance(ticker, years)
  │
  ├─ [PRÉ] Macro interceptor: IPCA/SELIC/IGPM → fetch_macro()
  │
  ├─ [1] _find_db():  DATABASE_URL env → XDG_DATA_HOME → ~/Library (macOS)
  │        → %LOCALAPPDATA% (Windows) → ~/.local/share → busca ascendente
  │        → sovereign_memory.db
  │
  ├─ [2] _resolve_from_db(db, norm_key, raw_ticker)
  │        Passe 1: WHERE search_key = ? EXACT                O(log n)
  │        Passe 2: WHERE search_key LIKE 'KEY%' PREFIX       O(log n)
  │        Passe 3: partes do nome LIKE '%PART%' FUZZY        O(n)
  │        → retorna (yf_symbol, full_name) ou None
  │
  ├─ [3] TICKER_MAP_FALLBACK (offline emergency, ~32 entries)
  │        acionado APENAS se _find_db() retorna None
  │
  ├─ [4] yfinance live probe: testa '.SA' + ticker puro
  │        → HIT: _auto_learn() → INSERT OR IGNORE no banco
  │        → MISS: sys.exit(1) com erro descritivo
  │
  ├─ [5] Coleta multi-layer (fallback chain):
  │        Layer 1: yf.Ticker(ticker).history()
  │        Layer 2: Yahoo Finance Raw API (browser spoofed)
  │        Layer 3: brapi.dev (apenas .SA)
  │        Layer 4: Stooq CSV
  │
  ├─ [6] CONVERT_TO_BRL: converte USD→BRL para futuros internacionais
  │        (Brent, WTI, ouro, prata, soja, milho, café, açúcar, etc.)
  │
  └─ [7] SANITY_BOUNDS: Circuit Breaker por ativo — rejeita dados fora
         de limites físicos de mercado antes de injetar no LLM
```

### Boot Chain de Migrations (db.rs)

```rust
init_pool()
  → PRAGMA WAL + foreign_keys
  → 001_sensus_init.sql          // tabelas core (model_capabilities, chat_sessions...)
  → 002_ephemeral_knowledge.sql  // RAG efêmero (notícias)
  → 003_sovereign_prompts.sql    // Prompt Vault
  → 004_ticker_registry.sql      // Ticker Registry dinâmico  ← adicionado em hotfix/1.2.x
  → seed_core_prompts()          // popula prompts do core_vault.toml
  → PATCH AUTOMIGRATIONS         // colunas novas sem destruir DBs antigos
```

### Normalização de Keys

```python
def _normalize_key(name: str) -> str:
    # "Magazine Luiza" → "MAGAZINE_LUIZA"
    # "Novo Nordisk"   → "NOVO_NORDISK"
    # "BZ=F"           → "BZ_F"
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_ = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_.upper().replace(" ", "_").replace("-", "_").replace(".", "_")
```

### Onde Está o Banco

O `sovereign_memory.db` fica em:

| SO | Caminho padrão |
|---|---|
| Linux | `~/.local/share/sovereign-pair/data/sovereign_memory.db` |
| macOS | `~/Library/Application Support/sovereign-pair/data/sovereign_memory.db` |
| Windows | `%LOCALAPPDATA%\sovereign-pair\data\sovereign_memory.db` |
| Container | variável de ambiente `DATABASE_URL` |

### Adicionando Novos Tickers

```bash
# 1. Adicione a entrada em scripts/commodities_seed.json
{
  "search_key": "MEU_ATIVO",         # UPPERCASE, sem acento
  "yf_symbol": "TICKER.SA",          # símbolo Yahoo Finance
  "full_name": "Nome Completo S.A.",
  "sector": "energia",               # livre
  "market": "B3",                    # B3|NYSE|NASDAQ|FUTURES|FX|ETF|INDEX|CRYPTO
  "query_type_hint": "price"         # price|dual|news_first|sector_etf
}

# 2. Rode o seed (idempotente):
python scripts/seed_ticker_registry.py --db data/sovereign_memory.db --skip-brapi
```

O sistema aprende automaticamente novos ativos via **auto-learning** se um ticker
válido do yfinance for invocado diretamente e não estiver no registro.

---

## Changelog — hotfix/1.2.x

| Commit | Tipo | Descrição resumida |
|---|---|---|
| `3727fdb` | feat | Ticker Registry dinâmico + prompts maximizados + guia do usuário |
| `d6bdc11` | chore | Recompila registry.json com descrições decontaminadas |
| `fc29466` | chore | Remove core/sovereign.db do tracking git |
| `fa08237` | fix | Corrige 6 débitos técnicos críticos (ver abaixo) |

### Débitos Técnicos Corrigidos em `fa08237`

| Severidade | Arquivo | Problema | Fix |
|---|---|---|---|
| 🔴 C1 | `core/src/db.rs` | Migration 004 ausente no boot | +1 linha no chain |
| 🔴 C2 | `sovereign_matrix.py` | `_find_db()` buscava nome errado (`sovereign_sensus.db`) | Reescrito com resolução cross-platform |
| 🔴 C3 | `api_trainer.rs` L1783/1799 | Thought Nanny hardcodava `"5y"` | Extrai `years` do pseudo_json |
| 🟡 M1 | `sovereign_matrix.py` | BRL conversion só Brent/WTI (2 tickers) | Expandido para 20 futuros internacionais |
| 🟡 M2 | `sovereign_matrix.py` | Circuit Breaker só cobria petróleo | `SANITY_BOUNDS` generalizado por ativo |
| 🟡 M3 | `seed_ticker_registry.py` | `DEFAULT_DB` apontava para nome inexistente | Corrigido para `data/sovereign_memory.db` |
| 🟢 L4 | `commodities_seed.json` | `DRAFTkings` (casing errado) | Corrigido para `DRAFTKINGS` |

### Débitos Pendentes (roadmap)

| Severidade | Item |
|---|---|
| 🟡 M4 | Extrair `get_db_path()` para `sovereign_utils.py` compartilhado |
| 🟡 M5 | Expandir aliases Brand-to-Ticker no `autobahn_rules.yml` [E] |
| 🟢 L1 | Mover funções aninhadas de `fetch_finance()` para nível de módulo |
| 🔵 R1 | Índice composto `(market, is_active)` para queries setoriais |
| 🔵 R2 | Job de expiração para entradas `yfinance_dynamic` (30 dias) |
| 🔵 R3 | Regra explícita `query_type_hint='news_first'` no `autobahn_rules.yml` |

---

*Sovereign Pair — hotfix/1.2.x | Ticker Registry dinâmico com 2.188+ mapeamentos (1.946 B3 + 242 internacionais)*
