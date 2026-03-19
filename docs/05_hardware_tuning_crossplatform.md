# Sovereign Pair: Cross-Platform Hardware Tuning (macOS & Windows)

Este documento centraliza as estratégias de otimização de baixo nível para o motor de inferência local (Ollama / Llama.cpp) em Sistemas Operacionais não-Linux, com foco especial em hardware com severas restrições de RAM (8GB a 16GB).

---

## 🍎 Ecossistema Apple (macOS)

A arquitetura de hardware da Apple diverge substancialmente do modelo x86 tradicional.

### 1. Apple Silicon (M1 / M2 / M3 - ARM64)
Os chips Apple Silicon possuem a **Arquitetura de Memória Unificada (UMA)**. O processador (CPU) e o acelerador gráfico (GPU - Metal) leem o exato mesmo pente de RAM. 

**Otimização para M1 (8GB de RAM):**
- **Restrição de Hardware:** A Apple trava a alocação de vídeo (GPU) em aproximadamente `2/3` da RAM total. Num M1 de 8GB, o Ollama não conseguirá usar mais do que `~5.3GB` de VRAM acelerada pelo Metal.
- **Estratégia de Threads (Crucial):** O Chip M1 base possui 8 Núcleos divididos em: **4 P-Cores (Performance)** e **4 E-Cores (Eficiência)**. 
  - ❌ *Erro Comum:* Setar `OLLAMA_NUM_THREADS=8`. Se o Ollama designar matemática tensorial para os E-Cores, os P-Cores terão que reduzir a velocidade para esperar o sincronismo. O desempenho despenca.
  - ✅ *Engenharia Correta:* Declare `OLLAMA_NUM_THREADS=4` para ancorar a carga matematicamente estrita nos núcleos de alto desempenho.
- **Variáveis (`~/.zshrc` ou LaunchAgent):**
  ```bash
  export OLLAMA_NUM_THREADS=4
  export OLLAMA_NUM_PARALLEL=1
  export OLLAMA_MAX_LOADED_MODELS=1
  export OLLAMA_KEEP_ALIVE=2m
  ```

**Otimização para M1 Pro/Max (16GB de RAM):**
O modelo de 16GB já entrega um respiro monumental, oferecendo à API Metal cerca de `~10.6GB` limpos. Aqui podemos sustentar paralelismo moderado (`OLLAMA_NUM_PARALLEL=2`) e modelos acima de 8B (ex: Llama-3 8B q8_0). O número de P-Cores no M1 Pro sobe para 6 ou 8, logo, o `OLLAMA_NUM_THREADS` deve ser ajustado para acompanhar os *P-Cores exatos* do seu chip.

### 2. Apple Intel Core (x64)
Macbooks Intel não possuem a arquitetura UMA nem decodificação tensorial avançada do framework Metal3. Eles dependem brutalmente do CPU e de iGPUs (ou discretas da AMD).
- **Abordagem:** Tratar de modo equivalente ao Linux base, limitando as Threads à metade das lógicas (Ignorando o Hyperthreading) e ativando aceleração Accelerate Framework.
- **Uso Crítico em 8GB:** Não rode a UI do Sovereign Pair via Electron/Chrome enquanto usar a API. Use o terminal ou a PWA instalada leve, delegando no máximo 4GB para o LLM.

---

## 🪟 Ecossistema Microsoft (Windows)

No Windows 10/11, as restrições baseiam-se fortemente no formato de Execução do Ollama (Virtualizado via WSL2 vs Executável Binário Nativo).

### Cenário 1: WSL2 ou Standalone Binary Desktop (Isolamento Linux no Windows)
O Windows Subsystem for Linux arquiteta um limite virtual agressivo. Por padrão dinâmico, o WSL2 se recusa a invadir mais do que **50% da sua RAM Total**. 
Num Intel Core i5 com 8GB de RAM, o seu *Sovereign Core* no WSL2 tentará sobreviver com **risíveis 4GB de RAM virtuais**. 

**Otimização via `.wslconfig`:**
Na pasta Raiz do seu usuário Windows (`C:\Users\SEU_NOME\.wslconfig`), você deve forçar o hipervisor com as regras soberanas:
```ini
[wsl2]
# Expandir limite de RAM para 6GB num host de 8GB
memory=6GB
# Limitar número de processadores virtuais (para o i5 10th Gen, se for 4 cores/8 threads, use 4)
processors=4
# DESLIGAR Swap do WSL VHD (Disco Paging mata a velocidade do LLM!)
swap=0
```

### Cenário 2: Ollama Nativo (Windows `.exe`)
Para hardware sem placa de vídeo NVIDA, o executável recai para instruções matemáticas x86_64 AVX2/AVX512.

**Otimização Intel Core i5 10xxx (8GB / 16GB RAM):**
O Intel série 10 não possui a arquitetura BIG.little (P-Cores vs E-Cores dos Intel 12+), ele roda núcleos brutos simétricos.
- Configurar as Variáveis de Ambiente do Windows (`Win + R` -> `sysdm.cpl` -> Guia Avançado -> Variáveis de Ambiente):
  - `OLLAMA_NUM_THREADS` = `Equivalente aos Núcleos Físicos` (Se for i5-10300H (4 Cores/8 Threads), setar como **4**).
  - `OLLAMA_NUM_PARALLEL` = `1` (Para 8GB) ou `2` (Para 16GB).
  - `OLLAMA_KEEP_ALIVE` = `2m` (Altamente recomendado no Windows).

Nenhum ajuste do *Systemd* é aplicado no Windows. Todas as restrições devem nascer explicitamente através do painel "Environment Variables" do painel de controle originário antes da abertura do ícone do Ollama no System Tray.
