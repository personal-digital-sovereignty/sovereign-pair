import logging
import chromadb
from llama_index.core.schema import TextNode
from llama_index.core.retrievers.fusion_retriever import QueryFusionRetriever, FUSION_MODES
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from custom_retrievers import CustomBM25Retriever
from config import CHROMA_DIR, CHROMA_COLLECTION_NAME, llm, USER_NAME
from datetime import datetime

logger = logging.getLogger(__name__)

def build_chat_engine(index):
    """
    Constrói a instância do ContextChatEngine configurada com Hybrid Search
    (Vector + BM25) para recuperação precisa de documentos.
    """
    logger.info("⚙️  Configurando Busca Híbrida (Vector + BM25)...")
    
    # 1. Vector Retriever (Semântico) - Top-K conservador para performance
    vector_retriever = index.as_retriever(similarity_top_k=5)
    
    # 2. BM25 Retriever (Palavras-chave / Datas exatas)
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
        similarity_top_k=3,  # Top-3 final para manter contexto leve no LLM
        mode=FUSION_MODES.RECIPROCAL_RANK,
    )
    logger.info("   ✓ Hybrid Retriever configurado.")

    # Criar Chat Engine com Retriever Híbrido
    chat_engine = ContextChatEngine.from_defaults(
        retriever=hybrid_retriever,
        llm=llm,
        memory=ChatMemoryBuffer.from_defaults(token_limit=16000), # Memória bufferizada
        system_prompt=(
            f"Você é o Sovereign Pair, um assistente pessoal de {USER_NAME}. "
            f"Hoje é: {datetime.now().strftime('%d/%m/%Y, %H:%M')}. "
            "Sua principal fonte de verdade são os fragmentos de contexto fornecidos pelo sistema (RAG). "
            "Sempre que o usuário perguntar sobre projetos, arquivos locais ou informações específicas, "
            "OBRIGATORIAMENTE USE O CONTEXTO. Se a resposta sobre os dados não estiver no contexto, diga: 'Não encontrei essa informação nos seus arquivos'. "
            "Para saudações e perguntas de conversação geral ou de datas atuais, responda com sua inteligência e de acordo com as informações de hoje fornecidas nesta instrução."
        ),
    )
    
    return chat_engine
