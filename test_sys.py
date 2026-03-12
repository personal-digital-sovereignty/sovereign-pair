import asyncio
from src.api.database import SessionLocal
from src.api.routes import get_current_user

# Simular a carga do Meta-RAG localmente
from src.engine_builder import build_system_chat_engine
try:
    engine = build_system_chat_engine(provider="ollama", model_name="llama3.2", api_keys={})
    print("Engine inicializado:", type(engine))
    # Para rodar o astream
    async def run():
        res = await engine.astream_chat("Teste de sistema")
        async for t in res.async_response_gen():
            print(t, end="")
    asyncio.run(run())
except Exception as e:
    import traceback
    traceback.print_exc()

