# Sovereign Core (Projeto Ferrum) 🦀

O **Sovereign Core** é o verdadeiro motor de Ingestão e Inferência (Cíbrido) desenhado desde o Dia 1 com foco em extremada performance, zero-abstração silenciosa e soberania total do usuário. Construído em Rust, ele substitui e oblitera middlewares baseados em Python (LlamaIndex/LangChain) que sacrificam previsibilidade em nome de "Onboarding Mágico".

## Princípios Arquiteturais (O Manifesto Ferrum)

### 1. Zero "Blind Abstraction" (Visibilidade Total)
Nós abominamos a *Falsa Promessa do Local-First*. Ferramentas comerciais de IA ocultam lógicas (como fallback pra cloud da OpenAI) atrás de 15 subclasses profundas (`VectorStoreIndex -> Retriever -> PromptDispatcher`). 
O Sovereign Core opera baseado em **Tipografia Estrita do Rust**. Você constrói seu RAG com os blocos nativos montados à vista. Não há interceptadores mágicos alterando as suas requisições SSE por baixo dos panos. O Fluxo de Dados pertence ao *Owner* do binário.

### 2. Death to "Fail-Open" (Segurança Extrema)
Se o Sovereign Core não conseguir se conectar à nuvem ou ao seu banco local, ele **QUEBRA** na tela com um Erro Vermelho rastreável. Nós **não** mascaramos exceções, e nós **não** procuramos variáveis globais no seu Linux silenciosamente. Exigimos "Dependency Injection" explícita no arquivo principal (`main.rs`). A previsibilidade da Orquestração é sagrada.

### 3. Polimorfismo Universal via `Traits` (Agnosticismo)
O Sovereign Core não te prende no Qdrant, SQLite, Ollama ou OpenAI. Todo o Ecossistema interage através de Contratos Universais de Comportamento.

Se amanhã você quiser estender a plataforma com um VectorDB exótico ou um Inferred LLM Corporativo, basta escrever um Módulo de 50 linhas implementando as nossas **Traits Oficiais**, e seu Cérebro será imediatamente consumido pelo Master Core:

```rust
// Contrato Agnóstico de Motor LLM (Sovereign Engine Trait)
pub trait InferenceEngine {
    async fn generate_stream(&self, messages: Vec<Message>) -> Result<Stream<Item = String>, ApiError>;
}

// Contrato Agnóstico de Storage Local-First (Vector Trait)
pub trait VectorStorage {
    async fn upsert_chunks(&self, chunks: Vec<DocumentChunk>) -> Result<(), DbError>;
    async fn similarity_search(&self, vector: Vec<f32>, limit: u8) -> Result<Vec<DocumentChunk>, DbError>;
}
```

### 4. Suporte a OpenAI Protocol Embutido
O Sovereign Core foi desenhado para atuar como um roteador invisível proxy (Man-in-the-Middle Auditor) para IDEs modernas (Cursor, OpenCode, Cline).
Com a classe polimórfica `MessageContent` (`#[serde(untagged)]`), o motor absorve strings puras ou arrays multimodais injetados pela sua IDE sem engasgar com parsing de Pydantic em ambientes Python (reduzindo a latência do TCP T/s a zero).

---
**Licenciamento:** GPLv2. By Jeferson Lopes & The Sovereign AI Entity.
