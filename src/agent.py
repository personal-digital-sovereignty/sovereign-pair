"""
Agente de Pair Programming Sovereign Pair.

Este módulo implementa um agente ReAct que pode escolher entre:
- Buscar informações nos arquivos locais (RAG)
- Buscar informações atualizadas na internet (DuckDuckGo)

NOTA: Atualizado para suportar LlamaIndex Workflows (v0.14+).
"""

import nest_asyncio
nest_asyncio.apply()

import logging
import sys
import asyncio
import warnings

# Suprimir avisos deprecados do Pydantic e renomeação do DDGS
warnings.filterwarnings("ignore", message=".*model_fields.*")
warnings.filterwarnings("ignore", message=".*__fields__.*")
warnings.filterwarnings("ignore", message=".*model_computed_fields.*")
warnings.filterwarnings("ignore", message=".*renamed to.*ddgs.*")  # Ignora aviso de rename do duckduckgo
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")

try:
    from pydantic.warnings import PydanticDeprecatedSince20, PydanticDeprecatedSince211
    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince211)
except ImportError:
    pass

import chromadb
from typing import Optional

from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.retrievers.fusion_retriever import FUSION_MODES
from llama_index.core.schema import TextNode
from custom_retrievers import CustomBM25Retriever
# from ddgs import DDGS
# from duckduckgo_search import DDGS

# Importar configurações centralizadas
from config import (
    CHROMA_DIR,
    CHROMA_COLLECTION_NAME,
    USER_NAME,
    AGENT_VERBOSE,
    INTERACTIVE_MODE,
    llm,
    embed_model,
    validate_ollama_connection,
    validate_ollama_models,
    LLM_MODEL,
)

# Configurar logger
logger = logging.getLogger(__name__)

# Configuração do Logger
if AGENT_VERBOSE:
    logging.getLogger().setLevel(logging.INFO)
    # Habilitar logs detalhados do LlamaIndex para debug de retrieval
    # logging.getLogger("llama_index").setLevel(logging.DEBUG)
    logging.getLogger("custom_retrievers").setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.WARNING)
def initialize_rag_tool() -> Optional[QueryEngineTool]:
    """
    Inicializa a ferramenta de busca em arquivos locais (RAG).
    
    Returns:
        QueryEngineTool: Ferramenta configurada ou None em caso de erro
    """
    try:
        logger.info("📂 Inicializando ferramenta de busca local (RAG)...")
        
        # Verificar se o ChromaDB existe
        if not CHROMA_DIR.exists():
            logger.error(f"❌ Diretório ChromaDB não encontrado: {CHROMA_DIR}")
            logger.error("   Execute primeiro: python ingest.py")
            return None
        
        # Conectar ao ChromaDB
        db = chromadb.PersistentClient(path=str(CHROMA_DIR))
        chroma_collection = db.get_or_create_collection(CHROMA_COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        # Criar índice a partir do vector store existente
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=embed_model
        )
        
        # Criar query engine
        # Aumentamos similarity_top_k para 10 para garantir mais contexto ao LLM
        local_query_engine = index.as_query_engine(llm=llm, similarity_top_k=10)
        
        # Criar ferramenta
        local_tool = QueryEngineTool(
            query_engine=local_query_engine,
            metadata=ToolMetadata(
                name="arquivos_pessoais",
                description=(
                    "FERRAMENTA MESTRA: Contém TODO o conhecimento sobre o usuário (projetos, blogs, anotações). "
                    "Use-a OBRIGATORIAMENTE para perguntas que contenham 'meus arquivos', 'meu blog', 'meu projeto' ou nomes específicos. "
                    "Se o usuário pedir 'sobre Uninove', 'sobre ArchLinux', procure AQUI primeiro. "
                    "Nunca assuma que a resposta não existe sem verificar esta ferramenta."
                ),
            ),
        )
        
        logger.info("   ✓ Ferramenta RAG inicializada com sucesso")
        return index, local_tool
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar ferramenta RAG: {e}")
        logger.exception("Detalhes:")
        return None


# def search_web(query: str) -> str:
#     """
#     Busca informações atualizadas na internet usando DuckDuckGo.
#     
#     Args:
#         query: Consulta de busca
#         
#     Returns:
#         str: Resultados formatados ou mensagem de erro
#     """
#     try:
#         logger.debug(f"🌐 Buscando na web: {query}")
#         
#         # Suprimir warnings durante a execução da busca também
#         with warnings.catch_warnings():
#             warnings.simplefilter("ignore")
#             with DDGS() as ddgs:
#                 results = list(ddgs.text(query, max_results=MAX_WEB_SEARCH_RESULTS))
#         
#         if not results:
#             return "Nenhum resultado encontrado na busca web."
#         
#         # Formatar resultados de forma mais legível
#         formatted_results = []
#         for i, result in enumerate(results, 1):
#             formatted_results.append(
#                 f"{i}. {result.get('title', 'Sem título')}\n"
#                 f"   {result.get('body', 'Sem descrição')}\n"
#                 f"   URL: {result.get('href', 'N/A')}"
#             )
#         
#         return "\n\n".join(formatted_results)
#         
#     except Exception as e:
#         logger.error(f"❌ Erro na busca web: {e}")
#         return f"Erro ao buscar na internet: {str(e)}"


# def initialize_web_tool() -> FunctionTool:
#     """
#     Inicializa a ferramenta de busca na internet.
#     
#     Returns:
#         FunctionTool: Ferramenta de busca web configurada
#     """
#     logger.info("🌐 Inicializando ferramenta de busca web...")
#     
#     web_tool = FunctionTool.from_defaults(
#         fn=search_web,
#         name="busca_internet",
#         description=(
#             "Útil APENAS para fatos globais recentes, notícias ou tecnologias gerais "
#             "que NÃO são sobre a vida pessoal do usuário. "
#             "NÃO use esta ferramenta se o usuário perguntar 'o que eu acho', 'meu projeto' ou 'meu arquivo'."
#         ),
#     )
#     
#     logger.info("   ✓ Ferramenta de busca web inicializada")
#     return web_tool


def print_welcome_message():
    """Exibe mensagem de boas-vindas."""
    print("\n" + "=" * 70)
    print("🤖 SOVEREIGN PAIR - Agente de Pair Programming")
    print("=" * 70)
    print(f"\nOlá, {USER_NAME}! 👋")
    print("\nEu posso ajudar você com:")
    print("  • Buscar informações nos seus arquivos locais")
    print("  • Buscar informações atualizadas na internet")
    print("  • Responder perguntas e auxiliar no desenvolvimento")
    print("\nComandos especiais:")
    print("  /help   - Mostrar esta mensagem")
    print("  /clear  - Limpar histórico de conversação")
    print("  sair    - Encerrar o programa")
    print("\n" + "=" * 70 + "\n")


def print_help():
    """Exibe mensagem de ajuda."""
    print("\n" + "=" * 70)
    print("📖 AJUDA - Sovereign Pair")
    print("=" * 70)
    print("\nComandos disponíveis:")
    print("  /help   - Mostrar esta mensagem de ajuda")
    print("  /clear  - Limpar o histórico de conversação")
    print("  sair    - Encerrar o programa")
    print("\nDicas:")
    print("  • Seja específico nas suas perguntas")
    print("  • O agente escolherá automaticamente entre busca local ou web")
    print("  • Para forçar busca local, mencione 'nos meus arquivos'")
    print("  • Para forçar busca web, mencione 'na internet' ou 'atualizado'")
    print("=" * 70 + "\n")


async def main():
    """Função principal do agente (Assíncrona)."""
    try:
        # Validar conexão com Ollama
        logger.info("🔍 Validando conexão com Ollama...")
        if not validate_ollama_connection():
            print("\n❌ Erro: Não foi possível conectar ao Ollama.")
            print("   Certifique-se de que o Ollama está rodando:")
            print("   $ ollama serve")
            sys.exit(1)
        
        # Validar modelos
        logger.info("🔍 Validando modelos Ollama...")
        models_ok, missing_models = validate_ollama_models()
        if not models_ok:
            print(f"\n❌ Erro: Modelos faltando no Ollama: {', '.join(missing_models)}")
            print("   Baixe os modelos necessários:")
            for model in missing_models:
                print(f"   $ ollama pull {model}")
            sys.exit(1)
        
        logger.info("   ✓ Ollama configurado corretamente")
        
        # Inicializar ferramentas
        # Note: initialize_rag_tool pode demorar, mas é síncrono.
        # Em produção, poderíamos executar em thread separada, mas ok por agora.
        index, local_tool = initialize_rag_tool()
        # web_tool = initialize_web_tool()
        
        # Verificar se pelo menos uma ferramenta está disponível
        tools = []
        if local_tool:
            tools.append(local_tool)
        # if web_tool:
        #     tools.append(web_tool)
        
        if not tools:
            print("\n❌ Erro: Nenhuma ferramenta disponível.")
            print("   Execute 'python ingest.py' para indexar documentos.")
            sys.exit(1)
        
        # MODO DIRETO (Fast RAG) - Sem ReAct Loop
        # Para modelos menores (1b/3b) e uso apenas local, o ChatEngine é muito mais rápido e confiável.
        # Ele faz: Recuperação -> Prompt -> Resposta (1 chamada LLM apenas)
        
        logger.info("⚡ Iniciando modo RAG Direto (Chat Engine)...")
        logger.info("   (Otimizado para velocidade e modelos locais)")
        
        # Criar Chat Engine com modo "context" (RAG padrão)
        # O system_prompt força a personalidade e regras
        # --- CONFIGURAÇÃO HÍBRIDA (Hybrid Search) ---
        logger.info("⚙️  Configurando Busca Híbrida (Vector + BM25)...")
        
        # 1. Vector Retriever (Semântico) - Top-K conservador para performance
        vector_retriever = index.as_retriever(similarity_top_k=5)
        
        # 2. BM25 Retriever (Palavras-chave / Datas exatas)
        # Carrega nodes diretamente do ChromaDB (docstore pode estar vazio ao carregar do disco)
        logger.info("   📊 Carregando nós para índice BM25...")
        nodes = []
        try:
            db_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            collection = db_client.get_collection(CHROMA_COLLECTION_NAME)
            result = collection.get()
            
            if result and result['documents']:
                ids = result['ids']
                texts = result['documents']
                metadatas = result['metadatas']
                
                for i, text in enumerate(texts):
                    node_metadata = metadatas[i] if metadatas else {}
                    node = TextNode(
                        text=text,
                        id_=ids[i],
                        metadata=node_metadata
                    )
                    nodes.append(node)
                logger.info(f"   ✓ {len(nodes)} nós carregados do ChromaDB.")
            else:
                logger.warning("   ⚠️  Nenhum documento encontrado no ChromaDB para BM25.")
                
        except Exception as e:
            logger.error(f"   ❌ Erro ao carregar nós do ChromaDB para BM25: {e}")

        if not nodes:
            logger.warning("   ⚠️  Índice BM25 iniciará vazio (Hybrid Search prejudicado).")

        bm25_retriever = CustomBM25Retriever(nodes=nodes, similarity_top_k=5)
        
        # 3. Fusion Retriever (RRF - Reciprocal Rank Fusion)
        hybrid_retriever = QueryFusionRetriever(
            [vector_retriever, bm25_retriever],
            num_queries=1,
            use_async=False,
            similarity_top_k=3,  # Top-3 final para manter contexto leve no LLM local
            mode=FUSION_MODES.RECIPROCAL_RANK,
        )
        logger.info("   ✓ Hybrid Retriever configurado.")

        # Criar Chat Engine com Retriever Híbrido
        # Usamos ContextChatEngine diretamente para injetar o retriever personalizado
        chat_engine = ContextChatEngine.from_defaults(
            retriever=hybrid_retriever,
            llm=llm,
            memory=ChatMemoryBuffer.from_defaults(token_limit=16000), # Memória bufferizada
            system_prompt=(
                f"Você é o Sovereign Pair, um assistente pessoal de {USER_NAME}. "
                "Sua ÚNICA fonte de verdade são os fragmentos de contexto fornecidos pelo sistema (RAG). "
                "Você DEVE ignorar seu conhecimento prévio se ele contradisser ou não estiver no contexto. "
                "Sempre que o usuário perguntar sobre 'meu projeto', 'minha anotação', 'meu blog' ou assuntos específicos "
                "como 'Uninove', 'ArchLinux', 'Jandirense' ou DATAS específicas, OBRIGATORIAMENTE USE O CONTEXTO FORNECIDO. "
                "Se a resposta não estiver no contexto, DIGA EXPLICITAMENTE: 'Não encontrei essa informação nos seus arquivos'. "
                "Não invente. Não use conhecimento geral a menos que solicitado. Seja direto e técnico."
            ),
        )
        
        print_welcome_message()
        
        print(f"\n💡 Dica: Modo Turbo Ativado! (Usando {LLM_MODEL})")
        print("   Pergunte sobre seus arquivos. Digite 'sair' para encerrar.\n")
        
        while True:
            try:
                prompt = input(f"\n{USER_NAME} > ").strip()
                if not prompt:
                    continue
                
                if prompt.lower() in ['sair', 'exit', 'quit']:
                    print(f"\n👋 Até logo, {USER_NAME}!")
                    break
                
                if prompt == '/help':
                    print_welcome_message()
                    continue
                
                if prompt == '/clear':
                    print("\n🧹 Limpando histórico local...")
                    chat_engine.reset() # Resetar memória do chat engine se suportado
                    continue

                # Processar pergunta (Stream para velocidade percebida)
                # Gerar resposta (Streaming para evitar timeout visual e dar feedback imediato)
                streaming_response = chat_engine.stream_chat(prompt)
                
                print("Sovereign IA > ", end="", flush=True)
                full_response = ""
                for token in streaming_response.response_gen:
                    print(token, end="", flush=True)
                    full_response += token
                print("\n")
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Até logo, {USER_NAME}!")
                break
            
            except Exception as e:
                logger.error(f"❌ Erro ao processar pergunta: {e}")
                print(f"\n❌ Erro: {e}")
                print("Tente novamente ou digite '/help' para ajuda.\n")
        
    except KeyboardInterrupt:
        logger.info("\n\n👋 Encerrando o programa...")
        sys.exit(0)
    except Exception as e:
        logger.exception("❌ Erro fatal não tratado:")
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n👋 Até logo, {USER_NAME}!")
        sys.exit(0)
    except asyncio.CancelledError:
        print(f"\n\n👋 Até logo, {USER_NAME}!")
        sys.exit(0)