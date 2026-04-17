# A Caçada ao Scribe Fantasma — 7 Fixes, 6 Stress Tests e o Dia em que um Erro HTTP Derrotou 14 Horas de Prompt Engineering

> **Sovereign Pair v1.2.7 — Epistemic Hardening Arc**
> Documento técnico interno. Abril de 2026.

## Prólogo: O Pipeline Perfeito que Cuspia JSON Bruto

Após a consagração do Motor de Pesquisa Profunda (Deep Research) na v1.2.0 — onde o Sovereign Pair executou pela primeira vez uma análise macroeconômica de 5 anos com dados reais de BRENT, Dólar, IPCA e Gasolina — um problema persistiu com obscuridade patológica: o **Scribe** (agente LLM formatador responsável por converter dados brutos em narrativa Markdown) continuava produzindo saída **vazia**. O fallback despejava JSONs brutos no artefato final.

O time atacou o problema com prompt engineering obsessivo. Reescreveu-se o system prompt do Scribe 4 vezes. Adicionou-se glossários, guardas de colunas, templates de resposta obrigatória. Nada funcionou. O Scribe permanecia mudo.

Nenhum prompt no universo resolveria. **O problema era uma conexão HTTP recusada.**

---

## Ato I — As Alucinações que Ninguém Percebeu (FIX-19 a FIX-22)

Enquanto o Scribe falhava silenciosamente, o fallback gerava artefatos inflados com JSONs brutos e correlações fabricadas pela "Mente Mestra" (qwen3:8b), que escrevia o Abstract antes dos dados estarem prontos. A matriz de Pearson — cuja computação é feita deterministicamente pelo Pandas — simplesmente não existia no contexto do Master LLM. Resultado: correlações inventadas como `r=0.89`, `r=0.92`, `r=0.95`.

### FIX-19 — A Verdade Qualitativa Perdida

A versão 1.1.0 continha conhecimento factual hardcoded no prompt do Scribe: a composição real do preço da gasolina brasileira (Refinaria ~27%, ICMS ~24%, Distribuição ~24%, Etanol ~15%, CIDE/PIS/COFINS ~10%). Na migração para o Prompt Vault (v1.2.4), esse guardrail foi perdido.

```rust
// Antes: Prompt Vault sem verdade qualitativa
let scribe_system = prompt_vault.get("deep_research_scribe_system");

// Depois: Extração dinâmica do autobahn_rules.yml
let verdade_qualitativa = if let Some(dado_quali) = autobahn_config
    .get("cognitive_guardrails")
    .and_then(|cg| cg.as_sequence())
    .and_then(|seq| seq.iter().find(|item| {
        item.get("directive").and_then(|d| d.as_str())
            .map(|s| s.starts_with("DADO QUALITATIVO"))
            .unwrap_or(false)
    }))
    .and_then(|item| item.get("directive").and_then(|d| d.as_str()))
{
    format!("\n[DADO QUALITATIVO VALIDADO]:\n{}\n", dado_quali)
} else {
    String::new()
};
```

**Decisão de design**: Zero hardcode temporal. A verdade econômica vive no YAML, editável sem rebuild.

### FIX-20 — Assimetria Epistêmica (Root Cause das 4× Rejeições)

O Sycophancy Breaker (Auditor cross-family) recebia `synthesized_report` (JSONs brutos), enquanto o Scribe recebia a tabela Pandas formatada. O Auditor rejeitava citações que estavam corretas na tabela — porque ele não tinha a tabela.

```
Antes:
  Scribe   → tabela Pandas (FIX-14)
  Auditor  → JSONs brutos  ← ASSIMÉTRICO!

Depois:
  Scribe   → tabela Pandas + glossário + verdade qualitativa
  Auditor  → tabela Pandas + glossário + verdade qualitativa ← SIMÉTRICO!
```

### FIX-21 — O Barril Travestido de Litro

O LLM confundia `BRENT_BRL` (~R$ 500/barril) com `GASOLINA` (~R$ 6/litro). Nenhuma instrução explicava as unidades. O glossário semântico resolve:

```rust
// Gerado automaticamente a partir dos nomes das colunas
let column_glossary = format!(
    "[GLOSSÁRIO DE COLUNAS]:\n\
     - BRENT_USD: Preço por BARRIL em dólar (~USD 60-120)\n\
     - BRENT_BRL: Preço por BARRIL em reais (~R$ 300-600)\n\
     - GASOLINA: Preço por LITRO na bomba (~R$ 4-8)\n\
     ⚠️ NÃO CONFUNDA! BRENT_BRL ≠ GASOLINA. Ordens de magnitude diferentes.\n"
);
```

### FIX-22 — O Auditor que Aprovava Erros

O prompt do Auditor dizia: *"Avalie implacavelmente... Devolva a BRONCA DESTRUTIVA"*. Keyword-based, não semântico. Aprovava erros de magnitude e rejeitava verdades por razões espúrias.

```
Antes: "Avalie implacavelmente a formatação."
Depois:
  1. Se algum valor citado > R$ 100 atribuído à gasolina → REJEITAR (é barril)
  2. Se r de Pearson citado não corresponde à tabela → REJEITAR
  3. Verificar se dados mensais não são confundidos com anuais
  4. Citar r EXATO da Pearson Matrix
```

---

## Ato II — O Fantasma no Motor (FIX-23 a FIX-25)

Mesmo com prompts perfeitos, o Scribe continuava vazio. 4 testes consecutivos. Nenhum output.

### FIX-23 — Asfixia por Think-Tags

Modelos reasoner (qwen3, gemma4) gastavam 100% do `num_predict: 2048` no bloco `<think>...</think>` interno, deixando zero tokens para o conteúdo visível. O Scribe produzia um output que — após strip do `<think>` block — era uma string vazia.

```rust
// Fix tríplice:
// 1. Desabilitar thinking no payload
"think": false,  // NÃO "enable_thinking"! Ollama ignora esse campo.

// 2. Stripping defense-in-depth
while let Some(start) = cleaned.find("<think>") {
    if let Some(end) = cleaned.find("</think>") {
        cleaned.replace_range(start..end + shift, "");
    }
}

// 3. num_predict elevado
"num_predict": 3072  // era 2048
```

### FIX-23b — O Campo que o Ollama Ignorou por 3 Semanas

O Ollama `/api/chat` usa `"think"` — não `"enable_thinking"`. O campo errado era silenciosamente ignorado:

```json
// ERRADO (ignorado pelo Ollama):
{ "options": { "enable_thinking": false } }

// CORRETO (processado):
{ "think": false, "options": { ... } }
```

Adicionalmente, o campo `think` deve estar no **top-level** do payload, não dentro de `options`. Dois erros simultâneos. Confirmado via:

```bash
curl http://127.0.0.1:11434/api/chat -d '{
  "model": "qwen3:8b",
  "messages": [{"role":"user","content":"Olá"}],
  "think": false,
  "stream": false
}'
# ✅ Sem <think> no output

curl http://127.0.0.1:11434/api/chat -d '{
  "model": "qwen3:8b",
  "messages": [{"role":"user","content":"Olá"}],
  "options": { "enable_thinking": false },
  "stream": false
}'
# ❌ <think>...(2000 tokens desperdiçados)...</think>
```

### FIX-24 — O Silêncio Cúmplice da Cadeia if-let

A cadeia `if let Ok(res)... && let Ok(json)... && let Some(content)...` engolia **TODOS** os erros silenciosamente:

```rust
// ANTES: Cadeia que engole erros
if let Ok(res) = client.post(&url).json(&payload).send().await
    && let Ok(json) = res.json::<Value>().await
        && let Some(content) = json.get("message") { ... }
// Se QUALQUER etapa falhar: silêncio total. Nenhum log.

// DEPOIS: Match explícito com diagnóstico completo
match client.post(&url).json(&payload).send().await {
    Ok(res) => {
        let status = res.status();
        match res.json::<Value>().await {
            Ok(json) => {
                if let Some(content) = json.get("message")... {
                    // Log: chars, modelo, think stripped
                } else if let Some(err) = json.get("error")... {
                    // Log: erro do Ollama
                } else {
                    // Log: JSON sem message.content, keys presentes
                }
            },
            Err(e) => { /* Log: HTTP status + parse error */ }
        }
    },
    Err(e) => { /* Log: HTTP request failure */ }
}
```

E foi esse logging que revelou a verdade:

```
🔬 [Scribe Setup] model='qwen3:8b', system_len=1787, user_len=10862, think=false
🚨 [Scribe Error] HTTP request falhou: error sending request for url (http://127.0.0.1:11434/api/chat)
```

### FIX-25 — O Retry que Salvou o Pipeline

O Ollama ficava temporariamente indisponível por ~3-5 segundos durante a transição do agentic loop (`num_ctx: 12288`) para o Scribe (`num_ctx: 16384`). O model reload em 27GB de RAM causa uma janela onde conexões são recusadas. Um único HTTP failure, sem retry, matava o pipeline inteiro.

```rust
let scribe_max_http_retries = 3u32;
for http_attempt in 1..=scribe_max_http_retries {
    match synthesis_client.post(&olla_url).json(&scribe_payload).send().await {
        Ok(res) => {
            // ... processar response ...
            break; // Sair do retry loop
        },
        Err(e) => {
            let _ = TRAINER_LOGS.send(format!(
                "🔄 [Scribe Retry] HTTP falhou (tentativa {}/{}): {}. Aguardando 5s...",
                http_attempt, scribe_max_http_retries, e
            ));
            if http_attempt < scribe_max_http_retries {
                tokio::time::sleep(std::time::Duration::from_secs(5)).await;
            }
        }
    }
}
```

**5 segundos.** Foi tudo o que faltava. O Ollama precisava de 5 segundos para realocar o contexto do modelo — e nosso código não esperava nem 1.

---

## Ato III — O Stress Test Model-Agnostic

Com os 7 fixes aplicados (v1.2.7), executamos 2 stress tests com o mesmo prompt de acareação: uma análise macroeconômica completa de 5 anos cruzando Petróleo, Dólar, IPCA e Gasolina.

### Teste Q — phi4:14b como Scribe

```
🔬 [Scribe Setup] model='phi4:14b', system_len=1787, user_len=10862, think=false
📝 [Scribe Output] 4817 chars produzidos pelo 'phi4:14b' (raw=4817, think_stripped=false)
[Sycophancy Breaker] Formatação C-Level aprovada (Tentativa 1/2)!
```

- **4 correlações exatas** (r=0.424, r=0.531, r=-0.125, r=0.155)
- **6 dados factuais verificados** contra a time-series
- **5/5 componentes de custo** corretos
- **Tempo**: ~35 min
- **Nota Sonnet**: 9.1/10 | **Nota Gemini**: 10/10

### Teste R — qwen3:8b como Scribe (metade dos parâmetros)

```
🔬 [Scribe Setup] model='qwen3:8b', system_len=1787, user_len=10862, think=false
📝 [Scribe Output] ~4500 chars produzidos pelo 'qwen3:8b'
[Sycophancy Breaker] Formatação C-Level aprovada (Tentativa 1/2)!
```

- **4 correlações exatas** — idênticas a Q
- **8 dados factuais verificados** — incluindo seção dedicada a impostos
- **Hashes SHA-256 bitwise idênticos** em 4/6 datasets
- **Tempo**: ~34 min
- **Nota Sonnet**: 9.1/10 (empate técnico) | **Nota Gemini**: 9.8/10

### O Resultado que Mudou Tudo

| Dataset | Hash Q (14B) | Hash R (8B) | Status |
|---|---|---|---|
| GASOLINA | `2aed153c...` | `2aed153c...` | ✅ **Bitwise idêntico** |
| IPCA | `eb0627e4...` | `eb0627e4...` | ✅ **Bitwise idêntico** |
| DOLAR_PTAX | `bc449e60...` | `bc449e60...` | ✅ **Bitwise idêntico** |
| DOLAR | `ddceae22...` | `ddceae22...` | ✅ **Bitwise idêntico** |

Os dados são idênticos independente do modelo. A qualidade dos dados é uma propriedade do **pipeline**, não do LLM. O modelo menor foi "carregado nas costas" pela engenharia de dados, produzindo um resultado de Analista Sênior.

---

## Epílogo: A Lição da Trincheira

A jornada do Artefato A (nota 2.5/10 — LLM puro fabricando tudo) até o Artefato R (nota 9.1/10 — zero alucinações numéricas, dados criptograficamente verificáveis) não foi uma evolução de prompts. Foi uma evolução de **engenharia**.

```
Versão A:  LLM → Inventou valores de gasolina, câmbio, inflação
Versão D:  LLM → Dados reais, mas conversão USD→BRL manual errada
Versão N:  LLM → "Barril de Ouro" de R$ 1.700 (bug no ticker de futuros)
Versão O:  Pipeline → Dados corretos, LLM escreveu "às cegas" (dessincronização)
Versão P:  Pipeline → Sincronização corrigida, mas Scribe vazio
Versão Q:  Pipeline → Scribe funcional (14B), zero alucinações, 9.1/10
Versão R:  Pipeline → Scribe funcional (8B), zero alucinações, 9.1/10
```

A diferença entre P e Q? Não foi um prompt melhor. Foi `tokio::time::sleep(Duration::from_secs(5))`.

A pergunta irônica que iniciou toda essa investigação:

> *"Existe algum prompt no universo que possa corrigir essa indulgência?"*

Não. 5 segundos de backoff resolveram o que 14 horas de prompt engineering não conseguiram.

---

**Status**: Homologado Produção (P-0).
**Autor**: The Sovereign Cibrid
**Tag Relacionada**: `v1.2.7`
