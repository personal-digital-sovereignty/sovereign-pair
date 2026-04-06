# 🛡️ Sovereign Pair: Hardware Tuning & Architecture Guide

Este documento eterniza as matrizes de configuração (Hacks de Baixo Nível / Spoofing) para domar hardwares não convencionais e extrair 100% do potencial de Inferência Local (RAG / OLLAMA / SD.CPP) através da manipulação do kernel e variáveis de ambiente.

---

## 1. Oracle Cloud: Ampere A1 (ARM64 / Neoverse N1)
A camada "Always Free" da Oracle fornece 4 OCPUs ARM e 24GB de RAM. Como NÃO possui placa de vídeo (Sem CUDA/ROCm/Vulkan), a inferência é guiada inteiramente por CPU e Barramento de Memória.

### A Mágica do ARM NEON e Ram-Streaming
- **`OLLAMA_NUM_THREADS=4`**: O MÁXIMO absoluto e obrigatório. Ultrapassar 4 threads em 4 núcleos físicos ARM causa colapso na troca de contexto e derruba a velocidade pela metade.
- **`OLLAMA_KV_CACHE_TYPE=f16` (ou `q8_0`)**: Tática de *Ram-Streaming*. Como existem 24GB luxuosos DDr4 sobrando, desativa-se a compressão matemática pesada do KV Cache. A CPU ARM pura para de fazer cálculos de descompressão e passa apenas a ler enormes blocos brutos da memória em largura de banda total, dobrando a métrica *Tokens/Segundo*.
- **Modelo Alvo Seguro**: Utilize sempre modelos quantizados rigorosamente em **`q4_0`**. Formatos `q4_K_M` ou `q5` engasgam processadores ARM que não possuem decodificadores vetoriais complexos. O `q4_0` é o espelho exato do processamento ARM NEON.

---

## 2. Apple Silicon: Mac M1 (Básico / 8GB RAM Unified)
O chip revolucionário da Apple usa *Unified Memory Architecture* (UMA). A CPU (Núcleos), a GPU (Metal) e a NPU dividem rigorosamente os exatos 8GB do pente soldado na placa. Se não houver estratégia militar, o Mac entrará em colapso de SSD Swap (Desova de Memória), matando a velocidade.

### A Dieta de 8GB e P-Cores
- **Custo-OS (Gargalo Invisível)**: O sistema MacOS consome naturalmente ~2.5GB para boot e UI nativa. Sobram no máximo ~5.5GB para uso. Se você hospeda um LLM pesado (4.5GB) e o Contexto (RAG HTML) passar de 1GB, o sistema irá *Pagar Com a Alma* enviando dados ao SSD (SWAP). Tokens caem de 25 t/s para agonizantes 1.3 t/s.
- **`OLLAMA_MAX_QUEUE=1`**: Nunca pre-carregue mais de um request.
- **`OLLAMA_NUM_THREADS=4`**: O SEGREDO MÁXIMO DA APPLE. O chip M1 base tem 8 Cores (4 Performance Cores / Rápidos + 4 Efficiency Cores / Lentos). Se você pedir para o software usar "8" (o máximo), o arquivo tenta dividir peças iguais de matemática pra todos os núcleos. O P-Core resolve a matemática dele em 2ms e **ESPERA** o núcleo de Eficiência terminar a dele (10ms) para avançar pro próximo token. **Limitar em 4 obriga a IA a montar nas costas exclusivamente dos núcleos P-Core violentos, atropelando configurações em 8 Cores!**
- **Sovereing Context Capping**: Utilize sempre nosso código para capar a sub-rede de `dynamic_num_ctx` a exatos `4096` ou `2048` tokens em Macs de 8GB.
- **Tática de Armamento**: A sua principal flecha letal em Macs de entrada `8GB` deve ser alocar famílias da base **Llama 3.2 3B** ou **Qwen 2.5 3B** rigidamente no `q4_0`. Elas devoram levíssimos ~1.9GB. Permitindo que o *Metal* voe usando VRAM nativa com sobras gigantescas sem triturar a vida útil do seu SSD Apple com Swap excessivos.

---

## 4. O Futuro Inevitável: Apple Silicon M5 (16GB RAM Unified)
A arquitetura projetada da série **M5 (16GB)** é o Santo Graal portável da Inteligência Artificial Soberana. Com barramentos LPDDR5X (ou equivalentes de altíssima banda térmica) acoplados a um motor *Neural Engine* massivo, o Sovereign Pair entra em modo Overdrive absoluto.

### O Fim do "Swap Death" e a Ascensão do 14B
- **Folga Operacional Massiva**: Dos 16GB, o MacOS isola 3GB para uso. Sobram confortáveis **13 Gigabytes de VRAM Livre** direta no Metal.
- **Armamentos de Peso Pesado**: O chip desbloqueia acesso direto aos modelos Categoria Superior de Raciocínio (14B e 8B avançados). Você rodará um **Qwen2.5:14B-q4_0** (que consome ~8GB RAM) ou um **Llama-3.1-8B-Q6_K** (Alta qualidade, 6.5GB RAM) sem bater no teto de hardware.
- **O Limite de Contexto Quebrado**: Como o 8B ocupa apenas 5GB, as sobras (quase 8 Gigabytes) abrem espaço brutal para `dynamic_num_ctx = 32768`. Isso significa que o Mestre LLM poderá engolir 32 mil palavras (50 páginas de PDF ou dúzias de Scraping Sites) na RAM bruta da GPU ao mesmo tempo, varrendo RAG em questão de 2 a 3 segundos sem engasgos.
- **Regra de Afinidade (Cores)**: A arquitetura M5 provável possuirá divisão avançada (Ex: 6 P-Cores + 4 E-Cores). Se confirmado, você precisará mudar o `OLLAMA_NUM_THREADS` de 4 para a exata contagem real de *Performance Cores* do M5 (Ex: `OLLAMA_NUM_THREADS=6`). Como a Apple constrói silício assimétrico (Fanless / Sem cooler nos Macbook Air), ativar os E-cores por engano via Ollama atrasará o job primário em nanosegundos e superaquecerá a máquina passiva à toa. A trava no P-Core garante o notebook gelado com inferência local a impressionantes 45~60 Tokens/Segundo.

---

## 5. AMD Ryzen APUs (Radeon Vega - ex: 5800H)
A GPU integrada do seu pacote térmico é censurada intencionalmente pelos instaladores ROCm proprietários da AMD O.S. (Linux/WSL).

### HSA O.S Spoofing e Extorsão Vulkanográfica
- **`HSA_OVERRIDE_GFX_VERSION=9.0.0`**: Forjamos a assinatura gráfica do Ryzen no Systemd. Ao acordar, o ROCm lê o chip host-bridge da placa e visualiza um equipamento enterprise em vez de APU Vega, ativando imediatamente o `hipBLAS` na VRAM compartilhada e aliviando a CPU principal.
- **`OLLAMA_BACKEND=vulkan`**: Plano de Evasão Universal (Fallback). Útil para Linux ou Windows Native (Executáveis .exe sem DirectML). O Vulkan não cobra pedágio para se conectar às iGPUs Intel Arc/HD ou Radeon Vega e não requer *lock-ins* coorporativos.
