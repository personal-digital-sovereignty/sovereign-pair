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

### 1.2. PaddleOCR-VL 0.9B (Extração Rígida em CPU)
Este modelo foge do padrão GGUF/Ollama pois utiliza arquitetura otimizada pontual para leitura de documentos. Deve ser instalado o framework oficial.

**Instalação do CLI/Pipeline e Download Automático:**
```bash
# Instala o ecossistema do PaddleOCR via Python
pip install paddlepaddle paddleocr

# Comando inicial de aquisição do modelo (Força o download dos pesos de 0.9B)
# Ao rodar pela primeira vez contra uma imagem teste, os pesos seram baixados para ~/.paddleocr/
paddleocr --image_dir ./teste.png --use_angle_cls true --lang pt --precision float16
```
*(Nota: Substitua `./teste.png` pelo caminho de qualquer imagem genérica presente no sistema apenas para deflagrar o gatilho de download).*

---

## 🎙️ 2. The Ears (Modelos de Áudio e Sinais)

### 2.1. Whisper Large-v3 Turbo (Speech-to-Text ASR)
Para máxima velocidade na CPU ou iGPU, não usaremos o modelo "puro" da OpenAI, mas sim a conversão otimizada em CTranslate2 rodando sob o motor `faster-whisper`.

**Instalação e Aquisição:**
```bash
# Instala a engine de inferência acelerada
pip install faster-whisper

# Baixa os pesos quantizados específicos do modelo Large-v3 Turbo 
# (Baixa para o diretório de cache padrão do HuggingFace)
huggingface-cli download Systran/faster-whisper-large-v3-turbo --local-dir ~/.cache/huggingface/hub/models--Systran--faster-whisper-large-v3-turbo
```

### 2.2. Basic Pitch (Transcrição Musical / MIDI)
Desenvolvido pelo Spotify Research, este modelo é minúsculo (~5MB) e opera maravilhosamente bem em CPU.

**Instalação e Aquisição:**
```bash
# Instala o software pip
pip install basic-pitch

# O modelo TensorFlow Liteweight de 5MB é empacotado e baixado automaticamente junto com a instalação da biblioteca via pip. Nenhuma ação adicional ou HuggingFace CLI é necessária.
# Exemplo de comando local gerando midi:
basic-pitch ./output_folder ./audio_file.wav
```

---

## 🛑 Validação de Ambiente Air-Gapped
Após executar todos os comandos acima, você pode desconectar o computador da internet. O sistema do **Sovereign Pair v0.9.9** conseguirá transcrever áudios de horas de duração em segundos, converter melodias em MIDI, dissecar tabelas do IBGE inteiras, e discutir imagens de alta resolução sem nunca fazer um único *request* para a nuvem.
