import asyncio
from src.core.the_nurse import TheNurse

async def run():
    print("Iniciando The Nurse Tactical Test...")
    nurse = TheNurse("ollama", "llama3.2:latest")
    
    intent_data = {
        "requires_doctor": False,
        "reason": "Direct request for code/markdown",
        "task_type": "extraction"
    }
    
    print("Executing Tactical Task...")
    stream = await nurse.execute_tactical_task("Faça uma tabela com 3 frutas", "Nenhum Contexto", intent_data)
    
    print("Reading Stream...")
    async for chunk in stream:
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(run())
