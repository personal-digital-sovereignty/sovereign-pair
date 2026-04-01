# Guia de Aquisição: Modelos Multimodais (Sovereign Tier 3)

Este documento centraliza os comandos oficiais para baixar e cachear localmente os modelos de **Visão (VLM / OCR)** e **Áudio (ASR / MIDI)** estipulados no manifesto arquitetural para o **Sovereign Pair v0.9.9**. 

A execução destes comandos garante que o *Host* (ex: Beelink) tenha todos os pesos necessários no disco antes de iniciar qualquer inferência offline (Air-Gapped).

---

## 🖼️ 1. The Eyes (Modelos de Visão e OCR)

### 1.1. Gemma 3 4B (VLM para Imagens Naturais / VQA)
Sendo um VLM massivamente adotado, o Gemma 3 4B pode ser servido primariamente via Ollama (GGUF quantizado) ou empuxado diretamente via HuggingFace para uso em engines customizadas.

**Opção A: Via Ollama (Recomendado para Svelte UI / API unificada)**
```bash
# Inicia o download da versão quantizada oficial e registra no host local
ollama pull gemma3:4b
```

**Opção B: Via HuggingFace CLI (Para engine isolada em Python/Rust)**
```bash
# Baixa o GGUF específico Q4_K_M (excelente balanço tamanho/inteligência)
huggingface-cli download google/gemma-3-4b-it-GGUF gemma-3-4b-it-Q4_K_M.gguf --local-dir ./models/vlm --local-dir-use-symlinks False
```

### 1.2. PaddleOCR-VL 0.9B (ONNX / Rust Native)
Para mantermos o *Sovereign Pair* livre de Python, nós interceptaremos a rede neural do PaddleOCR exportada matematicamente para **ONNX**. A inferência do modelo ocorrerá nativamente em Rust usando a crate `ort` (ONNX Runtime) com execução direta na CPU.

**Download dos Pesos ONNX:**
```bash
mkdir -p ./models/ocr && cd ./models/ocr
# Baixa os modelos otimizados de Detecção (Det) e Reconhecimento (Rec) em formato ONNX
wget https://huggingface.co/neulab/omni-doc-bench-weights/resolve/main/ch_PP-OCRv4_det_infer.onnx
wget https://huggingface.co/neulab/omni-doc-bench-weights/resolve/main/ch_PP-OCRv4_rec_infer.onnx
```

---

## 🎙️ 2. The Ears (Modelos de Áudio e Sinais)

### 2.1. Whisper Large-v3 Turbo (Speech-to-Text via whisper.cpp)
Ignoraremos a dependência Python do `faster-whisper`. Usaremos o monstruoso **`whisper.cpp`** com a crate `whisper-rs` em Rust. Precisamos do formato de peso nativo GGML.

**Aquisição do Modelo GGML:**
```bash
mkdir -p ./models/audio
# Baixa diretamente o binário GGML do Large-v3 Turbo convertido por Georgi Gerganov
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin -O ./models/audio/ggml-large-v3-turbo.bin
```

### 2.2. Basic Pitch (Transcrição Musical / MIDI via TensorFlow Lite)
Em vez da biblioteca Python do Spotify, baixaremos o grafo computacional puro exportado para TensorFlow Lite (`.tflite`). Esse formato minúsculo (5MB) será rodado via bindings C++ nativas pelo Rust.

**Aquisição do Grafo TensorFlow Lite:**
```bash
mkdir -p ./models/audio
# Transfere o modelo TFLite de 5MB que realiza a magia polifônica
wget https://raw.githubusercontent.com/spotify/basic-pitch/main/basic_pitch/saved_models/icassp_2022/model.tflite -O ./models/audio/basic_pitch.tflite
```

---

## 🛑 Validação de Ambiente Air-Gapped
Após executar todos os comandos acima, você pode desconectar o computador da internet. O sistema do **Sovereign Pair v0.9.9** conseguirá transcrever áudios de horas de duração em segundos, converter melodias em MIDI, dissecar tabelas do IBGE inteiras, e discutir imagens de alta resolução sem nunca fazer um único *request* para a nuvem.
