import logging
import chromadb
from llama_index.core.schema import TextNode
from llama_index.core.retrievers.fusion_retriever import QueryFusionRetriever, FUSION_MODES
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from src.custom_retrievers import CustomBM25Retriever
from src.config import CHROMA_DIR, CHROMA_COLLECTION_NAME, llm as default_llm, SOVEREIGN_NAME, ASSISTANT_PERSONA, \
     OWNER_NICKNAME, OCCUPATION, ABOUT_USER, LANGUAGE, GEOLOCATION, REQUEST_TIMEOUT, \
     OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, GEMINI_API_KEY
from datetime import datetime

logger = logging.getLogger(__name__)

from llama_index.core.llms import ChatMessage, MessageRole  # noqa: E402

def resolve_dynamic_llm(provider: str, model_name: str, fallback_llm, api_keys: dict = None):
    if not provider or not model_name:
        return fallback_llm
        
    api_keys = api_keys or {}
    p = provider.lower().strip()
    try:
        if p == "openai":
            from llama_index.llms.openai import OpenAI
            key = api_keys.get("openai_api_key") or OPENAI_API_KEY
            return OpenAI(model=model_name, api_key=key, request_timeout=REQUEST_TIMEOUT)
        elif p == "anthropic":
            from llama_index.llms.anthropic import Anthropic
            key = api_keys.get("anthropic_api_key") or ANTHROPIC_API_KEY
            return Anthropic(model=model_name, api_key=key, timeout=REQUEST_TIMEOUT)
        elif p == "groq":
            from llama_index.llms.groq import Groq
            key = api_keys.get("groq_api_key") or GROQ_API_KEY
            return Groq(model=model_name, api_key=key, request_timeout=REQUEST_TIMEOUT)
        elif p == "gemini":
            from llama_index.llms.gemini import Gemini
            key = api_keys.get("gemini_api_key") or GEMINI_API_KEY
            return Gemini(model=model_name, api_key=key)
        elif p == "ollama":
            from llama_index.llms.ollama import Ollama
            from src.config import OLLAMA_BASE_URL
            custom_url = api_keys.get("custom_ollama_url")
            url_to_use = custom_url if custom_url and custom_url.strip() else OLLAMA_BASE_URL
            return Ollama(
                model=model_name, 
                base_url=url_to_use, 
                request_timeout=REQUEST_TIMEOUT, 
                context_window=4096, 
                client_kwargs={"timeout": REQUEST_TIMEOUT},
                additional_kwargs={"num_ctx": 4096}
            )
    except ImportError as e:
        logger.error(f"Failed to load provider {p}: {e} - pip install llama-index-llms-{p} may be required.")
        
    return fallback_llm

def build_chat_engine(index, history=None, provider=None, model_name=None, tenant_id=None):
    """
    Constrói a instância do ContextChatEngine configurada com Hybrid Search
    (Vector + BM25) para recuperação precisa de documentos.
    Recebe opcionalmente o `history` (Lista de Dicts) para resgatar
    memória de curto/longo prazo do banco SQLite.
    """
    logger.info("⚙️  Configurando Busca Híbrida (Vector + BM25)...")
    
    # 1. Vector Retriever (Semântico) - Top-K conservador para performance
    filters = None
    if tenant_id:
        from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
        filters = MetadataFilters(filters=[ExactMatchFilter(key="tenant_id", value=tenant_id)])
        logger.info(f"   🔍 Filtro de Inquecilino aplicado: {tenant_id}")
        
    vector_retriever = index.as_retriever(similarity_top_k=5, filters=filters)
    
    # 2. BM25 Retriever (Palavras-chave / Datas exatas)
    logger.info("   📊 Carregando nós para índice BM25...")
    nodes = []
    try:
        from src.config import get_chroma_client
        db_client = get_chroma_client()
        collection = db_client.get_collection(CHROMA_COLLECTION_NAME)
        where_clause = {"tenant_id": tenant_id} if tenant_id else None
        result = collection.get(where=where_clause)
        
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
        all_settings = db.query(SystemSettings).all()
        settings_dict = {s.setting_key: s.setting_value for s in all_settings if s.setting_value}
        
        active_persona = settings_dict.get("system_prompt", ASSISTANT_PERSONA)
        formality = settings_dict.get("formality", "neutral")
        
        nickname = settings_dict.get("nickname", OWNER_NICKNAME)
        nickname = nickname if nickname.strip() else OWNER_NICKNAME
        
        ai_name = settings_dict.get("ai_name", SOVEREIGN_NAME)
        ai_name = ai_name if ai_name.strip() else SOVEREIGN_NAME
        
        occupation = settings_dict.get("occupation", OCCUPATION)
        about_user = settings_dict.get("about_user", ABOUT_USER)
        
        language = settings_dict.get("language", LANGUAGE)
        language = language if language.strip() else LANGUAGE
        
        geolocation = settings_dict.get("geolocation", GEOLOCATION)
        geolocation = geolocation if geolocation.strip() else GEOLOCATION
        
        db_provider = settings_dict.get("llm_provider", None)
        db_provider = db_provider if db_provider and db_provider.strip() else None
        
        db_model = settings_dict.get("llm_model", None)
        db_model = db_model if db_model and db_model.strip() else None
        
        api_keys = {
            "openai_api_key": settings_dict.get("openai_api_key", ""),
            "anthropic_api_key": settings_dict.get("anthropic_api_key", ""),
            "gemini_api_key": settings_dict.get("gemini_api_key", ""),
            "custom_ollama_url": settings_dict.get("custom_ollama_url", "")
        }
        
    except Exception as e:
        logger.error(f"   ❌ Erro ao ler configs dinâmicas: {e}")
        active_persona = ASSISTANT_PERSONA
        formality = "neutral"
        nickname = OWNER_NICKNAME
        ai_name = SOVEREIGN_NAME
        occupation = OCCUPATION
        about_user = ABOUT_USER
        language = LANGUAGE
        geolocation = GEOLOCATION
        db_provider = None
        db_model = None
        api_keys = {}
    finally:
        try:
            db.close()
        except:
            pass

        

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

    # Resolve o LLM Ativo (Nuvem ou Local) com base no Request ou no Banco de Dados
    active_provider = provider or db_provider
    active_model = model_name or db_model
    active_llm = resolve_dynamic_llm(active_provider, active_model, default_llm, api_keys)

    # Log da Mídia utilizada (Para telemetria no terminal FastAPI)
    provider_log = provider or "Ollama (Default)"
    model_log = model_name or getattr(active_llm, "model", "Local")
    logger.info(f"   🧠 Engine inicializada via {provider_log.upper()} com modelo {model_log}")

    # Criar Chat Engine com Retriever Híbrido e Condensador Explícito
    chat_engine = CondensePlusContextChatEngine.from_defaults(
        retriever=hybrid_retriever,
        llm=active_llm,
        memory=memory, # Memória bufferizada re-hidratada
        system_prompt=(
            f"Você é a inteligência artificial {ai_name} (da família Sovereign Pair), atuando como assistente pessoal corporativa e soberana. "
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

def build_system_chat_engine(provider=None, model_name=None):
    """
    Constrói a instância do ChatEngine específica para o Meta-RAG (System Knowledge).
    Conecta-se à coleção isolada que contém o próprio código fonte do Sovereign.
    """
    logger.info("⚙️  Configurando System Chat Engine (Meta-RAG)...")
    from src.config import CHROMA_SYSTEM_COLLECTION_NAME, get_chroma_client
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.core import VectorStoreIndex
    
    try:
        db = get_chroma_client()
        chroma_collection = db.get_collection(CHROMA_SYSTEM_COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(vector_store)
        
        # IGNORAR o modelo vindo do Frontend para a aba Sistema (Meta-RAG)
        # OMeta-RAG deve SEMPRE usar um modelo enxuto e rápido para não dar OOM (Out Of Memory)
        if provider == "ollama" or not provider:
            sys_provider = "ollama"
            sys_model = "llama3.2"
        else:
            sys_provider = provider
            sys_model = model_name
            
        active_llm = resolve_dynamic_llm(sys_provider, sys_model, default_llm)
        
        chat_engine = index.as_chat_engine(
            llm=active_llm,
            chat_mode="condense_plus_context",
            system_prompt=(
                "Você é o Meta-RAG do Sovereign Pair. Seu objetivo é ajudar o usuário a entender as "
                "configurações, a arquitetura e o código fonte do sistema. Responda apenas com base no "
                "conhecimento dos arquivos injetados no seu banco vetorial. Seja direto e escreva em "
                "Português do Brasil."
            )
        )
        return chat_engine
    except Exception as e:
        logger.error(f"❌ Erro ao construir System Chat Engine: {e}")
        return None
