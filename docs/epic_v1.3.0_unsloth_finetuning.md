# Épico (v1.3.0): Integração Absoluta PyTorch & Unsloth Local

**Status:** Desenhado / Arquitetura Definida para v1.3.0
**Módulo Raiz:** `Sovereign Core` (Rust), `Trainer Daemon` (Python), `Ollama Engine`
**Objetivo Principal:** Substituir o atual "Mock de Clonagem Rápida" (Modelfile Wrap) por um orquestrador real de treinamento de tensores, utilizando a biblioteca Unsloth para aceleração massiva de LoRA Fine-Tuning sem fritar a VRAM do usuário.

---

## 1. Validação de Cenário Atual (O que é Real vs Mock)

### ✅ O que é REAL hoje (v1.2.0)
1. **RAG Telemetry & Deep Research State:** Os ponteiros visuais como `Knowledge Gap`, `Sources Scanned` e `Recently Acquired` são verídicos. Eles refletem a mineração ativa do seu Hub (SQLite e Chunks).
2. **Perfection Controls:** Os sliders e as preferências que você escolhe na UI moldam verdadeiramente as intenções do que deveria ser o treinamento e geram *Payloads* absolutos via JSON/HTTP `POST`.
3. **Comunicações IPC:** O Backend em Rust realmente intercepta todas as chamadas `POST /v1/engineer/trainer/finetune` transmitidas pelo Svelte, sem gargalhar no meio do caminho. Múltiplos núcleos são engajados assincronamente.

### 🎭 O que é MOCK cenográfico (Tech Debt)
1. **Manipulação de Tensores (O Grande Truque):** Atualmente o Ollama não suporta Fine-Tuning (apenas inferência GGUF estática). Quando a tela exige um "Start Fine-Tuning", o seu motor em Rust (embaixo dos panos) apenas burla a operação engatilhando um endpoint `/api/create` no Ollama. Ele copia (`FROM base_model`) e cola `SYSTEM PROMPTS`, sem adicionar nada às redes neurais profundas do modelo. Por isso ele termina em assustadores 3 segundos.
2. **Telemetria de VRAM e Loss Gradients:** No Unsloth Monitor, o gráfico de Memory Bandwidth, Temperature, Curva de Loss, e Gradiente Norm são pré-renderizações passivas (Strings fixadas em UI).

---

## 2. A Missão do Épico v1.3.0 (Desenho Arquitetural)

Para alcançarmos Inteligência Artificial Orgânica (Soberana Absoluta), os buracos documentados no `Vault/gaps/` devem ser ensinados ao modelo via atualização retro-propagada de pesos (Loss Gradient Descent).

### Fase 1: Sovereign Python Daemon (O Músculo)
O Rust não possui bibliotecas maduras suficientes de otimização de matrizes como o ecossistema PyTorch. O Sovereign Pair precisará despachar um Sub-Serviço.
1. Criar o diretório `core/trainer/` contendo um ambiente Python blindado via `uv` ou `conda-pack`.
2. Desenvolver o script `unsloth_lora_trigger.py` baseado na API da Unsloth (HuggingFace). Ele receberá via parâmetro o diretório `gaps/` e orquestrará a transformação dos PDFs em JSONs (`Dataset.from_json()`).

### Fase 2: Rust Orchestrator (O Cérebro Supervisor)
O arquivo `api_trainer.rs` sofrerá uma mutação profunda:
1. Ao receber a chamada `POST`, o Rust irá usar `std::process::Command` alocando o daemon Python.
2. O Rust abrirá um *Piped Stream* (`stdout`) assíncrono para ouvir tudo que o Python transpirar pelo console:
   - Extraindo com expressões regulares (`regex`) métricas cruas como `Loss: 0.8122`, `VRAM_Used_Gb: 6.4`, `Temp: 82C`.
3. Direcionará exatamente essa extração para o nosso canal de SSE já construído: `TRAINER_LOGS`. Assim, a aba **Unsloth Monitor** explodirá em telemetria viva e reativa que pulsa junto com sua Placa de Vídeo.

### Fase 3: Auto GGUF Quantization & Ollama Reload (Fechando o Loop)
Treinar via Unsloth gera pesos LoRA cruzeiros (Safetensors), que o Ollama não compreende de imediato.
1. O pipeline Python deverá executar o comando de *Merge to 4bit GGUF* nativo do Unsloth (`model.save_pretrained_gguf("model", tokenizer, quantization_method = "q4_k_m")`).
2. Uma vez empacotado o arquivo binário `.gguf`, o Rust (Pai) retoma o controle, deleta o cache temporário para economizar SSD, e emite finalmente a chamada verdadeira ao Ollama (`/api/create` via arquivo cru físico `.gguf`). O usuário terá um modelo novo com raciocínio expandido!

---

> [!CAUTION] 
> **Friction Warning**
> O usuário deverá garantir que possui suporte a Hardware local (Placas NVIDIA série 30xx/40xx RTX) com drivers nativos compilados instalados, ou que as chaves da Oracle Sandboxing Cloud (OCI) estejam bem estabilizadas no *Settings* para repassar carga extrema de tensores. Modelos Edge de 3B com LoRA Rank 16 costumam tomar ao menos ~5.8GB de VRAM bruta durante o finetuning PEFT otimizado via Flash_Attention.
