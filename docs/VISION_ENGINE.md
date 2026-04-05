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

## A Mágica de "Zero-Touch" (Rotina de Desenho Automática)
Esqueça comandos manuais longos pelo terminal. O sistema foi programado para a filosofia de atrito zero.

Ao executar o `cargo run` ou levantar o serviço principal do Sovereign Core, o binário inspeciona furtivamente o seu disco rígido à procura do diretório `~/Sovereign_LLM/Vision`.
- Se o motor de arte for detectado, o próprio Rust invocará assincronamente **uma Thread Limpa (Daemon)** contendo a API do SD.cpp nativa mapeada para a porta **7860**.
- Quaisquer logs ou ruídos típicos da geração visual foram amordaçados do seu STDOUT/STDERR, para que o terminal principal continue minimalista e limpo.
- Quando o próprio backend Sovereign for derrubado (Ao fechar o processo principal), o artista visual "morrerá" harmonicamente junto a ele.

Simplesmente abra a UI e comece a pintar suas ideias!
