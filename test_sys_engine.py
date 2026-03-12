import asyncio
import os
import sys

# Add sovereign to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.engine_builder import build_system_chat_engine

async def run():
    print("Iniciando System Chat Engine...", flush=True)
    engine = build_system_chat_engine(provider="ollama", model_name="llama3.2", api_keys={})
    print("Engine construído:", engine, flush=True)
    if engine:
        try:
            res = await engine.astream_chat("/sys Arquitetura")
            async for t in res.async_response_gen():
                pass
            print("OK!")
        except Exception as e:
            print("RUN ERROR:", repr(e))
    else:
        print("Engine None retornado")

if __name__ == "__main__":
    asyncio.run(run())
