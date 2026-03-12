import asyncio
from src.web_search import search_web

async def run():
    print("Iniciando Web Search Mock...", flush=True)
    try:
        res = await asyncio.to_thread(search_web, "Previsão do tempo em Jandira SP para 12/03/2026", None)
        print("Tamanho Result:", len(res))
        print("Sample:", res[:300])
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run())
