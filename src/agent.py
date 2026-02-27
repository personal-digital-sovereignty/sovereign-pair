"""
Agente de Pair Programming Sovereign Pair.

Este módulo implementa um agente ReAct que pode escolher entre:
- Buscar informações nos arquivos locais (RAG)
- Buscar informações atualizadas na internet (DuckDuckGo)

NOTA: Atualizado para suportar LlamaIndex Workflows (v0.14+).
"""

# nest_asyncio movido para __main__ para evitar conflito com uvicorn
import logging
import sys
import asyncio
import warnings
import subprocess
import re

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

import chromadb  # noqa: E402
from typing import Optional  # noqa: E402

from llama_index.core import VectorStoreIndex  # noqa: E402
from llama_index.vector_stores.chroma import ChromaVectorStore  # noqa: E402
from llama_index.core.tools import QueryEngineTool, ToolMetadata  # noqa: E402

from config import (  # noqa: E402
    CHROMA_DIR,
    CHROMA_COLLECTION_NAME,
    OWNER_NAME,
    AGENT_VERBOSE,
    llm,
    embed_model,
    validate_ollama_connection,
    validate_ollama_models
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


from web_search import search_web  # noqa: E402
def print_welcome_message():
    """Exibe mensagem de boas-vindas."""
    print("\n" + "=" * 70)
    print("🤖 SOVEREIGN PAIR - Agente de Pair Programming")
    print("=" * 70)
    print(f"\nOlá, {OWNER_NAME}! 👋")
    print("\nEu posso ajudar você com:")
    print("  • Buscar informações nos seus arquivos locais")
    print("  • Buscar informações atualizadas na internet")
    print("  • Responder perguntas e auxiliar no desenvolvimento")
    print("\nComandos especiais:")
    print("  /help          - Mostrar esta mensagem")
    print("  /clear         - Limpar histórico de conversação")
    print("  /web <query>   - Buscar na internet (DuckDuckGo)")
    print("  sair           - Encerrar o programa")
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
            print(f"\n⚠️  Modelos faltando no Ollama: {', '.join(missing_models)}")
            print("   Iniciando download automático (isso pode demorar minutos ou horas dependendo da sua conexão)...")
            for model in missing_models:
                print(f"   Baixando {model}...")
                try:
                    subprocess.run(["ollama", "pull", model], check=True)
                    print(f"   ✓ {model} baixado com sucesso!")
                except FileNotFoundError:
                    print("\n❌ Erro: O comando 'ollama' não foi encontrado no seu sistema.")
                    print("   Por favor, instale o Ollama em https://ollama.com/")
                    sys.exit(1)
                except subprocess.CalledProcessError:
                    print(f"\n❌ Erro ao baixar o modelo {model}.")
                    print(f"   Por favor, rode manualmente: ollama pull {model}")
                    sys.exit(1)
            print("   ✓ Todos os modelos prontos!")
        
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
        from engine_builder import build_chat_engine
        chat_engine = build_chat_engine(index)
        
        print_welcome_message()
        
        model_name = getattr(chat_engine.llm, "model", "Motor Desconhecido")
        
        print(f"\n💡 Dica: Modo Turbo Ativado! (Usando {model_name})")
        print("   Pergunte sobre seus arquivos. Digite 'sair' para encerrar.\n")
        
        while True:
            try:
                prompt = input(f"\n{OWNER_NAME} > ").strip()
                if not prompt:
                    continue
                
                if prompt.lower() in ['sair', 'exit', 'quit']:
                    print(f"\n👋 Até logo, {OWNER_NAME}!")
                    break
                
                if prompt == '/help':
                    print_welcome_message()
                    continue
                
                if prompt == '/clear':
                    print("\n🧹 Limpando histórico local...")
                    chat_engine.reset()
                    continue
                
                if prompt.startswith('/web'):
                    web_args = prompt[4:].strip()
                    # Parsear filtro temporal com regex para lidar com múltiplos espaços: /web -d query
                    timelimit = None
                    match = re.match(r'^(-[dwmy])\s+(.*)', web_args)
                    if match:
                        timelimit = match.group(1)[1]  # 'd', 'w', 'm', 'y'
                        web_query = match.group(2).strip()
                    else:
                        web_query = web_args
                    
                    if web_query:
                        time_labels = {'d': '24h', 'w': 'semana', 'm': 'mês', 'y': 'ano'}
                        time_info = f" 🕐 {time_labels[timelimit]}" if timelimit else ""
                        print(f"\n🌐 Buscando na web...{time_info}\n")
                        web_result = search_web(web_query, timelimit=timelimit)
                        print(web_result)
                        print()
                    else:
                        print("\n⚠️  Uso: /web <query>")
                        print("   Filtros: /web -d (dia), /web -w (semana), /web -m (mês), /web -y (ano)")
                    continue

                # Processar pergunta (Stream para velocidade percebida)
                # Gerar resposta (Streaming para evitar timeout visual e dar feedback imediato)
                streaming_response = chat_engine.stream_chat(prompt)
                
                print("Sovereign IA > ", end="", flush=True)
                full_response = ""
                for token in streaming_response.response_gen:
                    print(token, end="", flush=True)
                    full_response += token
                
                # ---- EXTRAÇÃO DE CITAÇÕES E FONTES ----
                source_nodes = getattr(streaming_response, "source_nodes", [])
                if source_nodes:
                    unique_sources = set()
                    for node_w_score in source_nodes:
                        metadata = node_w_score.node.metadata
                        if not metadata:
                            continue
                            
                        # Mapeamento do Caminho Original
                        if "file_path" in metadata:
                            unique_sources.add(f"📄 {metadata['file_path']}")
                        elif "file_name" in metadata:
                            unique_sources.add(f"📄 {metadata['file_name']}")
                    
                    if unique_sources:
                        print("\n\n**Fontes:**")
                        for source in sorted(unique_sources):
                            print(f"  - {source}")
                
                print("\n")
            except KeyboardInterrupt:
                print(f"\n👋 Até logo, {OWNER_NAME}!")
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
    import nest_asyncio
    try:
        nest_asyncio.apply()
    except ValueError:
        pass

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n👋 Até logo, {OWNER_NAME}!")
        sys.exit(0)
    except asyncio.CancelledError:
        print(f"\n👋 Até logo, {OWNER_NAME}!")
        sys.exit(0)