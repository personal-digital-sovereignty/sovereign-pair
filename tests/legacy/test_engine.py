import asyncio
import sys

sys.path.append("/app")
from src.engine_builder import build_chat_engine

async def main():
    print("Iniciando depuração de Engine (No-Stream)...")
    engine = build_chat_engine("ollama", "qwen2.5")
    
    print("Enviando prompt síncrono para o LLM...")
    response_obj = await engine.achat("What is 1+1? Answer in 1 word.")
    
    print("\n\n==== DEBUG RESPONSE ====")
    print("RAW STR:", str(response_obj))
    print("RAW REPR:", repr(response_obj))
    print("TYPE:", type(response_obj))
    print("DIR:", [attr for attr in dir(response_obj) if not attr.startswith('_')])
    
    for attr in ['response', 'message', 'text', 'content', 'source_nodes']:
        val = getattr(response_obj, attr, "MISSING")
        print(f"ATTR ({attr}): {val} (Type: {type(val)})")
        if hasattr(val, 'content'):
            print(f"  -> {attr}.content: {val.content}")

if __name__ == "__main__":
    asyncio.run(main())
