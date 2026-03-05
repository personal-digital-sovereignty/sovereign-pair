import asyncio
from llama_index.core.llms import ChatMessage
from src.engine_builder import resolve_dynamic_llm
from config import llm as default_llm

async def main():
    try:
        llm = resolve_dynamic_llm(None, None, default_llm)
        print("Got LLM:", type(llm))
        
        messages = [ChatMessage(role="user", content="Hello")]
        print("Calling astream_chat...")
        
        # Test if it returns an async generator synchronously
        result = llm.astream_chat(messages)
        print("Result without await:", type(result))
        
        import inspect
        if inspect.isasyncgen(result):
            print("It is an async generator!")
            async for token in result:
                break
        elif inspect.iscoroutine(result):
            print("It is a coroutine!")
            real_result = await result
            print("Result after await:", type(real_result))
            if inspect.isasyncgen(real_result):
                print("And real result is an async generator")
        else:
            print("Unknown type")
    except Exception as e:
        print("Error:", repr(e))

asyncio.run(main())
