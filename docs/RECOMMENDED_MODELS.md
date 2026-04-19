# Sovereign Engine: Local Models Guide (v1.2.4)

O Sovereign Pair V1.2.4 exige um esquema de "Hardware-Model Matching" altamente otimizado para evitar *OOM (Out-of-Memory)* e garantir inferência local em tempo hábil. Mantenha em seu disco OLLAMA apenas as ferramentas cognitivas essenciais da nossa *Elite Pipeline*.

---

## 1. A Elite Pipeline (Configuração Sênior)
**Recomendado para:** Workstations (Nvidia RTX 3060+) ou Desktops/M-Series com 32GB+ RAM.

A topologia ideal isola responsabilidades para erradicar sobreposição arquitetural e latência.

*   🧠 **`qwen3:8b` (Master / Scribe):** O Assistente principal. Opera com *No-Think Bypass* ativado para extração ultrarrápida de Tools, retornando ao Modo Híbrido apenas no ciclo de Síntese Final em Markdown.
*   ⚖️ **`phi4-mini:latest` (Auditor Primário — TIER 1):** Modelo Microsoft 3.8B ultra-literal e factual. Especialista no *Sycophancy Breaker* (quebra de viés confirmatório). Extremamente rápido (~2.5GB VRAM), cross-family a todos os demais.
*   👁️ **`gemma4:e4b` (Recepcionista Multimodal / Auditor Reserva):** Modelo compacto Sub-5B para triagem rápida, leitura de imagens e backup do Scribe. Atua como Auditor TIER-2 quando o Master é qwen.
*   🔍 **`gemma3:12b` (Specialist / Heavy RAG):** Modelo largo para análises complexas multi-documento e recuperação de informação massiva. Acionado via tier `specialist` (>9.5B).
*   ⛓️ **`bge-m3:latest` & `nomic-embed-text:latest`:** Motores vetoriais essenciais do nosso Knowledge Hub. Nunca devem ser apagados.

### Topologia de Auditoria (Sycophancy Breaker v1.2.4+)

```
Master (qwen3:8b) → Auditor: phi4-mini (cross-family Microsoft)
Scribe (qwen3:8b) → Auditor: phi4-mini (TIER 1) ou gemma4:e4b (TIER 2)
Scribe Resgate (gemma4:e4b) → Auditor SWAP: qwen3:8b (evita self-audit)
```

> **Co-Residency (27GB+):** Durante o pipeline Scribe↔Auditor, ambos os modelos permanecem carregados na VRAM simultaneamente. Isso elimina ~8min de cold-start por swap VRAM.

---

## 2. Configuração de Baixa Borda (Hardwares com 16GB-20GB RAM)
**Recomendado para:** Notebooks APU (Ryzen 7, i7) de gráficos integrados e uso diário isolado.

Para impedir o *Swap Freezing* (paginação no SSD forçada), extirpe do banco todas as IAs entre 12B e 14B+ (Ex: Phi-4, Gemma 3 12b). O ecossistema roda limpo com:

*   **Ponto Focal Absoluto:** `qwen3:8b`. Resoluto o suficiente para encapsular o Multi-Agent reasoning e o Output diário do RAG sem fundir a VRAM reservada do sistema operacional.
*   **Apoio Tático Visual:** `gemma4:e4b`. 
*   **Auditor:** `phi4-mini:latest` (3.8B — cabe em qualquer hardware).

---

## 3. Matriz de Guardrails Sub-5B (O Fallback Essencial)
O *Sovereign Core* implementa funções SQL ativas ("Thought Nanny") projetadas para ejetar agentes do pool caso emitam saídas textuais rompendo esquemas estruturais JSON. 

* **⚠️ A Regra do Gatekeeper Reserva:** 
Apesar da limpeza de disco, **nunca apague 100% dos modelos abaixo de 5 Bilhões de parâmetros**. 
Você deve manter o `llama3.2:3b` ou o `nous-hermes3:3b` instalados silenciamente na sua máquina. Eles atuam como **backup nativo**. Se no meio da noite a recepção de Extração (`gemma4:e4b`) falhar os testes lógicos estruturais de loop, a *Dynamic Agentic Fallback* varrerá o banco procurando o reserva Imediato mais leve sem causar pânico ao Backend.

---

## 4. Modelos Obsoletos (Remover do Ollama)

| Modelo | Motivo |
|---|---|
| `mistral-nemo:12b` | Nunca é eleito por nenhum scanner automático. Consome ~7.4GB de disco sem uso. |
| `deepseek-r1:7b` | Reasoner lento (thinking overhead). Para chat, use qwen3:8b. |
| `qwen2.5:7b` | Geração anterior. Substituído por qwen3:8b em todas as funções. |
