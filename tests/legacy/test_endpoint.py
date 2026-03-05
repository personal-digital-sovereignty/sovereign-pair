import asyncio
import sys
sys.path.append('src')
from config import llm
from src.engine_builder import build_chat_engine
from llama_index.core import VectorStoreIndex

async def main():
    engine = build_chat_engine(VectorStoreIndex.from_documents([]))
    
    # Mock search web logic
    from src.web_search import search_web
    from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
    from datetime import datetime
    
    print("Executing web query block")
    web_args = "qual foi o resultado do jogo do SPFC ontem?"
    timelimit = None
    web_query = web_args
    
    web_result = await asyncio.to_thread(search_web, web_query, timelimit)
    print("Web result bytes:", len(web_result))
    
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # noqa: F841
    sys_prompt = "..."
    sys_msg = LlamaMsg(role=MessageRole.SYSTEM, content=sys_prompt)
    context_msg = LlamaMsg(role=MessageRole.USER, content=f"Resultados Web: {web_result}")
    
    history_msgs = engine._memory.get_all() if engine else []
    messages_to_send = [sys_msg] + history_msgs + [context_msg]
    
    print("Calling stream_chat")
    try:
        response_gen = await asyncio.to_thread(llm.stream_chat, messages_to_send)
        print("Generator got, starting loop")
        for token in response_gen:
            if token.delta:
                print(token.delta, end="")
        print("Done generator")
    except Exception as e:
        print(f"FAILED AT stream_chat!! {e}")

if __name__ == "__main__":
    asyncio.run(main())
