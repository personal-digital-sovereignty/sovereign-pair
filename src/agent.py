import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from duckduckgo_search import DDGS
from llama_index.core.tools import FunctionTool
from config import llm, embed_model

# 1. Configuração para o acesso local aos arquivos (RAG)
db = chromadb.PersistentClient(path="../data/chromadb")
chroma_collection = db.get_or_create_collection("sovereign_knowledge")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)

local_query_engine = index.as_query_engine(llm=llm)

local_tool = QueryEngineTool(
    query_engine=local_query_engine,
    metadata=ToolMetadata(
        name="arquivos_pessoais",
        description="Útil para busca de informações nos arquivos locais, PDFs, anotações em Markdown e documentações pessoais do usuário."
    ),
)

# 2. Configura a tool de busca na Internet
def search_web(query: str) -> str:
    """Busca informações atualizadas na internet."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=3)]
        return str(results)

web_tool = FunctionTool.from_defaults(fn=search_web)

# 3. Inicializar o Agente de Pair Programming. Sim, ele irá pensar e escolher qual ferramenta usar!
agent = ReActAgent.from_tools(
    [local_tool, web_tool], 
    llm=llm, 
    verbose=True # Deixe True para ver a IA "pensando" e escolhendo qual ferramenta usar
)

