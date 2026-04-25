# 📥 Aquisição de Modelos (Weights & Assets)
## Guia de Provisionamento Offline

Este documento centraliza os comandos necessários para baixar e gerenciar os pesos dos modelos neurais (LLM, VLM, OCR, Audio) utilizados pelo Sovereign Pair.

---

## 1. Modelos de Linguagem (Ollama)

O Sovereign Pair orquestra o Ollama para inferência de texto. Use os comandos abaixo para garantir que os modelos corretos estão no cache local:

```bash
# Modelos Recomendados por Tier:
ollama pull qwen2.5:0.5b     # Estagiário (Latência Ultra-baixa)
ollama pull qwen2.5:7b       # Analista Júnior (Balanço Ideal)
ollama pull llama3.1:8b      # Senior Generalista
ollama pull llama3.3:70b     # Especialista (Requer 48GB+ VRAM)
```

---

## 2. Visão e OCR (Multimodal)

### 2.1 Gemma 3 4B (VLM)
Recomendado para análise de imagens e VQA (Visual Question Answering).
```bash
ollama pull gemma3:4b
```

### 2.2 PaddleOCR (ONNX)
Para extração de texto de documentos sem dependência de Python (via Rust `ort`).
```bash
mkdir -p ./models/ocr
wget https://huggingface.co/neulab/omni-doc-bench-weights/resolve/main/ch_PP-OCRv4_det_infer.onnx -P ./models/ocr
wget https://huggingface.co/neulab/omni-doc-bench-weights/resolve/main/ch_PP-OCRv4_rec_infer.onnx -P ./models/ocr
```

---

## 3. Áudio e Sinais (ASR)

### 3.1 Whisper Large-v3 Turbo (GGML)
Usado para transcrição de áudio via `whisper.cpp`.
```bash
mkdir -p ./models/audio
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin -O ./models/audio/ggml-large-v3-turbo.bin
```

### 3.2 Basic Pitch (MIDI)
Para conversão de áudio musical em MIDI (TensorFlow Lite).
```bash
wget https://raw.githubusercontent.com/spotify/basic-pitch/main/basic_pitch/saved_models/icassp_2022/model.tflite -O ./models/audio/basic_pitch.tflite
```

---

## 4. Ferramentas de Download

- **HuggingFace CLI**: Para baixar GGUFs específicos que não estão no Ollama.
  ```bash
  huggingface-cli download <repo> <file> --local-dir ./models
  ```
- **SHA-256 Checksum**: Sempre valide a integridade dos pesos baixados manualmente em ambientes de produção.
