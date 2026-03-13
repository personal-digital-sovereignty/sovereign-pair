import json
import logging
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, START, END

from llama_index.core.llms import ChatMessage, MessageRole
from .brain_logger import log_perfect_reflection

logger = logging.getLogger(__name__)

# --- STATE DEFINITION ---
class CognitiveState(TypedDict):
    """
    O Estado que trafega entre os nós do LangGraph.
    """
    query: str
    context: str # Retornado pelo sqlite-vec híbrido
    original_messages: List[Dict[str, str]] # Histórico original VUE -> FastApi
    draft_response: str
    reflection_notes: str
    final_response: str
    iteration_count: int
    llm_instance: Any # Passamos a instnância dinâmica da Oracle ou Ollama

# --- NODE: DRAFTING (Rascunhando a primeira resposta rápida) ---
def draft_node(state: CognitiveState) -> Dict:
    logger.info("🧠 [Cognitive Graph] Nó 1: Drafting (Gerando rascunho inicial base)")
    llm = state["llm_instance"]
    
    # Montamos as mensagens. O System Prompt base + Memória + Nova Query com Contexto
    messages = []
    
    system_msg = """Você é o Sovereign Pair (The Nurse). 
Use as informações fornecidas no CONTEXTO para responder à PERGUNTA. 
Seja analítico. Se o contexto não responder, use seu conhecimento prévio mas pontue isso.
"""
    messages.append(ChatMessage(role=MessageRole.SYSTEM, content=system_msg))
    
    # Reconstruir memória histórica
    for msg in state["original_messages"][:-1]: # Exceto a última
        role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
        messages.append(ChatMessage(role=role, content=msg["content"]))
        
    # Última mensagem com o contexto vetorial do RAG
    user_prompt = f"CONTEXTO:\n{state['context']}\n\nPERGUNTA: {state['query']}"
    messages.append(ChatMessage(role=MessageRole.USER, content=user_prompt))

    # Inferencia LLM (Sem stream no draft)
    try:
        response = llm.chat(messages)
        draft = response.message.content
        return {"draft_response": draft, "iteration_count": state.get("iteration_count", 0) + 1}
    except Exception as e:
        logger.error(f"Erro no Drafting: {e}")
        return {"draft_response": f"Erro interno na geração do rascunho: {e}", "iteration_count": 0}

# --- NODE: REFLECT (System 2 Critique) ---
def reflect_node(state: CognitiveState) -> Dict:
    logger.info("🤔 [Cognitive Graph] Nó 2: Critique (Avaliando rigorosamente o rascunho)")
    llm = state["llm_instance"]
    
    reflection_prompt = f"""Atue como um Crítico Especialista (System 2 Thinking).
    
Analise este DRAFT DE RESPOSTA dado à PERGUNTA DO USUÁRIO. O Draft foi baseado no CONTEXTO.

CONTEXTO: 
{state['context']}

PERGUNTA DO USUÁRIO: 
{state['query']}

DRAFT DE RESPOSTA:
{state['draft_response']}

Sua tarefa:
Forneça CRÍTICAS do que está faltando, incorreto, ambíguo ou alucinado no draft em relação à pergunta ou ao contexto.
Se o draft estiver perfeito, diga 'APROVADO'.
Use a tag <thinking> para raciocinar antes de criticar. E dentro dela, a tag <reflection> se mudar de ideia.
"""
    
    try:
        response = llm.complete(reflection_prompt)
        critique = response.text
        return {"reflection_notes": critique}
    except Exception as e:
        logger.error(f"Erro no Reflection: {e}")
        return {"reflection_notes": "APROVADO"} # Fail-open: se falhar, aceita o rascunho

# --- NODE: REFINE (Consolidação Final) ---
def refine_node(state: CognitiveState) -> Dict:
    logger.info("💎 [Cognitive Graph] Nó 3: Refinement (Aplicando as críticas ao rascunho)")
    llm = state["llm_instance"]
    
    refine_prompt = f"""Atue como o Assistente Final que entregará a versão definitiva ao usuário.

RASCUNHO INICIAL:
{state['draft_response']}

CRÍTICAS RECEBIDAS (O que melhorar):
{state['reflection_notes']}

Produza a RESPOSTA FINAL DEFINITIVA, incorporando todas as melhorias e correções apontadas nas críticas. 
Não mencione as críticas ou que isso é um rascunho melhorado. Aja de forma natural em português do Brasil, formatado lindamente em Markdown de alto nível.
"""
    
    try:
         # OBS: Se a crítica diz APROVADO, ele apenas melhora gramaticalmente ou formatação.
         response = llm.complete(refine_prompt)
         final = response.text
         
         # Distilação do Conhecimento (Salvar a cadeia Pensamento + Resposta)
         log_perfect_reflection(state["query"], state["context"], state.get("reflection_notes", ""), final)
         
         return {"final_response": final}
    except Exception as e:
        logger.error(f"Erro no Refinement: {e}")
        return {"final_response": state["draft_response"]} # Volta pro draft se o refinamento quebrar

# --- EDGE ROUTER ---
def should_refine(state: CognitiveState) -> str:
    """
    Roteador Condicional. Decide se as críticas exigem refinamento.
    """
    critique = state.get("reflection_notes", "")
    
    if "APROVADO" in critique and state.get("iteration_count", 1) >= 1:
        # Se tá aprovado e já rodou pelo menos 1 loop, a gente poderia pular o refine.
        # Mas vamos forçar o refine como polimento de qualquer forma para padronizar o Stream.
        return "refine"
    
    if state.get("iteration_count", 0) > 2:
        return "refine" # Evita Loops Infinitos (Max 2 rascunhos)
        
    return "refine"


# --- COMPILE STATE GRAPH ---
def get_cognitive_graph():
    """Build and compile the LangGraph for Sovereign Reflection."""
    workflow = StateGraph(CognitiveState)
    
    workflow.add_node("draft", draft_node)
    workflow.add_node("reflect", reflect_node)
    workflow.add_node("refine", refine_node)
    
    workflow.add_edge(START, "draft")
    workflow.add_edge("draft", "reflect")
    workflow.add_conditional_edges("reflect", should_refine, ["refine"])
    workflow.add_edge("refine", END)
    
    app = workflow.compile()
    return app
