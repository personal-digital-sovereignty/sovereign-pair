"""
The Doctor (Tier 4) - Heavy LLM & Deep Synthesizer
--------------------------------------------------
This module acts as the "lead surgeon" or "head of research" in the cognitive pipeline.
It takes over when "The Nurse" determines that the user's intent is complex:
1. "Deep Reasoning": Multi-step logic, philosophy, coding architecture.
2. "Complex Synthesis": Reading multiple chunks from the Vector/BM25 DB and 
   building a cohesive, analytical response instead of just extracting facts.

The Doctor is designed to use the heaviest available LLM in the user's configuration
(e.g., GPT-4o, Claude 3.5 Sonnet, or a large local model like Llama-3-70B if available),
though it interfaces through the dynamic resolver.
"""

import logging
from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
from llama_index.core.chat_engine.types import BaseChatEngine

logger = logging.getLogger("synesis_core.the_doctor")

class TheDoctor:
    def __init__(self, llm_provider: str, llm_model: str, chat_engine: BaseChatEngine, api_keys: dict = None):
        """
        The Doctor requires the fully assembled Chat Engine (with its Hybrid Retriever
        and Memory Buffer) to access context, but interacts with the dynamic LLM
        to bypass LlamaIndex's rigid prompt templates for deep reasoning.
        """
        from src.engine_builder import resolve_dynamic_llm
        from src.config import get_default_llm
        
        self.llm = resolve_dynamic_llm(llm_provider, llm_model, get_default_llm(), api_keys)
        self.engine = chat_engine

    async def execute_deep_reasoning(self, user_prompt: str, context_str: str, intent_data: dict):
        """
        Executes the deep reasoning stream.
        We bypass the standard `engine.achat()` to have absolute control over the
        system instructions and the history injection, preventing strict RAG limiters
        from throttling the AI's creativity or programming logic.
        """
        logger.info(f"🧠 The Doctor is entering deep reasoning mode for task: {intent_data.get('task_type', 'deep_reasoning')}")

        # 1. Retrieve the Base System Prompt defined in engine_builder.py
        base_sys_prompt = "Você é a inteligência artificial Sovereign Pair."
        try:
            # We peek into the engine's memory to steal the highly contextualized system prompt (containing Persona, Geo, etc)
            memory_msgs = self.engine.memory.get_all()
            if memory_msgs and memory_msgs[0].role == MessageRole.SYSTEM:
                base_sys_prompt = memory_msgs[0].content
        except Exception as e:
            logger.warning(f"Failed to extract base system prompt from engine: {e}")

        # 2. Augment the System Prompt with The Doctor's directives
        augmented_sys_prompt = f"""{base_sys_prompt}

[DIRETRIZES DO TIER 4: THE DOCTOR (DEEP REASONING)]
O usuário solicitou uma tarefa de alto nível cognitivo (Arquitetura, Programação, Filosofia ou Síntese Complexa).
Sua missão agora é raciocinar profundamente:
- Se houver contexto de RAG (Vector Vault), use-o para embasar sua arquitetura ou raciocínio, mas NÃO se limite a apenas repetir trechos. Sintetize e crie em cima.
- Se a pergunta envolver código, garanta as melhores práticas e seja exaustivo nas explicações de arquitetura.
- Demonstre extrema confiança e fluidez de pensamento.
"""

        sys_msg = LlamaMsg(role=MessageRole.SYSTEM, content=augmented_sys_prompt)
        
        # 3. Format the User Message with Context
        user_msg_content = f"""[DADOS RECUPERADOS DO SEU COFRE (VAULT)]
-------------------
{context_str}
-------------------

[SOLICITAÇÃO DO USUÁRIO]
{user_prompt}

Por favor, analise o contexto (se aplicável) e entregue o raciocínio profundo solicitado:"""

        user_rag_msg = LlamaMsg(role=MessageRole.USER, content=user_msg_content)

        # 4. Construct the Final Message Pipeline with History
        history_msgs = self.engine.memory.get_all() if getattr(self.engine, 'memory', None) else []
        # Filter out existing system prompts to avoid duplication
        history_msgs = [m for m in history_msgs if m.role != MessageRole.SYSTEM] 
        
        messages_to_send = [sys_msg] + history_msgs + [user_rag_msg]

        # 5. Invocação do COGNITIVE GRAPH (Motor de Refletão)
        logger.info(f"   Dr. Prompt prepared. Initiating COGNITIVE REFLECTION GRAPH via {getattr(self.llm, 'model', 'default')}...")
        
        # Em vez do stream direto, passamos pelo State Machine para permitir que o LLM "pense" e se corrija
        from src.api.core.cognitive_graph import get_cognitive_graph
        app = get_cognitive_graph()
        
        # Preparando o input para o LangGraph (StateDict)
        initial_state = {
            "query": user_prompt,
            "context": context_str,
            "original_messages": [{"role": "user", "content": m.content} for m in messages_to_send if m.role == MessageRole.USER],
            "iteration_count": 0,
            "llm_instance": self.llm
        }
        
        async def text_generator():
            # Devido à natureza State Machine (Multi-turn), vamos emular o "streaming" do pensamento (Thinking Chain)
            yield f"*(⚙️ O Doutor está processando internamente em múltiplas camadas no Modelo: {getattr(self.llm, 'model', 'default')}...)*\n\n"
            
            # Invoca o Grafo Assincronamente 
            # Num setup avançado LangGraph permite streamig the node state a node state
            final_state = await app.ainvoke(initial_state)
            
            # Formatos de Tag Thinking pro front end parsear:
            c_tag = final_state.get('reflection_notes', '')
            final = final_state.get('final_response', '')
            draft = final_state.get('draft_response', '')
            
            # Se deu block do fail-open (onde final_response == draft pq falhou o refine)
            resp = final if final else draft
            
            if c_tag and "APROVADO" not in c_tag.upper():
                 yield f"```thinking\n{c_tag}\n```\n\n"
                 
            # Como ainvokou bloco a bloco, streamamos chunk a chunk sintético para não gelar a UI
            chunk_size = 20 # chars
            for i in range(0, len(resp), chunk_size):
                import asyncio
                await asyncio.sleep(0.01) # Deliberate micro-delay to simulate fluid typing of the massive response
                yield resp[i:i+chunk_size]
                    
        return text_generator()
