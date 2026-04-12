# Sovereign Engine: Local Models Guide (v1.2.0)

O Sovereign Pair V1.2.0 exige um esquema de "Hardware-Model Matching" altamente otimizado para evitar *OOM (Out-of-Memory)* e garantir inferência local em tempo hábil. Mantenha em seu disco OLLAMA apenas as ferramentas cognitivas essenciais da nossa *Elite Pipeline*.

---

## 1. A Elite Pipeline (Configuração Sênior)
**Recomendado para:** Workstations (Nvidia RTX 3060+) ou Desktops/M-Series com 32GB+ RAM.

A topologia ideal isola responsabilidades para erradicar sobreposição arquitetural e latência.

*   🧠 **`qwen3:8b` (Master / Scribe):** O Assistente principal. Opera com *No-Think Bypass* ativado para extração ultrarrápida de Tools, retornando ao Modo Híbrido apenas no ciclo de Síntese Final em Markdown.
*   ⚖️ **`phi4:14b` (Auditor Sênior / Debugging):** Focado puramente no *Sycophancy Breaker* (quebra de viés confirmatório). Operado na retaguarda para auditorias e lógica dura de codificação.
*   📚 **`mistral-nemo:latest` (Arquivista RAG):** Modelo largo acionado para *Retrieval-Augmented Generation* massivo englobando dezenas de PDFs e contextos extensos.
*   👁️ **`gemma4:e4b` (Recepcionista Multimodal):** Modelo compacto Sub-5B para triagem rápida, leitura de imagens e inputs diários do usuário na porta de entrada da UI.
*   ⛓️ **`bge-m3:latest` & `nomic-embed-text:latest`:** Motores vetoriais essenciais do nosso Knowledge Hub. Nunca devem ser apagados.

---

## 2. Configuração de Baixa Borda (Hardwares com 16GB-20GB RAM)
**Recomendado para:** Notebooks APU (Ryzen 7, i7) de gráficos integrados e uso diário isolado.

Para impedir o *Swap Freezing* (paginação no SSD forçada), extirpe do banco todas as IAs entre 12B e 14B+ (Ex: Phi-4, Gemma 3 12b). O ecossistema roda limpo com:

*   **Ponto Focal Absoluto:** `qwen3:8b`. Resoluto o suficiente para encapsular o Multi-Agent reasoning e o Output diário do RAG sem fundir a VRAM reservada do sistema operacional.
*   **Apoio Tático Visual:** `gemma4:e4b`. 

---

## 3. Matriz de Guardrails Sub-5B (O Fallback Essencial)
O *Sovereign Core* implementa funções SQL ativas ("Thought Nanny") projetadas para ejetar agentes do pool caso emitam saídas textuais rompendo esquemas estruturais JSON. 

* **⚠️ A Regra do Gatekeeper Reserva:** 
Apesar da limpeza de disco, **nunca apague 100% dos modelos abaixo de 5 Bilhões de parâmetros**. 
Você deve manter o `llama3.2:3b` ou o `nous-hermes3:3b` instalados silenciamente na sua máquina. Eles atuam como **backup nativo**. Se no meio da noite a recepção de Extração (`gemma4:e4b`) falhar os testes lógicos estruturais de loop, a *Dynamic Agentic Fallback* varrerá o banco procurando o reserva Imediato mais leve sem causar pânico ao Backend.

> Os modelos legados da estrutura deepseek pura (`r1:7b`) ou gerações engessadas (como `qwen2.5:7b`) foram sumariamente desativados e obsoletos no Kernel 1.2 a favor das flags híbridas em tempo-real do motor de base supracitado.
