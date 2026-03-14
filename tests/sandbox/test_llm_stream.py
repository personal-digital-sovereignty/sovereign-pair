import asyncio
from src.llm_factory import get_llm
from llama_index.core.llms import ChatMessage, MessageRole

async def run():
    llm = get_llm("ollama", "llama3.2")
    msgs = [
        ChatMessage(role=MessageRole.SYSTEM, content="Você é um RAG avançado. Resuma a pesquisa web em 1 linha."),
        ChatMessage(role=MessageRole.USER, content="DuckDuckGo: Previsão do tempo: sol e nuvens. Qual o tempo?")
    ]
    print("Iniciando Ollama astream...")
    try:
        gen = await llm.astream_chat(msgs)
        async for t in gen:
            print(t.delta, end="")
        print("\nPronto.")
    except Exception:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
