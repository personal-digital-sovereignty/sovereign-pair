import logging
import chromadb
from llama_index.core.schema import TextNode
from llama_index.core.retrievers.fusion_retriever import QueryFusionRetriever, FUSION_MODES
from llama_index.core.chat_engine import ContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from custom_retrievers import CustomBM25Retriever
from config import CHROMA_DIR, CHROMA_COLLECTION_NAME, llm, OWNER_NAME, SOVEREIGN_NAME, ASSISTANT_PERSONA, \
     OWNER_NICKNAME, OCCUPATION, ABOUT_USER, LANGUAGE, GEOLOCATION
from datetime import datetime

logger = logging.getLogger(__name__)

from llama_index.core.llms import ChatMessage, MessageRole

def build_chat_engine(index, history=None):
    """
    Constrói a instância do ContextChatEngine configurada com Hybrid Search
    (Vector + BM25) para recuperação precisa de documentos.
    Recebe opcionalmente o `history` (Lista de Dicts) para resgatar
    memória de curto/longo prazo do banco SQLite.
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

    # Memory Buffer (Preparar histórico persistente se fornecido)
    chat_history = []
    if history:
        for msg in history:
            role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
            chat_history.append(ChatMessage(role=role, content=msg["content"]))
            
    memory = ChatMemoryBuffer.from_defaults(chat_history=chat_history, token_limit=16000)

    # Verifica se a Persona foi alterada nas Configurações Livres do Frontend (Fase 9)
    from src.api.database import SessionLocal
    from src.api.models import SystemSettings
    try:
        db = SessionLocal()
        setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "system_prompt").first()
        active_persona = setting.setting_value if setting and setting.setting_value else ASSISTANT_PERSONA
        
        formality_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "formality").first()
        formality = formality_setting.setting_value if formality_setting else "neutral"
        
        nickname_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "nickname").first()
        nickname = nickname_setting.setting_value if nickname_setting and nickname_setting.setting_value.strip() else OWNER_NICKNAME
        
        occupation_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "occupation").first()
        occupation = occupation_setting.setting_value if occupation_setting else OCCUPATION
        
        about_user_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "about_user").first()
        about_user = about_user_setting.setting_value if about_user_setting else ABOUT_USER
        
        language_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "language").first()
        language = language_setting.setting_value if language_setting and language_setting.setting_value.strip() else LANGUAGE

        geolocation_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == "geolocation").first()
        geolocation = geolocation_setting.setting_value if geolocation_setting and geolocation_setting.setting_value.strip() else GEOLOCATION
        
        db.close()
    except Exception as e:
        logger.error(f"   ❌ Erro ao ler configs dinâmicas: {e}")
        active_persona = ASSISTANT_PERSONA
        formality = "neutral"
        nickname = OWNER_NICKNAME
        occupation = OCCUPATION
        about_user = ABOUT_USER
        language = LANGUAGE
        geolocation = GEOLOCATION
        

    gender_instruction = ""
    if formality == "feminine":
        gender_instruction = "\nREGRA DE TRATAMENTO: Sempre responda se referindo a si mesma no gênero feminino e seja cordial.\n"
    elif formality == "masculine":
        gender_instruction = "\nREGRA DE TRATAMENTO: Sempre responda se referindo a si mesmo no gênero masculino e evite excesso de formalidade.\n"

    user_context_block = ""
    if occupation or about_user or geolocation:
        user_context_block += "\n[CONTEXTO AVANÇADO SOBRE O USUÁRIO ACHADO NA MEMÓRIA]:\n"
        if occupation:
            user_context_block += f"- Ocupação / Especialidade: {occupation}\n"
        if about_user:
            user_context_block += f"- Preferências / Sobre o usuário: {about_user}\n"
        if geolocation:
            user_context_block += f"- Geolocalização Base do Usuário: {geolocation}\n"

    # Criar Chat Engine com Retriever Híbrido
    chat_engine = ContextChatEngine.from_defaults(
        retriever=hybrid_retriever,
        llm=llm,
        memory=memory, # Memória bufferizada re-hidratada
        system_prompt=(
            f"Você é a inteligência artificial {SOVEREIGN_NAME}, atuando como assistente pessoal corporativa e soberana. "
            f"Sua persona de comportamento e alinhamento é estritamente definida como: {active_persona}. "
            f"O usuário com quem você está conversando e de quem deve receber ordens se chama {nickname}. "
            f"O idioma PRINCIPAL no qual ESCRITAMENTE OBRIGATÓRIO responder (mesmo para traduzir o RAG) é: {language}. "
            f"Hoje é: {datetime.now().strftime('%d/%m/%Y, %H:%M')}. "
            "Sua principal fonte de verdade são os fragmentos de contexto fornecidos pelo sistema (RAG). "
            "Sempre que o usuário perguntar sobre projetos, arquivos locais ou informações específicas, "
            "OBRIGATORIAMENTE USE O CONTEXTO fornecido ou o Histórico do Chat.\n"
            f"{user_context_block}"
            f"{gender_instruction}"
            "REGRAS CRÍTICAS DE CONDUTA:\n"
            "1. Seja SEMPRE direto, transparente, realista e analítico. Pode haver um leve senso de humor e empatia respeitosa (NÃO seja ácido ou sarcástico).\n"
            "2. NUNCA peça desculpas ou use frases evasivas do tipo 'Infelizmente, não tenho acesso a dados'. Aja com total confiança e extraia a tabela ou dado solicitado sem reclamar.\n"
            "3. NUNCA preveja ou invente tabelas ou placares esportivos/financeiros inexistentes. Se os dados foram capturados pelo RAG ou Web Search, construa uma MARAVILHOSA Tabela Markdown.\n"
            "4. Pare de agir como uma inteligência artificial corporativa assustada: aja naturalmente, exiba tabelas em Markdown e cite fontes de forma elegante."
        ),
    )
    
    return chat_engine
