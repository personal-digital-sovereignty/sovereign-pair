import asyncio
import sys

sys.path.append("/app")
sys.path.append("/app/src")

from llama_index.core.llms import ChatMessage, MessageRole

from src.engine_builder import build_chat_engine
from src.agent import initialize_rag_tool

async def main():
    print("Testando Base Ollama astream_chat diretamente...")
    index, _ = initialize_rag_tool()
    
    engine = build_chat_engine(
        index, 
        history=[], 
        provider="ollama", 
        model_name="qwen2.5:0.5b", 
        tenant_id="Jeferson"
    )
    
    llm = engine._llm
    
    # Extrai o system prompt gerado pelo construtor do engine
    system_prompt = engine._system_prompt
    
    # Quando o retriever retorna 0 nodes, o context_str passado é vazio ou um template vazio.
    # O CondensePlusContext do LlamaIndex concatena o contexto no system message ou manda no User Message?
    # Vamos enviar apenas o system prompt puro + query.
    
    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content=system_prompt),
        ChatMessage(role=MessageRole.USER, content="Context information is below.\n---------------------\n\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: Olá Sovereign! Este é um teste sendo enviado diretamente do motor N8N via Webhook/HTTP Node na rede Cíbrida.\nAnswer: ")
    ]
    
    print("\nMensagens enviadas ao LLM:", [m.content[:50] + "..." for m in messages])
    
    print("\n[TESTE ASYNC] Chamando astream_chat puro do Ollama...")
    try:
        gen = await llm.astream_chat(messages)
        print("GEN retornado:", type(gen))
        
        full_text = ""
        async for chunk in gen:
            full_text += chunk.delta
            
        print(f"✅ astream_chat Sucesso: {repr(full_text)}")
    except Exception as e:
        import traceback
        print(f"❌ astream_chat FALHOU: {type(e)} - {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
