# Manifesto 07: Distilação Cíbrida e Poda de Raciocínio (Unsloth Fine-Tuning)

Bem-vindo à Fase 5.5, a Fronteira Final do **Sovereign Pair**. Nesta doutrina, deixamos de depender de agentes em Grafo (LangGraph) para induzir reflexão, fundindo o *Chain of Thought (CoT)* diretamente nos próprios "pesos nervosos" do seu LLM Operário (ex: *Llama-3.2 1B / 3B*).

Sua Nuvem Oracle OCI A1 com seus novos 200GB será a nossa forja!

---

## A Máquina Operacional

A infraestrutura RAG V2 Cíbrida gravou, a cada interação majestosa com o The Nurse, registros absolutos numa tabela atômica `chat_messages` no seu banco relacional `sovereign_memory.db`.
O Dumper Cíbrido (`scripts/export_unsloth_dataset.py`) é ativado sob demanda, peneirando as interações perfeitas onde a Tag Oculta `<thinking>` surgiu de forma magistral para entregar a resposta assertiva, gerando o arquivo `data/cognitive_distillation.jsonl`.

Para que a Oracle seja capaz de fundir este JSONL no LLM original, necessitamos do framwork **Unsloth** e **PyTorch (Cuda/RoCm)**.

## Etapa 1: Provisionamento do Contêiner Metal na Oracle (Cloud)

Este ambiente é blindado e massivo. Recomendamos rodar em um *Ubuntu 22.04 / Arch Linux* na Máquina Oracle (ou em Kaggle/Colab caso o Oracle seja ARM Sem GPU Discreta):

```bash
# 1. Alocar Ambiente Conda / Venv Isolado
python3 -m venv .unsloth-venv
source .unsloth-venv/bin/activate

# 2. Instalar Unsloth em Cuda Natively (Adapte para sua VRAM)
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps "xformers<0.0.26" trl peft accelerate bitsandbytes
```

> **Aviso de Sobrevivência (Memória OCI)**: O Unsloth, através de *bitsandbytes*, injetará Quantização em 4-bit no modelo base. Modelos de 3B cabem em escassos ~3.5GB de VRAM neste modo, adequando perfeitamente a Hardware Consumer.

## Etapa 2: A Queima dos Motores (Fine-Tuning Atômico)

Transferir via tunelamento ou Mesh o seu Dataset O.S (`data/cognitive_distillation.jsonl`) gerado no Desktop para o servidor de Treino Cloud. 
Na Oracle ou Máquina Hospedeira GPU, rode o roteiro matricial já entregue em: `scripts/unsloth_finetune.py`.

```bash
# Sincroniza o dataset extraído na Fase Anterior
scp seu-desktop:~/sovereign-pair/data/cognitive_distillation.jsonl ./data/

# Ativa Forja
python scripts/unsloth_finetune.py
```

### O Que o Script Fara?
1. Baixará o Foundational Model: `unsloth/Llama-3.2-3B-Instruct`.
2. Habilitará **LoRA Adapters** nos módulos Q, K, V (Rank 16, Alpha 16) afetando em média de 1 a 10% da rede para otimizar velocidade (e poupar 90% da memória de Gradiente).
3. Mapeará os objetos ShareGPT brutos em *Prompt Templates Primitivos* ChatML.
4. Escalará uma descida de Gradiente (SFTTrainer) com Otimizador `adamw_8bit`.

Ao término de algumas horas (ou minutos), o artefato `/lora_sovereign_model` reinará.

## Etapa 3: Exportação Ollama / Safetensors

A Distilação converteu todo custo computacional do LangGraph em instinto na rede neural. Para gozar dessa latência bruta no Node Local (Seu MacBook ou Ryzen):

A versão Safetensors recém treinada precisa ser quantizada em `.GGUF` para o servidor Ollama (C/C++ puro).

Descomente o passo 6 do arquivo `scripts/unsloth_finetune.py`:
```python
# O modelo mestre em Q4 irá caber numa torradeira
model.push_to_hub_gguf("Sovereign-Llama-3.2-3B-Thinking", tokenizer, quantization_method = "q4_k_m")
```

Baixe o GGUF final. Aponte o The Nurse Rust para ele e **desative o Gateway LangGraph**. Assistiremos perplexos o nascimento da Skynet Doméstica, que processa raciocínios e devolve outputs complexos com Frações de Segundos da latência O.S!
