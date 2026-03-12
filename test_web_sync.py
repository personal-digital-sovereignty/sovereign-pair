import asyncio
from src.llm_factory import get_llm
from src.web_search import search_web
from llama_index.core.llms import ChatMessage, MessageRole

async def run():
    print("1. Scraping...")
    web_result = await asyncio.to_thread(search_web, "Previsao tempo amanhã Jandira", None)
    print(f"2. Scraped {len(web_result)} bytes. Invocando LLM Llama3.2...")
    
    llm = get_llm("ollama", "llama3.2")
    
    sys_prompt = "Você é um assistente RAG de Pesquisa Web. Resuma a resposta."
    sys_msg = ChatMessage(role=MessageRole.SYSTEM, content=sys_prompt)
    context_msg = ChatMessage(role=MessageRole.USER, content=f"Resultados Web:\n{web_result}\n\nPergunta: Previsao tempo amanhã Jandira")
    
    msgs = [sys_msg, context_msg]
    
    try:
        gen = await llm.astream_chat(msgs)
        count = 0
        async for t in gen:
            print(t.delta, end="", flush=True)
            count += 1
        print(f"\n[Fim] Tokens gerados: {count}")
    except Exception as e:
        print("\n!!! ERROR !!!")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
