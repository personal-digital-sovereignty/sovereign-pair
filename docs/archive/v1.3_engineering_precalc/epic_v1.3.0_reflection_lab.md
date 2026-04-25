# Épico (v1.3.0): O Despertar do Sovereign Reflection Lab 

**Status:** Desenhado / Aguardando Ciclo v1.3.0
**Módulo Raiz:** `Sovereign Core` (Rust) e `Model Trainer` (Svelte 5)
**Objetivo Principal:** Materializar o laboratório cenográfico em uma pipeline real e mecânica de Auditoria de *Chain of Thought* (CoT) com métricas persistentes, simulação ao vivo via SSE, e Injeção de Dataset Fino no SQLite.

---

## 1. Visão Geral da Funcionalidade

A aba do **Reflection Lab** deixará de ser uma Mock UI para se transformar no mais avançado **Depurador Lógico de LLMs** da central Cíbrida. Seu propósito é expor, interpelar e otimizar os caminhos neurais intrínsecos que uma IA local adota para chegar a uma conclusão (Raciocínio Latente), penalizando raciocínios cegos e pontuando "Self-Corrections" (Auto-Correções).

---

## 2. Tarefas e Entregáveis (Backlog Architecture)

### Milestone A: Persistência e IPC (Rust + SQLite)
As alavancas e configurações que o Engenheiro mexe na UI não podem evaporar. Elas representam diretrizes que moldarão o motor.
1. **Schema de Banco de Dados (`001_sensus_init.sql`)**:
   - Injetar propriedade `reflection_settings` (`value_json`) na tabela global `global_settings`.
   - Adicionar tabela nova `reflection_datasets` `(id UUID, model_tag TEXT, payload_json TEXT, created_at DATETIME)`.
2. **APIs Axum (CRUD)**:
   - Rota `POST /v1/engineer/reflection/apply`: Uma API para salvar o JSON formatado no Workspace Local para uso posterior.
   - Rota `POST /v1/engineer/reflection/settings`: API para cravar no SQLite as preferências de "Reasoning Depth" e "Audit Intensity".

### Milestone B: O Motor de Auditoria CoT (The Sentinel)
A telemetria de auditoria da Mente Mestra.
1. **The Think-Before-Response Trigger**:
   - O Rust precisará injetar uma sub-rotina (`<think> ... </think>`) no Payload do Ollama ou forçar uma flag `response_format` onde a IA é obrigada a passar por 2 camadas de output: "Critique" e "Synthesis".
2. **Lógica Comparativa em Tempo Real (Ollama API)**:
   - Criaremos o método `trigger_reflection_pipeline()` no `core/src/api_trainer.rs`.
   - Em vez de gerar 1 resposta, o backend chamará o Mestre. Depois, chamará o "*Audit Agent*" para ler o "thought" original e atribuir um `confidence_score`.

### Milestone C: Integração SSE (A Quebra do Labirinto Mock)
A tela possui uma "Live Stream" com animações incríveis, que pedem por um *Streamed Server-Sent Events* em vez de Arrays de `Math.random()`.
1. **Event Hook (`TRAINER_LOGS`)**:
   - Ampliar o canal broadcast do Rust para enviar payloads tipados em JSON, contendo métricas `Event { type: "correction", msg: "Identificado viés..." }`.
   - A Interface (EventSource Javascript) parseará o JSON assíncrono e pichará na cor verde/azul de acordo com a premissa de *Self-Correction* e cadência processual do Backend de verdade.

### Milestone D: Retroalimentação do Sensus (Telemetry Real)
Métricas Reais na tela.
1. O backend deverá contabilizar em Memória Cache quantas inferências caíram no `catch` de Alucinação e qual a profundidade dos laços (Loops).
2. Devolver no Dashboard do Hub os cálculos matemáticos para as seções "Reasoning Chain [Stable]" e "Self-Correct Ratio []".

---

## 3. Desfio de Engenharia Crítico (Blindspot Warning)

> [!WARNING]
> Modelos menores (Slm's < 5B) **falham estruturalmente** em aderir ao Chain-of-Thought focado. Se não colocarmos uma "Trava de Modelos Habilitados a Refletir" na aba do Reflection Lab (exigindo modelos da linha Qwen 2.5 `math` ou `reasoner`), a UI entrará em colapso retornando falsos-positivos na validação de auditoria, porque os modelos menores vomitarão prosa livre ignorando o schema forçado. O Lab precisará, portanto, interrogar a *Operations Matrix* pelo metadado `m.is_reasoner` antes de destravar o botão `Launch Simulation`.

---

## 4. Próxima Ação quando for iniciar (1.3.0)
Quando o v1.3.0 for declarado, o trabalho começará quebrando o `trainer.svelte.ts`, limpando o loop iterativo randômico, conectando-o ao EventSource da porta P2P da Engine, e traçando a modelagem do SQLite em `db.rs`!
