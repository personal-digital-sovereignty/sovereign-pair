# Sovereign Vision Engine (Fase G.1)

O sistema Sovereign Pair não depende de nuvem para geração de imagens (Midjourney, DALL-E, etc). 
Toda a síntese de Inteligência Visual acontece de forma 100% "Bare-Metal" no seu computador utilizando a porta local `7860`.

## A Integração Multimodal em Rust (`api_multimodal.rs`)
Nosso Backend já foi instruído no ciclo da Fase G.1 para compreender a ferramenta dinâmica `dispatch_visual_artist()`.
Se você solicitar a criação de uma arte na interface Chat Svelte, a linguagem do LLM enviará o comando JSON simulando o comportamento da API padrão, caindo na porta `7860` da sua máquina, salvando silenciosamente no `~/Vault/Images/` e refletindo em sua janela de Chat.

## Como instalar a Pipeline Local (Motor + Pesos Cíbridos)
Para evitar que você lide com dependências massivas de Python (`pip install torch torchvision`, `CUDA` toolkits, etc), padronizamos nossa orquestração focada no repósitorio universal em C++: **stable-diffusion.cpp**.

Nós criamos um script para automatizar inteiramente a decodificação para o seu sistema:

```bash
chmod +x scripts/install_sovereign_vision.sh
./scripts/install_sovereign_vision.sh
```

### O que o Script automatiza sob o capô?
1. Baixa o binário do `sd.cpp` compilado para LINUX AVX2 OpenBLAS, suportando processadores genéricos como placas gráficas embutidas (Ryzen).
2. Clona os pesos visuais da arquitetura **SDXL Turbo (Q8_0)**: Este modelo gera artes fotorealistas precisando apenas de **4 Steps**, tornando ele insanamente rápido mesmo em CPU/Mesa drivers, eliminando loops imensos.
3. Arquiva tudo na pasta centralizada do sistema `~/Sovereign_LLM/Vision/`.

## Rotina para desenhar
Sempre que ligar os motores pela manhã para trabalhar usando todo o potencial multimodal, inicie a malha visual em uma aba lateral (Terminal):

```bash
cd ~/Sovereign_LLM/Vision/sd_bin
./sd --mode server --port 7860 -m ~/Sovereign_LLM/Vision/models/sdxl_turbo.gguf
```

Isso ligará a interface de recepção na porta **7860**. Todo o resto já foi acoplado no `Sovereign_memory.db`.
