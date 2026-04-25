# 🏗️ Arquitetura do Core & Engine Cíbrida

Este documento detalha a estrutura interna do Sovereign Pair, abrangendo desde a integração de modelos híbridos até o sandboxing de execução e processamento visual.

---

## 1. O Modelo Cíbrido (Hybrid LLM Architecture)

O Sovereign Pair opera em uma topologia **Cíbrida**, onde a inteligência é distribuída entre nós locais (Edge) e nós remotos (Cloud Mesh), garantindo soberania e performance.

### 1.1 Camadas de Execução
- **L0: Local Purist**: Inferência 100% offline via Ollama em GGUF.
- **L1: Regional Mesh**: Offload para instâncias Oracle OCI via túneis SSH seguros.
- **L2: Cloud Specialized**: Integração com provedores externos (NVIDIA, Qwen, OpenRouter) com sanitização de prompts.

---

## 2. Sandbox Python (Engineering Runtime)

Para tarefas analíticas pesadas (Pandas, Yfinance, Deep Research), o sistema utiliza um ambiente Python isolado e auto-provisionado.

### 2.1 Cadeia de Resolução (Resolution Chain)
O motor Rust (`api_trainer.rs`) localiza o Python seguindo esta prioridade:
1. **Venv Hermético**: Localizado em `sandbox/venv/bin/python3`.
2. **Standalone CPython**: Versões auto-baixadas do projeto `python-build-standalone` da Astral.
3. **System Probing**: Busca via `which python3` ou caminhos conhecidos do OS.

### 2.2 Ticker Resolver Dinâmico
O script `sovereign_matrix.py` gerencia o mapeamento de ativos financeiros, resolvendo nomes populares para tickers do Yahoo Finance com fallback dinâmico para a B3 (.SA).

---

## 3. Sovereign Vision Engine

A síntese de imagens e processamento de visão é realizada localmente, sem dependências de nuvem.

- **Motor**: `stable-diffusion.cpp` (SDXL Turbo Q8_0).
- **Integração**: O Rust gerencia uma thread daemon na porta `7860`, interceptando chamadas de `dispatch_visual_artist()`.
- **Performance**: Otimizado para CPU/Mesa drivers via AVX2/OpenBLAS, permitindo geração fotorealista em poucos segundos.

---

## 4. Otimização de Hardware (Tuning)

### 4.1 Gestão de VRAM & RAM
- **OOM Guard**: Monitoramento constante da memória de vídeo. Ao atingir limites críticos, o sistema purga o KV Cache e reduz a janela de contexto (`num_ctx`).
- **Unified Memory**: Suporte nativo para Apple Silicon, tratando a memória unificada como um pool compartilhado entre CPU/GPU.

### 4.2 Swappiness & ZRAM
- **Diretriz**: Desativar ZRAM em sistemas de IA, pois pesos quantizados são incomprimíveis.
- **Swappiness**: Recomendado definir `vm.swappiness=10` para priorizar a permanência de tensores na RAM física.
