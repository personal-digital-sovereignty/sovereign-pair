import asyncio
import logging
from src.core.the_dad import TheDadWorker
from src.config import ensure_directories

logging.basicConfig(level=logging.INFO)
ensure_directories()

async def test_dad():
    worker = TheDadWorker(check_interval_seconds=5)
    print("Iniciando o Pai...")
    await worker.process_pending_documents()
    print("Finalizou um ciclo do Pai.")

if __name__ == "__main__":
    asyncio.run(test_dad())
