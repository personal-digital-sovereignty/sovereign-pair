# Treatise IX: Local Predictive Optimization (Unsloth Fine-Tuning)

This documentation describes the operational methods tied to Sovereign Pair's focused training (Fine-Tuning). The costly employment of LangGraph's abstract procedural graph at *Runtime* (discontinued base Python architecture) is replaced by syntactic local adaptation on compact architectures (Llama-3.2 1B / 3B) linked to the OS Rust engine.

The process is grounded under provisioned infrastructure in the OCI A1 Base Cloud matrices (Volume > 200GB).

---

## Training Data Structuring

The RAG infrastructure generates logistic operational records stored in the restricted operational history table `chat_messages` operated via the local SQLite database (`sovereign_memory.db`). The origin-format converter (`scripts/export_unsloth_dataset.py`) is activated locally to process RAG translations into filtered conversions containing exact logics applied with strict contextual standards (Base Tags), generating the master artifact `data/cognitive_distillation.jsonl`.

To compile the remote operational weights, the Cloud server will use standardized instances superimposed over the *Unsloth Framework* and *PyTorch (Cuda/RoCm)* installed on the Ubuntu/Arch infrastructure.

## Step 1: Physical Dedicated Environment Provisioning (Oracle OCI / Remote)

The technical isolation of the Python library is guaranteed.
```bash
# 1. Allocate Virtual Validated Environment
python3 -m venv .unsloth-venv
source .unsloth-venv/bin/activate

# 2. Install Unsloth Base Framework Module
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps "xformers<0.0.26" trl peft accelerate bitsandbytes
```

> **OCI Node Load Attenuators**: The Unsloth base package, coupled with the `bitsandbytes` library, formats primitive tensors for mathematical alignments in `4-bit` (Remote Dynamic Quantization). Structural lightweight models fill VRAM usage within the `~3.5GB` range, scaling accessibility to modest local hardware or small Cloud servers.

## Step 2: Logic Instruction and Convergence Fine-Tuning (SFT Trainer)

The developer will submit the extracted Dataset (Restricted JSONL Copy) through the Private OS Mesh. After that, they will invoke restricted compilation processing managed via the native script: `scripts/unsloth_finetune.py`.

```bash
# Peer-to-Peer Privatized Transfer (Desktop ➔ Oracle Node)
scp local-desktop:~/sovereign-pair/data/cognitive_distillation.jsonl ./data/

# Logical Initialization
python scripts/unsloth_finetune.py
```

### The Transactional Script (Operational Pipeline)
1. Performs the transactional importation of the initial referential model (`unsloth/Llama-3.2-3B-Instruct`).
2. Will allocate matrix formatting specifications of *LoRA Adapters* to the main processor targets (Q, K, V in Rank 16 OS).
3. Will convert unoptimized local base logs (ShareGPT Formats) adhering strictly to standard *ChatML OS* structural guidelines.
4. Invokes iterative OS convergence (Directed SFT Training) using native base optimizers.

The final transactional consolidated artifact will save the optimizing weights (`/lora_sovereign_model`) in the globally mapped base directory.

## Step 3: Quantized Export (GGUF Formats / Ollama Compatibility)

The newly integrated instructional parameters will demand strict standardizations based on GGUF compressed packaging (Usable in the standard Ollama C/C++ inference engine on the engineer's access desktop).

In the primary Python code, the export base variable `push_to_hub_gguf` requires enabling under the primary Python file `scripts/unsloth_finetune.py`:
```python
# Base Formatting Module For OS Ollama (Restricted q4 compression method)
model.push_to_hub_gguf("Sovereign-Llama-3.2-3B-Thinking", tokenizer, quantization_method = "q4_k_m")
```

Download the final integrating formatted packages (`.gguf`). Update the local router Model Selection of the project (OS Local Rust Axum) ensuring the direct initialization of LLM calls and analog attenuators, standardizing and suppressing external operational costs linked to the private Desktop networking.
