# 🧠 Estratégia de Modelos & Destilação de Conhecimento

Este documento define o manifesto de modelos recomendados, as capacidades exigidas e as técnicas de transferência de conhecimento (Distillation) entre modelos de diferentes tiers.

---

## 1. Manifesto de Modelos (Registry)

O sistema utiliza um registro dinâmico para mapear capacidades e disparar as ferramentas corretas (Tool Calling).

### 1.1 Modelos Recomendados por Tier
| Tier | Modelo | Parâmetros | Uso Principal |
|---|---|---|---|
| **Estagiário** | `qwen2.5:0.5b` | 500M | Autocomplete, saudações e tarefas triviais. |
| **Júnior** | `qwen2.5:7b` | 7B | Chat diário, RAG simples e extração de fatos. |
| **Sênior** | `llama3.1:8b` | 8B | Deep Research, codificação e lógica complexa. |
| **Especialista** | `llama3.3:70b` | 70B | Auditoria final, análise financeira e decisões críticas. |

---

## 2. Destilação de Conhecimento (Knowledge Distillation)

O Sovereign Pair utiliza o paradigma **Professor (Cloud/Massive LLM) -> Estudante (Local/Small LLM)** para transferir inteligência.

- **Processo**: O modelo "Professor" gera cadeias de raciocínio (Reasoning Chains) sobre um dataset complexo no Vault.
- **Treinamento**: O modelo "Estudante" é ajustado (Fine-Tuning/LoRA) para replicar os resultados do Professor em uma fração do custo computacional e latência.
- **Métrica de Sucesso**: Monitoramos a **Similarity Matrix** entre Aluno e Mestre para atestar a maturação sináptica.

---

## 3. Tool-Calling & Decodificação JSON

Para que a orquestração agêntica funcione, o modelo deve suportar nativamente a exportação de intenções em formato JSON.

- **Fallback Purificador**: Se um modelo falhar na geração de ferramentas, o motor Rust (`api.rs`) intercepta a falha, remove as ferramentas da payload e permite que o modelo responda em prosa, protegendo a integridade do servidor.
