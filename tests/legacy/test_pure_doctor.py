import asyncio
from src.engine_builder import build_chat_engine

async def run_doctor():
    print("Iniciando Teste Puro The Doctor (LlamaIndex Context)..")
    
    from llama_index.core import Document, VectorStoreIndex
    dummy_index = VectorStoreIndex.from_documents([Document(text="Vazio")])
    
    # Simulate routes.py
    engine = build_chat_engine(
        index=dummy_index,
        provider="ollama",
        model_name="llama3.2:latest",
        tenant_id="PDS"
    )
    
    message = "Escreva um ensaio filosófico sobre o significado do conhecimento e a soberania digital humana na arquitetura moderna de software."
    
    # No vectors for now, to isolate the Generation Engine
    context_str = "Nenhum documento vetorial encontrado."
    
    sys_prompt = "Você é a inteligência artificial Sovereign Pair."
    
    try:
        from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
        messages = [
            LlamaMsg(role=MessageRole.SYSTEM, content=sys_prompt),
            LlamaMsg(role=MessageRole.USER, content=f"Contexto do Sensus Vault:\n{context_str}\n\nUser: {message}")
        ]
        
        print(f"Executing... Context: {len(messages)} messages")
        response_gen = await engine._llm.astream_chat(messages)
        
        async for chunk in response_gen:
            if chunk.delta:
                print(chunk.delta, end="", flush=True)
                
    except Exception as e:
        print(f"\nCRASH LlamaIndex ASTREAM CHAT!!! Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_doctor())
