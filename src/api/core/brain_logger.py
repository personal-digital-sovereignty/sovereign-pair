import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# O JSONL format será otimizado nativamente para o Llama-Factory ou Unsloth (Modo Alpaca Instruction)
# {"instruction": "O que eh...", "input": "Contexto...", "output": "<thinking>...</thinking> Resposta"}

BRAIN_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "cognitive_distillation.jsonl")

def log_perfect_reflection(query: str, context: str, reflection: str, final_answer: str):
    """
    Grava apenas os Graph Loops que geraram reflexões reais (na Fase de critique)
    num banco de JSONL pronto para LoRA Fine-Tuning futuro.
    """
    # Se a critica só diz aprovado e não teve cadeia de pensamento rica, descartamos para não treinar coisa inútil
    if not reflection or "APROVADO" in reflection.upper() or len(reflection) < 50:
        return
        
    try:
        # Garante o diretório
        os.makedirs(os.path.dirname(BRAIN_LOG_FILE), exist_ok=True)
        
        # Padrão Unsloth ShareGPT/Alpaca
        row = {
            "instruction": query,
            "input": context,
            "output": f"<thinking>\n{reflection}\n</thinking>\n\n{final_answer}",
            "timestamp": datetime.now().isoformat()
        }
        
        with open(BRAIN_LOG_FILE, "a", encoding="utf-8") as f:
             f.write(json.dumps(row, ensure_ascii=False) + "\n")
             
        logger.info(f"💾 [Knowledge Distillation] Raciocínio Profundo salvo para Fine-Tuning. (Tamanho: {len(row['output'])} bytes).")
    except Exception as e:
        logger.error(f"Erro ao salvar Destilação: {e}")
