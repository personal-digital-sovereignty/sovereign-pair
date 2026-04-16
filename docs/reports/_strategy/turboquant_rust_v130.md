# Strategy: TurboQuantMSE em Rust — Sovereign Vault RAG v1.3.0

> **Classificação:** Estratégia de Implementação
> **Target:** v1.3.0 (Epic: Resilience Shield + Memory Sovereignty)
> **Paper:** [TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate](https://arxiv.org/abs/2504.19874) (Google Research, 2025)
> **Referência:** [rag-embedding-compression-lab](https://github.com/marcos2872/rag-embedding-compression-lab) (MarcosBritoDev)
> **Inspiração complementar:** [Exo Labs](https://exolabs.net/) (inferência distribuída), [LLM em Pentium 1997](https://www.techspot.com/news/106136-llama-language-model-tamed-ancient-windows-98-computer.html)

---

## 1. Tese Central

> **"50 linhas de código fazem mais diferença do que 300 iterações de otimização."**
>
> O TurboQuant demonstra que uma rotação ortogonal aleatória (1 operação) uniformiza
> a distribuição de energia entre dimensões de embeddings, permitindo que um quantizador
> escalar simples (Lloyd-Max) atinja desempenho quase ótimo sem precisar treinar
> codebooks específicos por dataset.

**Para o Sovereign:** Em 27GB de RAM com 3-4 modelos LLM simultaneamente, cada MB de
embedding comprimido é um MB liberado para contexto do LLM. Com TurboQuant 4-bit,
o sistema suporta **8× mais documentos** na mesma máquina sem sacrificar qualidade de busca.

---

## 2. Análise do Algoritmo (Paper + Implementação)

### 2.1 Pipeline Matemático

```
x (float32, d=384)
  │
  ├─ 1. NORMALIZAÇÃO
  │    norm = ||x||₂ (armazena como f16, 2 bytes)
  │    x̂ = x / norm → vetor unitário em S^(d-1)
  │
  ├─ 2. ROTAÇÃO ORTOGONAL
  │    R ← QR(Normal(0,1), d×d) — calculada UMA VEZ por (dim, seed)
  │    y = x̂ × Rᵀ → coordenadas redistribuídas uniformemente
  │    
  │    POR QUE FUNCIONA: Embeddings de modelos neurais têm energia
  │    não-uniforme (umas dimensões carregam mais info que outras).
  │    A rotação R (medida de Haar) equaliza a variância: cada yᵢ
  │    seguirá a distribuição Beta((d-1)/2, (d-1)/2) ≈ N(0, 1/√d).
  │    Para d=384: σ ≈ 0.051. Extremamente concentrada em 0.
  │
  ├─ 3. QUANTIZAÇÃO ESCALAR (Lloyd-Max)
  │    Codebook: 2^b centróides calculados pela PDF teórica da Beta.
  │    b=4 → 16 centróides → ~100 bytes de codebook, REUTILIZÁVEL.
  │    Para cada yᵢ: k(i) = argmin_k |yᵢ - c_k| via searchsorted.
  │
  └─ 4. BIT-PACKING
       b=4: 2 índices por byte → d×b/8 = 384×4/8 = 192 bytes/vetor
       b=2: 4 índices por byte → d×b/8 = 384×2/8 = 96 bytes/vetor

ARMAZENADO POR VETOR: {packed_indices: [192B], norm: [2B]} = 194 bytes
                      vs FLOAT32: 384 × 4 = 1536 bytes
                      COMPRESSÃO: 7.9×
```

### 2.2 Resultados Validados (Referência Python)

| Método | Bits | Bytes/vetor | Compressão | Recall@10 | MSE |
|---|---|---|---|---|---|
| float32 baseline | 32 | 1536 | 1× | 0.935 | 0 |
| float16 | 16 | 768 | 2× | 0.935 | ~0 |
| Uniforme | 4 | 192 | 8× | 0.860 | alto |
| Uniforme | 2 | 96 | 16× | **0.200** | catastrófico |
| Lloyd-Max | 4 | 192 | 8× | 0.905 | médio |
| **TurboQuantMSE** | **4** | **192** | **7.9×** | **0.925** | **11× menor que Lloyd puro** |
| **TurboQuantMSE** | **2** | **96** | **15.7×** | **0.925** | mínimo |

**Observação crítica:** Uniform 2-bit destrói o sistema (0.200 recall). TurboQuantMSE 2-bit
mantém 0.925. A diferença é **apenas** a rotação. Isso é o poder da álgebra linear.

---

## 3. Mapeamento Python → Rust

### 3.1 Código-fonte analisado (5 módulos)

```
src/quantization/
├── rotation.py         → core/src/turboquant.rs::rotation_matrix()
├── lloyd_max.py        → core/src/turboquant.rs::lloyd_max_codebook()
├── turboquant_mse.py   → core/src/turboquant.rs::quantize() / dequantize()
├── turboquant_prod.py  → FASE 2 (QJL bias correction)
└── storage.py          → core/src/turboquant.rs::pack_bits() / unpack_bits()
```

### 3.2 Tradução Função por Função

#### `rotation.py::fit_rotation(dim, seed)` → Rust

```python
# Python (3 linhas core)
rng = np.random.default_rng(seed)
G = rng.standard_normal((dim, dim)).astype(np.float64)
Q, _ = np.linalg.qr(G)
```

```rust
// Rust (~10 linhas com ndarray + rand)
use ndarray::{Array2};
use ndarray_linalg::QR;
use rand::SeedableRng;
use rand_distr::{StandardNormal, Distribution};

fn fit_rotation(dim: usize, seed: u64) -> Array2<f32> {
    let mut rng = rand_chacha::ChaCha8Rng::seed_from_u64(seed);
    let g: Array2<f64> = Array2::from_shape_fn((dim, dim), |_| {
        StandardNormal.sample(&mut rng)
    });
    let (q, _) = g.qr().unwrap();
    q.mapv(|x| x as f32)
}
```

**Dependências Rust:** `ndarray`, `ndarray-linalg` (backend LAPACK/OpenBLAS), `rand`, `rand_chacha`

#### `lloyd_max.py::lloyd_max_codebook(dim, bits)` → Rust

```python
# Python (core loop ~30 linhas)
xs = np.linspace(-1.0 + 1e-9, 1.0 - 1e-9, num_grid)
pdf = coord_pdf(xs, dim)  # Beta((d-1)/2, (d-1)/2) escalada
centroids = init_from_quantiles(xs, pdf, K)
for _ in range(300):
    midpoints = (centroids[:-1] + centroids[1:]) / 2.0
    bucket_idx = np.searchsorted(midpoints, xs)
    denom = np.bincount(bucket_idx, weights=pdf, minlength=K)
    numer = np.bincount(bucket_idx, weights=pdf * xs, minlength=K)
    centroids[mask] = numer[mask] / denom[mask]
```

```rust
// Rust equivalente (~40 linhas)
use statrs::distribution::Beta;

fn lloyd_max_codebook(dim: usize, bits: u8) -> Vec<f32> {
    let k = 1usize << bits;
    let num_grid = 500_000;
    let alpha = (dim as f64 - 1.0) / 2.0;
    let beta_dist = Beta::new(alpha, alpha).unwrap();

    let xs: Vec<f64> = (0..num_grid)
        .map(|i| -1.0 + 1e-9 + (2.0 - 2e-9) * i as f64 / (num_grid - 1) as f64)
        .collect();

    let pdf: Vec<f64> = xs.iter()
        .map(|&t| {
            let u = (t + 1.0) / 2.0;
            beta_dist.pdf(u) / 2.0
        })
        .collect();

    // Inicializar centróides por quantis...
    // Lloyd-Max loop (300 iterações)...
    // searchsorted via partition_point()...
    // bincount via HashMap ou vec acumulador...
    
    centroids.iter().map(|&c| c as f32).collect()
}
```

**Dependências Rust:** `statrs` (distribuição Beta), ou cálculo analítico direto da PDF.

**OTIMIZAÇÃO:** O codebook é calculado UMA VEZ por (dim, bits) e cacheado como `const`.
Para dim=384, bits=4: são 16 centróides × f32 = **64 bytes**. Pode ser hardcoded via `lazy_static!`.

#### `turboquant_mse.py::quantize_mse_batch()` → Rust

```python
# Python (3 linhas)
Y = X @ R.T                           # Rotação
indices = quantize_lloyd(Y, codebook)  # searchsorted
return indices
```

```rust
// Rust (6 linhas, nativamente SIMD-friendly)
fn quantize(embeddings: &Array2<f32>, state: &TurboState) -> Array2<u8> {
    let rotated = embeddings.dot(&state.rotation.t());  // matmul
    let midpoints = compute_midpoints(&state.codebook);
    rotated.mapv(|v| {
        midpoints.partition_point(|&m| m < v) as u8      // searchsorted
    })
}
```

#### `storage.py::pack_indices()` → Rust

```python
# Python (numpy bit manipulation)
powers = np.int32(1) << np.arange(bits-1, -1, -1)
bit_array = ((indices & powers) > 0).astype(np.uint8)
packed = np.packbits(bit_array)
```

```rust
// Rust (zero-cost bit manipulation)
fn pack_4bit(indices: &[u8]) -> Vec<u8> {
    indices.chunks(2)
        .map(|pair| (pair[0] << 4) | pair.get(1).copied().unwrap_or(0))
        .collect()
}

fn unpack_4bit(packed: &[u8], dim: usize) -> Vec<u8> {
    let mut out = Vec::with_capacity(dim);
    for &byte in packed {
        out.push(byte >> 4);
        out.push(byte & 0x0F);
    }
    out.truncate(dim);
    out
}
```

**Em Rust, bit-packing é TRIVIAL** — sem overhead de numpy, sem GIL, inline SIMD natural.

---

## 4. Arquitetura WAG Efêmera — O Encaixe Perfeito

### 4.0 O que já existe (e por que TurboQuant encaixa como luva)

O Sovereign JÁ possui uma infraestrutura completa de **WAG (Web-Augmented Generation)**
com memória efêmera temporizada. Esta arquitetura foi projetada EXATAMENTE para o caso
de uso onde TurboQuant tem máximo impacto:

```
┌─ SCHEMA ATUAL (002_ephemeral_knowledge.sql) ──────────────────┐
│                                                                │
│  ephemeral_knowledge                                           │
│  ├── id TEXT PRIMARY KEY                                       │
│  ├── source_url TEXT                                           │
│  ├── domain TEXT                                               │
│  ├── expires_at DATETIME  ← EXPIRA EM 30 DIAS                │
│  ├── content_raw TEXT                                          │
│  └── FK → ephemeral_chunks (ON DELETE CASCADE)                │
│                                                                │
│  ephemeral_chunks                                              │
│  ├── id INTEGER PRIMARY KEY                                    │
│  ├── text_content TEXT                                          │
│  ├── chunk_index INTEGER                                       │
│  └── FK → vec_ephemeral_chunks                                │
│                                                                │
│  vec_ephemeral_chunks (sqlite-vec, VIRTUAL TABLE vec0)        │
│  ├── chunk_id INTEGER PRIMARY KEY                              │
│  └── embedding float[1024]  ← 1024 dims × 4 bytes = 4096 B  │
│                                                                │
│  garbage_collector.rs (roda a cada 1h)                         │
│  └── DELETE WHERE expires_at < CURRENT_TIMESTAMP              │
│      └── CASCADE → chunks → vec_ephemeral desorfanados        │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Ciclo de vida de um embedding WAG:**
```
Scrape Web → Ollama (nomic-embed-text) → float[1024] → SQLite BLOB
                                                           │
                                                    4096 bytes/chunk
                                                    × 50 chunks/doc
                                                    = 200 KB/documento
                                                           │
                                              30 dias depois → EXPURGADO
                                              pelo Garbage Collector
```

### 4.0.1 Por que WAG efêmero é o cenário IDEAL para TurboQuant

A natureza efêmera cria um **fluxo contínuo de write+delete** onde o custo por byte
se multiplica ao longo do tempo:

| Métrica | float32 (hoje) | TurboQuant 4-bit | Economia |
|---|---|---|---|
| Bytes/chunk | 4096 | 514 | **7.9×** |
| Bytes/documento (50 chunks) | 200 KB | 25 KB | **175 KB/doc** |
| 10 pesquisas/dia × 5 docs/pesquisa × 30 dias | **300 MB** | **38 MB** | **262 MB** |
| Em 1 ano (rotação contínua) | **3.6 GB write throughput** | **456 MB** | **3.1 GB menos I/O** |

**Insight crítico:** Como os embeddings são EFÊMEROS (30 dias), o Sovereign não precisa
migrar dados antigos. Basta ativar TurboQuant — novos embeddings entram comprimidos,
antigos expiram naturalmente. **Zero migração, zero downtime.**

### 4.0.2 Impacto Cognitivo (a pergunta real)

A pergunta "melhoraremos performance cognitiva?" tem uma resposta direta nesta arquitetura:

```
HOJE: 10 pesquisas/dia × 5 docs × 50 chunks = 2.500 embeddings ativos
      × 4096 bytes = ~10 MB de vetores na vec0

      Com 27 GB de RAM e ~16 GB de modelos:
      Espaço para embeddings: ~500 MB → suporta ~125K chunks

COM TURBOQUANT:
      Mesmos 2.500 embeddings = ~1.3 MB  (em vez de 10 MB)
      Espaço para embeddings: ~500 MB → suporta ~1M chunks

      = 8× MAIS contexto semântico para o LLM
      = Recall mais rico quando o Mestre busca fontes
      = MENOS alucinação (mais fatos disponíveis para RAG)
```

**Em termos cognitivos:**
1. O Mestre faz tool-calling → `dispatch_sub_researcher` → scrape web
2. Resultados são embeddados e armazenados na `vec_ephemeral_chunks`
3. Em pesquisas FUTURAS (dentro de 30 dias), o Mestre pode **resgatar fatos anteriores** via busca semântica
4. Com TurboQuant, o Vault comporta **8× mais fatos** → probabilidade de resgatar contexto relevante **aumenta proporcionalmente**

> **Veredicto cognitivo:** TurboQuant não melhora a capacidade de raciocínio do LLM,
> mas melhora dramaticamente a **qualidade do input que ele recebe**.
> É como dar a um analista financeiro acesso a 8× mais relatórios —
> ele não fica mais inteligente, mas suas conclusões ficam mais fundamentadas.

### 4.0.3 Dimensionalidade Real: 1024, não 768

**Observação importante:** O schema usa `float[1024]`, não `float[768]`.
O `nomic-embed-text` gera vetores de **768 dimensões**, mas a declaração `vec0`
reserva `float[1024]`. Isso significa:

- **Hoje:** 1024 × 4 = **4096 bytes/chunk** (256 bytes desperdiçados se dim=768)
- **Com TQ 4-bit:** 768 × 4/8 = **384 bytes** (pack real) + 2 bytes norm = **386 bytes**
- **Compressão real:** 4096 → 386 = **10.6×** (melhor que os 7.9× teóricos!)

A migração deve corrigir a dimensionalidade para `float[768]` ou manter `float[1024]`
com padding zero — decisão a ser tomada na Fase 2.

---

### 4.1 Ponto de Inserção (api_trainer.rs:337-358)

```rust
// HOJE: Embedding float32 bruto → SQLite vec0 BLOB
let emb_req = json!({"model": "nomic-embed-text", "prompt": ch});
let embedding = emb_json.get("embedding"); // Vec<f64> do Ollama
let floats_bytes: Vec<u8> = embedding.iter()
    .filter_map(|v| v.as_f64().map(|f| f as f32))
    .flat_map(|f| f.to_ne_bytes())
    .collect();
// → 1024 dims × 4 bytes = 4096 bytes/chunk (com padding) no SQLite
sqlx::query("INSERT INTO vec_ephemeral_chunks (chunk_id, embedding) VALUES (?, ?)")
    .bind(floats_bytes)  // BLOB de 4096 bytes
```

### 4.2 Estado Futuro (com TurboQuant)

```rust
// COM TURBOQUANT: Embedding → Rotação → Lloyd-Max → Pack → SQLite
let raw_embedding: Vec<f32> = embedding.iter()
    .filter_map(|v| v.as_f64().map(|f| f as f32))
    .collect();

let (packed, norm) = turboquant::quantize_single(&raw_embedding, &TURBO_STATE);
// → packed: 384 bytes (4-bit, dim=768) + norm: 2 bytes = 386 bytes/chunk
// → COMPRESSÃO REAL: 4096 → 386 = 10.6×

sqlx::query("INSERT INTO vec_ephemeral_chunks (chunk_id, embedding, norm) VALUES (?, ?, ?)")
    .bind(packed)    // BLOB comprimido
    .bind(norm)      // f16 (2 bytes)
```

### 4.3 Garbage Collector — Zero Migração

```rust
// garbage_collector.rs NÃO PRECISA MUDAR!
// O expurgo por CASCADE funciona idêntico — apaga o parent,
// chunks e vetores são destruídos automaticamente.
// Novos embeddings entram comprimidos, antigos expiram naturalmente.
// Em 30 dias, 100% do Vault já é TurboQuant sem migração forçada.
```

### 4.4 Busca (Dequantize + Cosseno)

```rust
// No momento da busca semântica:
fn search_similar(query_emb: &[f32], pool: &SqlitePool, top_k: usize) -> Vec<(i64, f32)> {
    let (query_packed, query_norm) = turboquant::quantize_single(query_emb, &TURBO_STATE);
    
    // Opção A: Dequantizar e comparar em float32 (simples, correto)
    let query_recon = turboquant::dequantize(&query_packed, query_norm, &TURBO_STATE);
    // dot product com cada documento desquantizado...

    // Opção B: Comparar diretamente nos índices (mais rápido, aproximado)
    // Lookup table de distâncias: codebook[i] × codebook[j] pré-computada (16×16)

    // Opção C: vec0 nativo — se o sqlite-vec suportar custom distance functions,
    // podemos armazenar os índices quantizados diretamente e usar vec0 para ANN search
}
```

---

## 5. Impacto no Hardware (27GB Ryzen)

### 5.1 Orçamento de Memória

```
HOJE (v1.2.4):
  Modelos LLM:       ~16 GB (qwen3:8b + gemma4:e4b + nomic-embed-text)
  SQLite + Vault:     ~500 MB
  Embeddings RAG:     depende do corpus (float32)
  Disponível:         ~10.5 GB

COM TURBOQUANT (v1.3.0):
  Modelos LLM:        ~16 GB (mesmo)
  SQLite + Vault:      ~500 MB
  Embeddings RAG:      7.9× MENOR
  Disponível:          ~10.5 GB + economia de embeddings
```

### 5.2 Projeção por Escala

| Corpus | float32 | TurboQuant 4-bit | Economia |
|---|---|---|---|
| 1K chunks (dim=768) | 3 MB | 384 KB | 2.6 MB |
| 10K chunks | 30 MB | 3.8 MB | 26 MB |
| 100K chunks | 300 MB | 38 MB | **262 MB** |
| 1M chunks | **3 GB** | **384 MB** | **2.6 GB** |

Para 1M chunks, economizamos **2.6 GB** — quase o equivalente a um modelo inteiro de 3B.

### 5.3 Conexão com Exo Labs (Inferência Distribuída)

Se no futuro o Sovereign operar em modo distribuído (Ryzen Local ↔ Oracle Cloud),
o TurboQuant comprime o tráfego de **sincronização de embeddings** entre nodes em 8×.

Hoje, sincronizar 100K chunks entre local e cloud = 300 MB via rede.
Com TurboQuant = **38 MB**. Em link de 10 Mbps, a diferença é 4 minutos vs 30 segundos.

---

## 6. Plano de Implementação (3 Fases)

### Fase 1: PoC Nativo (2-3 dias)

**Objetivo:** `core/src/turboquant.rs` funcional com benchmark vs numpy

```
1. Implementar fit_rotation() com ndarray-linalg (QR decomposition)
2. Implementar lloyd_max_codebook() com statrs (Beta distribution)
3. Implementar quantize/dequantize single vector
4. Implementar pack_4bit/unpack_4bit
5. Benchmark: gerar 10K embeddings aleatórios dim=768, comparar:
   - Tempo quantize/dequantize (Rust vs Python)
   - MSE da reconstrução
   - Tamanho em disco
```

**Cargo.toml adições:**
```toml
ndarray = "0.16"
ndarray-linalg = { version = "0.17", features = ["openblas-static"] }
rand = "0.8"
rand_chacha = "0.3"
rand_distr = "0.4"
statrs = "0.17"
```

### Fase 2: Integração com Vault RAG (1-2 dias)

```
1. Modificar api_trainer.rs: interceptar embeddings do Ollama pós-geração
2. Adicionar coluna `norm` na tabela vec_ephemeral_chunks
3. Quantizar antes de INSERT, dequantizar no SELECT para busca
4. Migração SQLite: ALTER TABLE + upgrade de dados existentes
5. Benchmark end-to-end: Recall@10 com queries reais vs float32
```

### Fase 3: Otimização SIMD + Codebook Pré-computado (1 dia)

```
1. Pré-computar codebook para (dim=768, bits=4) e hardcodar como const
   → Elimina scipy/statrs do runtime — apenas 16 floats
2. SIMD pack/unpack via std::arch (AVX2 se disponível)
3. Lazy rotation matrix via lazy_static! com seed fixo
4. Busca por dot product diretamente no espaço quantizado
   → Lookup table de distâncias entre centróides (16×16 = 256 entradas)
```

---

## 7. Riscos e Mitigações

| Risco | Probabilidade | Mitigação |
|---|---|---|
| `ndarray-linalg` com LAPACK falha na compilação | Média | Usar `nalgebra` como alternativa (pure Rust, sem deps externas) |
| Codebook Lloyd-Max diverge para dim muito alta | Baixa | Pré-computar offline e hardcodar; já validado para dim=384 |
| Recall degrada com embeddings do Ollama (nomic-embed-text) vs BAAI/bge | Baixa | Os embeddings são sempre normalizados — TurboQuant é model-agnostic |
| QR decomposition lenta para dim=768 (768² = 590K floats) | Média | Executar UMA VEZ no startup e cachear; ou usar Hadamard+diag |
| SQLite BLOB mismatch na migração | Baixa | Migração com fallback: tentar ler como TQ, se falhar, assumir float32 |

---

## 8. Critério de Sucesso

| Métrica | Meta | Validação |
|---|---|---|
| Compressão de memória | ≥ 7× vs float32 | `sizeof(packed_blob) / sizeof(float32_blob)` |
| Recall@10 degradation | ≤ 2 pp | Benchmark com queries do Vault existente |
| Latência de quantize (single) | < 1ms | `Instant::now()` em loop de 10K vetores |
| Latência de dequantize+search | < 5ms para 10K docs | Benchmark end-to-end |
| Tempo de compilação `cargo build` | Sem regressão >10s | CI check |

---

## 9. Referências

- **Paper original:** [arxiv.org/abs/2504.19874](https://arxiv.org/abs/2504.19874) — Google Research (2025)
- **Implementação Python:** [github.com/marcos2872/rag-embedding-compression-lab](https://github.com/marcos2872/rag-embedding-compression-lab)
- **Crates Rust:**
  - [`ndarray`](https://crates.io/crates/ndarray) — N-dimensional arrays
  - [`ndarray-linalg`](https://crates.io/crates/ndarray-linalg) — QR, SVD, etc  
  - [`nalgebra`](https://crates.io/crates/nalgebra) — Alternativa pure-Rust
  - [`statrs`](https://crates.io/crates/statrs) — Distribuição Beta para PDF
  - [`rand_chacha`](https://crates.io/crates/rand_chacha) — PRNG determinístico
- **Exo Labs:** [exolabs.net](https://exolabs.net/) — Distributed inference framework
- **Artigo TabNews:** [TurboQuant: 7,9× Menos RAM em Embeddings](https://www.tabnews.com.br/MarcosBritoDev/eu-descobri-que-50-linhas-de-codigo-fazem-mais-diferenca-do-que-300-iteracoes-de-otimizacao)
- **Insight complementar:** [LLM em processador de 1997](https://br.ign.com/tech/152134/news/alguem-realizou-um-experimento-com-um-processador-de-1997)

---

## 10. Código-Fonte de Referência Analisado

Os 5 módulos Python abaixo foram lidos linha por linha e mapeados para equivalentes Rust.
Os arquivos originais estão em `src/quantization/` do repositório de referência.

### `turboquant_mse.py` — 50 linhas (core do algoritmo)

```python
# O algoritmo INTEIRO em 3 funções:
def fit_turbo_mse(dim, bits, seed):
    R        = fit_rotation(dim, seed)      # QR(Normal(d,d))
    codebook = get_codebook(dim, bits)      # Lloyd-Max offline
    return TurboMSEState(R, codebook, dim, bits, seed)

def quantize_mse_batch(X, state):
    Y       = apply_rotation(X, state.R)    # Y = X @ R.T
    indices = quantize_lloyd(Y, codebook)   # searchsorted
    return indices

def dequantize_mse_batch(indices, norms, state):
    Y_hat = dequantize_lloyd(indices, codebook)  # lookup
    X_hat = apply_inverse_rotation(Y_hat, R)     # Y @ R
    return X_hat * norms
```

### `rotation.py` — 20 linhas

```python
def fit_rotation(dim, seed):
    G = rng.standard_normal((dim, dim))
    Q, _ = np.linalg.qr(G)                 # Haar measure
    return Q

def apply_rotation(X, R):
    return X @ R.T                          # Batch matmul

def apply_inverse_rotation(Y, R):
    return Y @ R                            # R ortogonal → inv = transpose
```

### `lloyd_max.py` — 90 linhas (computação mais pesada, roda offline)

```python
# PDF da coordenada em S^(d-1): Beta((d-1)/2, (d-1)/2)
# Lloyd-Max: Partition (midpoints) + Reconstruction (E[X|bucket])
# searchsorted + bincount = O(N*log(K)) por iteração
# Converge em 50-100 iterações tipicamente
```

### `storage.py` — 60 linhas (pack/unpack bit-level)

```python
# pack_indices: cada índice vira b bits, empacota com np.packbits
# unpack_indices: reverso exato
# pack_signs: +1/-1 → 1/0 → packbits (para QJL do TurboProd)
```

---

> **Veredicto:** O algoritmo é elegante, matematicamente sólido, e **trivial de portar
> para Rust**. As operações core (matmul, searchsorted, bitwise) são exatamente o tipo
> de coisa que Rust faz melhor que Python. A rotação ortogonal é a sacada genial —
> transforma um problema intratável (quantização ótima multidimensional) em um problema
> resolvido (quantização escalar independente por coordenada).
>
> **Estimativa de implementação: ~200 linhas de Rust para o core funcional.**
