import asyncio
import sys
from src.llm_factory import get_llm
from llama_index.core.llms import ChatMessage, MessageRole

async def run():
    print("1. Ligando Llama 3.2 Ollama via LlamaIndex...")
    llm = get_llm("ollama", "llama3.2")
    
    sys_prompt = "Você é um AI Soberano. Responda 1+1"
    sys_msg = ChatMessage(role=MessageRole.SYSTEM, content=sys_prompt)
    context_msg = ChatMessage(role=MessageRole.USER, content="Apenas responda o cálculo com confiança.")
    
    msgs = [sys_msg, context_msg]
    print("2. Gerando Tokens...")
    try:
        gen = await llm.astream_chat(msgs)
        cnt = 0
        async for t in gen:
            print(t.delta, end="", flush=True)
            cnt += 1
        print(f"\n[OK] {cnt} Tokens gerados.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run())
