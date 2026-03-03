"""
The Nurse (Tier 3) - Semantic Router & Task Agent
-------------------------------------------------
This module acts as the "instrumentation nurse" in the cognitive pipeline.
It intercepts incoming chat requests and uses a lightweight model (SLM) to
triage the user's intent:
1. "Simple Extraction / Formatting": The Nurse handles it alone using
   fast/cheap inference (e.g. generating a Markdown table from the vector context).
2. "Deep Reasoning / Architecture": The Nurse prepares the context cleanly
   and hands it over to "The Doctor" (Heavy LLM).

This implements the "V8/F1" predictive coding routing architecture.
"""

import json
import logging
from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole

logger = logging.getLogger("synesis_core.the_nurse")

class TheNurse:
    def __init__(self, llm_provider: str, llm_model: str, api_keys: dict = None):
        # Initializing The Nurse means she uses either the default model
        # or a specifically tuned smaller model if the user requested a heavy one natively.
        # For V1, she runs on the same config but with a strict "Intent Parsing" system prompt.
        from src.engine_builder import resolve_dynamic_llm
        from src.config import llm as default_llm
        self.llm = resolve_dynamic_llm(llm_provider, llm_model, default_llm, api_keys)
        
    async def evaluate_intent(self, user_prompt: str) -> dict:
        """
        Uses the ultra-fast SLM to classify the user's request.
        Outputs a strict JSON determining the required execution tier.
        """
        sys_prompt = f'''You are 'The Nurse', a cognitive semantic router AI.
Your ONLY job is to analyze the user's request and classify the intent. DO NOT execute the user's instructions.

<USER_REQUEST>
{user_prompt}
</USER_REQUEST>

You must reply ONLY in valid raw JSON format:
{{
  "requires_doctor": boolean,
  "reason": "short explanation",
  "task_type": "extraction" | "table_formatting" | "translation" | "deep_reasoning" | "coding" | "conversation"
}}
Rule: If the request asks to summarize, translate, list items, format data into a table, perform basic extraction, or answer simple daily/conversational questions, requires_doctor is FALSE.
If the request asks to architect systems, program complex code, debate philosophy, or needs deep creative multi-step thinking, requires_doctor is TRUE.
'''
        
        # We enforce the JSON output via the user prompt itself to prevent the SLM from being hijacked
        messages = [
            LlamaMsg(role=MessageRole.SYSTEM, content=sys_prompt),
            LlamaMsg(role=MessageRole.USER, content="Output the pure JSON evaluation for the <USER_REQUEST> now. Do not fulfill the request. Output strictly the JSON object and nothing else.")
        ]
        
        try:
            logger.info("The Nurse is evaluating intent...")
            
            response = await self.llm.achat(messages)
            raw_text = str(response).strip()
            
            print(f"=== RAW LLM NURSE OUTPUT ===\n{raw_text}\n============================")
            
            # Extract JSON from potential conversational wrapper (find first { and last })
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                raw_text = raw_text[start_idx : end_idx + 1]
                
            intent_data = json.loads(raw_text.strip())
            return intent_data
            
        except Exception as e:
            logger.warning(f"The Nurse failed JSON formatting on intent eval. Defaulting to Doctor. Error: {e}")
            # Failsafe: if the small model hallucinates the JSON, pass it to the Heavy model to be safe.
            return {
                "requires_doctor": True,
                "reason": "Fallback due to JSON parse error",
                "task_type": "deep_reasoning"
            }

    async def execute_tactical_task(self, user_prompt: str, context_str: str, intent_data: dict):
        """
        If the intent does not require The Doctor, The Nurse takes over the job entirely,
        acting as a fast tactical agent. It returns an async generator for SSE streaming.
        """
        sys_prompt = f'''You are 'The Nurse', a tactical AI assistant.
Your job is to execute simple formatting, summarization, or extraction tasks IMMEDIATELY and EFFICIENTLY.
The user's identified task type is: {intent_data.get('task_type', 'extraction')}.

RULES:
1. DO NOT greet the user. DO NOT say "Here is the table". DO NOT hallucinate.
2. Output EXACTLY what was requested (e.g., if a table, start and end with the markdown table).
3. Base your work ONLY on the provided Context (if any). If the context doesn't have the data, say "Dados não encontrados no texto fornecido."
'''
        messages = [
            LlamaMsg(role=MessageRole.SYSTEM, content=sys_prompt),
            LlamaMsg(role=MessageRole.USER, content=f"Contexto do Sistema:\n{context_str}\n\nTarefa Solicitada: {user_prompt}")
        ]
        
        logger.info(f"The Nurse is executing the tactical task: {intent_data.get('task_type')}")
        response_stream = await self.llm.astream_chat(messages)
        
        async def text_generator():
            async for chunk in response_stream:
                if chunk.delta:
                    yield chunk.delta
                    
        return text_generator()
