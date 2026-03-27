# Sovereign RAG: Official Models Manifest & Hardware Tiers

Este documento estabelece o padrão arquitetural oficial para o instanciamento local de modelos de linguagem (LLMs) dentro do **Sovereign Agentic Loop**. A topologia do sistema depende matematicamente da "Inquisição da Trindade" (Consenso de 3 Sub-Agentes) para mitigar a Alucinação Preditiva e garantir a integridade dos dados extraídos offline.

A escolha dos modelos abaixo **não é intercambiável aleatoriamente**, pois foi formulada sobre o princípio matemático dos **Erros Ortogonais** (arquiteturas e treinamentos alienígenas entre si para evitar colusão de alucinação em grupo).

Todos os modelos estão especificados em suas versões GGUF/Ollama (quantização recomendada: Q4_K_M).

---

## 🚀 Tier 1: Sovereign Edge (Recomendado)
**Hardware Alvo:** Máquinas com 32 GB de RAM Unificada (Teto de pico de \~27 GB no Host).
Este setup é o estado da arte para extração offline e capacidade analítica profunda.

### 🧠 A Trindade da Extração (The Inquisition Layer)
Despachados simultaneamente para análise de HTML via `tokio::join!`. A alocação estática dos 3 é inferior a 5GB VRAM.
1. **O Bisturi (The Surgeon):**
   * **Modelo:** `qwen2.5:3b` (ou o industrial `refuel-llm-2-mini:1.5b`)
   * **Papel:** Extração estrutural rígida. Resiliente a quebras de formato JSON.
2. **O Árbitro Lógico (The Reasoner):**
   * **Modelo:** `phi4-mini:latest`
   * **Papel:** Altíssimo poder de raciocínio. Excelente em identificar premissas ausentes e "confessar" o vazio (`NOT_FOUND`).
3. **O Freio de Emergência CoT (The CoT Auditor):**
   * **Modelo:** `deepseek-r1:1.5b`
   * **Papel:** Destilado do DeepSeek v3, utiliza internamente a trilha `<think>` para racionalizar o texto antes de tentar emitir uma resposta final estruturada. Aniquila o viés preditivo "Pleaser".

### 👑 O Mestre e Especialistas (Supervisor Layer)
1. **The Scribe / Orquestrador:** `qwen2.5:14b` (\~9.0 GB RAM) para a síntese final impecável, ou `llama3.1:8b` como backup geral.
2. **The Coder:** `qwen2.5:7b` (Substitui com brutal vantagem as antigas vertentes CodeLlama).
3. **O Contador / The Vector DB:** `nomic-embed-text:latest` (Embeddings leves) ou `bge-m3:latest` (Multilinguístico denso).

---

## 💻 Tier 2: Sovereign Minimal (Low End)
**Hardware Alvo:** Máquinas com 16 GB (ou extremo 8 GB) de RAM.
Este setup visa manter o consenso da Trindade rodando pacificamente sem incorrer em saturação do barramento (Out-Of-Memory/Swap), utilizando exclusivamente modelos da classe \~1.5B (SLMs ultraleves).

> ⚠️ **Diretiva de Restrição (Banimento Llama):** Modelos ultraleves da série Llama (ex: Llama 3.2 1B ou 3B) estão **ESTRITAMENTE PROIBIDOS** neste tier para o papel de Inquisidores de Extração. Diante de dados ausentes (falhas de raspagem), os modelos Llama sofrem da "Síndrome de Agradar" (Sycophancy) e inventam predições matemáticas irreais.

### 🧠 A Trindade Minimalista (The Inquisition Layer)
Consumo máximo alocado de estático + KV Cache fica entre 4 GB a 5 GB de RAM.
1. **O Bisturi (The Surgeon):**
   * **Modelo:** `qwen2.5:1.5b` (O bisturi oriental em sua versão mínima).
2. **O Árbitro Lógico (The Reasoner):**
   * **Modelo:** `smollm2:1.7b` (Uma alternativa excepcional treinada em datasets ultra-curados de altíssima qualidade).
3. **O Freio de Emergência CoT (The CoT Auditor):**
   * **Modelo:** `deepseek-r1:1.5b` (Mantido do Tier 1 por seu minúsculo peso de 1.0 GB em Q4).

### 👑 O Mestre e Especialistas (Supervisor Layer Minimal)
1. **The Scribe / Orquestrador:** `qwen2.5:7b` (\~4.7 GB RAM). Se a máquina constar com absolutos 8GB de RAM totais, recomenda-se "espremer" o Mestre com `gemma2:2b` ou `qwen2.5:3b`.

---

## 🛠️ Validação do Manifesto

Este documento foi forjado com o auxílio do **Loop de Deep Research do Google Gemini 3 Pro** (Artefato Fase 41), além de validação cruzada entre Claude 3.5 Sonnet, MS Copilot e testes autônomos locais.
