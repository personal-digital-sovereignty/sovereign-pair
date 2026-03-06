import asyncio
import os
import sys

sys.path.append("/app")
from src.engine_builder import build_chat_engine

async def main():
    engine = build_chat_engine("ollama", "qwen2.5")
    
    # Send message and await response
    response_obj = await engine.achat("Diga a palavra SUCESSO.")
    
    print("\n\n==== DEBUG RESPONSE ====")
    print("TYPE:", type(response_obj))
    print("DIR:", [attr for attr in dir(response_obj) if not attr.startswith('_')])
    
    # DUMP attrs
    for attr in ['response', 'message', 'text', 'content']:
        val = getattr(response_obj, attr, "MISSING")
        print(f"ATTR ({attr}): {val} (Type: {type(val)})")
        if hasattr(val, 'content'):
            print(f"  -> {attr}.content: {val.content}")

if __name__ == "__main__":
    asyncio.run(main())
