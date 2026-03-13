"""
Sovereign Pair - Unsloth Fine-Tuning Pipeline (Fase 5.5)
Este script é um Template prático para rodar no Oracle A1 ou Master Node, consumindo
o `cognitive_distillation.jsonl` gerado pelo LangGraph (The Doctor) para destilar a 
Cadeia de Pensamento (Chain of Thought - CoT) via LoRA e fundir pesos nativos num Llama 3.2.

REQUISITOS (Em ambiente GPU Linux/Oracle A1):
!pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --no-deps "xformers<0.0.26" trl peft accelerate bitsandbytes
"""

import os
from datasets import load_dataset
from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments

# ---------------------------------------------------------
# 1. Configurações
# ---------------------------------------------------------
MAX_SEQ_LENGTH = 4096 # Pode escalar baseada na VRAM da instância
DTYPE = None # Auto detecção (Bfloat16 via Ampere)
LOAD_IN_4BIT = True # Maximiza economia de VRAM para rodar local

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cognitive_distillation.jsonl")

# ---------------------------------------------------------
# 2. Carregar o Modelo Base (Llama 3.2 1B ou 3B) via Unsloth
# ---------------------------------------------------------
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Llama-3.2-3B-Instruct", # Base LLM
    max_seq_length = MAX_SEQ_LENGTH,
    dtype = DTYPE,
    load_in_4bit = LOAD_IN_4BIT,
)

# Integrando adaptadores PEFT/LoRA (Atualiza ~1 a 10% dos pesos da rede rapidamente)
model = FastLanguageModel.get_peft_model(
    model,
    r = 16, # Rank dimension (16 é ótimo equilíbrio)
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0, # Auto-otimizado pr Unsloth
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

# ---------------------------------------------------------
# 3. Formatação do Dataset Cíbrido (ShareGPT / Llama-3 Inst)
# ---------------------------------------------------------
prompt_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Você é a inteligência Sovereign Pair. Use <thinking> para raciocinar profundamente antes de responder.<|eot_id|><|start_header_id|>user<|end_header_id|>

CONTEXTO VETORIAL:
{input}

PERGUNTA:
{instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{output}<|eot_id|>"""

def format_prompts(examples):
    instructions = examples["instruction"]
    inputs       = examples["input"]
    outputs      = examples["output"]
    texts = []
    for instruction, input, output in zip(instructions, inputs, outputs):
        text = prompt_template.format(instruction=instruction, input=input, output=output)
        texts.append(text)
    return { "text" : texts, }

print(f"Carregando Dataset Destilado: {DATASET_PATH}")
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
dataset = dataset.map(format_prompts, batched = True)

# ---------------------------------------------------------
# 4. Configurar Treinamento Contínuo (SFTTrainer)
# ---------------------------------------------------------
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = MAX_SEQ_LENGTH,
    dataset_num_proc = 2,
    packing = False, # Define False para textos curtos/Q&A
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # Ajuste dinâmico vs tamanho do seu .jsonl
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    ),
)

# ---------------------------------------------------------
# 5. Iniciar Distilação (Run it!)
# ---------------------------------------------------------
print("Iniciando injeção de Conhecimento LoRA no Córtex Llama...")
trainer_stats = trainer.train()

# ---------------------------------------------------------
# 6. Salvar Adapters e Exportar Ollama GGUF (opcional)
# ---------------------------------------------------------
print("Treino Finalizado. Exportando Lora Adapters para `lora_sovereign_model` ...")
model.save_pretrained("lora_sovereign_model") # Salva pesos relativos LoRA Localmente
tokenizer.save_pretrained("lora_sovereign_model")

# Descomente abaixo para forçar dump no formato GGUF para o Ollama rodar cru no MacBook/Ryzen
# model.push_to_hub_gguf("seu-repo/Sovereign-Llama-3.2-3B", tokenizer, quantization_method = "q4_k_m")

print("Distilação Concluída.")
