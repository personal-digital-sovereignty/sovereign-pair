import asyncio
from src.core.the_nurse import TheNurse

async def run():
    print("Iniciando The Nurse...")
    nurse = TheNurse("ollama", "llama3.2:latest")
    res = await nurse.evaluate_intent("Extraia a seguinte lista em uma tabela Markdown limpa: Maçã vermelha, Banana roxa, Uva verde.")
    print(res)

if __name__ == "__main__":
    asyncio.run(run())
