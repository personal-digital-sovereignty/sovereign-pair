# Manifesto 07: Otimização Preditiva Local (Unsloth Fine-Tuning)

Esta documentação descreve os métodos operacionais vinculados ao treinamento focado (Fine-Tuning) do Sovereign Pair. Substitui-se o emprego oneroso do grafo processual abstrato de LangGraph em *Runtime* (arquitetura Python base descontinuada) pela adequação local sintática em arquiteturas compactas (Llama-3.2 1B / 3B) ligadas ao motor Rust O.S. 

O processo fundamenta-se sob infraestrutura provisionada nas matrizes Cloud OCI A1 Base (Volume > 200GB).

---

## Estruturação de Dados de Treino

A infraestrutura de RAG gera registros operacionais logísticos armazenados na tabela restrita de histórico `chat_messages` operacionada via banco SQLite local (`sovereign_memory.db`). O conversor em formato originário (`scripts/export_unsloth_dataset.py`) é ativado localmente para processar transcrições RAG em conversões filtradas contendo lógicas exatas aplicadas com os padrões contextuais estritos (Tags Base), originando o artefato matriz `data/cognitive_distillation.jsonl`.

Para compilação dos weights operacionais remotos, o servidor Cloud utilizará instâncias padronizadas sobrepostas perante *Unsloth Framework* e *PyTorch (Cuda/RoCm)* instalados na infraestrutura Ubuntu/Arch.

## Etapa 1: Provisionamento do Ambiente Físico Dedicado (Oracle OCI / Remota)

Garante-se a isolação técnica da biblioteca Python.
```bash
# 1. Alocar Ambiente Validado Virtual
python3 -m venv .unsloth-venv
source .unsloth-venv/bin/activate

# 2. Instalar Módulo Unsloth Base Framework
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps "xformers<0.0.26" trl peft accelerate bitsandbytes
```

> **Atenuadores de Carga Node OCI**: O pacote base Unsloth, atrelado a biblioteca `bitsandbytes`, formata os tensores primitivos para alinhamentos matemáticos em `4-bit` (Quantização Dinâmica Remota). Modelos leves estruturais preenchem o uso VRAM na faixa de `~3.5GB`, escalonando acessibilidade a hardware modesto local ou servidores pequenos Cloud.

## Etapa 2: Fine-Tuning de Instrução Lógica e Convergência (SFT Trainer)

O desenvolvedor submeterá através de Mesh O.S Privada o Dataset extraído (Cópia Restrita JSONL). Em seguida, acionará processamento de compilação restrita gerida perante o script nativo: `scripts/unsloth_finetune.py`.

```bash
# Transferência Privativa Ponto a Ponto (Desktop ➔ Oracle Node)
scp local-desktop:~/sovereign-pair/data/cognitive_distillation.jsonl ./data/

# Inicialização Lógica
python scripts/unsloth_finetune.py
```

### O Script Transacional (Pipeline Operacional)
1. Efetua a importação transacional do modelo referencial inicial (`unsloth/Llama-3.2-3B-Instruct`).
2. Alocará as especificações formativas matrizais de *LoRA Adapters* aos alvos processadores principais (Q, K, V em Rank 16 O.S).
3. Converterá logs base não-otimizados locais (ShareGPT Formats) aderindo as orientações estruturais padrões *ChatML O.S*.
4. Invoca convergência iterativa O.S (Treinamento Direcionado SFT) com uso de otimizadores de base nativa.

O artefato consolidado transacional final salvará no diretório mapeado base os pesos otimizadores (`/lora_sovereign_model`).

## Etapa 3: Exportação Quantizada (GGUF Formats / Ollama Compatibillity)

Os parâmetros instrucionais recém-integrados exigirão padronizações estritas baseadas no empacotamento compresso GGUF (Utilizável na inferenciadora C/C++ padrão Ollama no desktop de acesso do engenheiro).

No código Python primário, a variável base exportacional `push_to_hub_gguf` requer habilitação sob o arquivo Python primário `scripts/unsloth_finetune.py`:
```python
# Módulo Formatação Base para O.S Ollama (Método de compactação restrito q4)
model.push_to_hub_gguf("Sovereign-Llama-3.2-3B-Thinking", tokenizer, quantization_method = "q4_k_m")
```

Baixe os pacotes integrativos finalizantes formatados (`.gguf`). Atualize os roteamentos de Model Selection local do projeto (O.S Local Rust Axum) garantindo a inicialização direta de chamadas LLM e atenuadores analógicos padronizando e suprimindo custos operacionais externos à rede privativa Desktop.
