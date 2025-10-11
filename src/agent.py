"""
Agente de Pair Programming Sovereign Pair.

Este módulo implementa um agente ReAct que pode escolher entre:
- Buscar informações nos arquivos locais (RAG)
- Buscar informações atualizadas na internet (DuckDuckGo)
"""

import logging
import sys
import chromadb
from typing import Optional
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.agent import ReActAgent
from duckduckgo_search import DDGS

# Importar configurações centralizadas
from config import (
    CHROMA_DIR,
    CHROMA_COLLECTION_NAME,
    USER_NAME,
    AGENT_VERBOSE,
    MAX_WEB_SEARCH_RESULTS,
    llm,
    embed_model,
    validate_ollama_connection,
    validate_ollama_models,
)

# Configurar logger
logger = logging.getLogger(__name__)


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
        local_query_engine = index.as_query_engine(llm=llm, similarity_top_k=5)
        
        # Criar ferramenta
        local_tool = QueryEngineTool(
            query_engine=local_query_engine,
            metadata=ToolMetadata(
                name="arquivos_pessoais",
                description=(
                    "Útil para buscar informações nos arquivos locais do usuário, "
                    "incluindo PDFs, anotações em Markdown, documentações pessoais, "
                    "e qualquer conteúdo que foi previamente indexado. "
                    "Use esta ferramenta para perguntas sobre documentos pessoais."
                ),
            ),
        )
        
        logger.info("   ✓ Ferramenta RAG inicializada com sucesso")
        return local_tool
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar ferramenta RAG: {e}")
        logger.exception("Detalhes:")
        return None


def search_web(query: str) -> str:
    """
    Busca informações atualizadas na internet usando DuckDuckGo.
    
    Args:
        query: Consulta de busca
        
    Returns:
        str: Resultados formatados ou mensagem de erro
    """
    try:
        logger.debug(f"🌐 Buscando na web: {query}")
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=MAX_WEB_SEARCH_RESULTS))
        
        if not results:
            return "Nenhum resultado encontrado na busca web."
        
        # Formatar resultados de forma mais legível
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"{i}. {result.get('title', 'Sem título')}\n"
                f"   {result.get('body', 'Sem descrição')}\n"
                f"   URL: {result.get('href', 'N/A')}"
            )
        
        return "\n\n".join(formatted_results)
        
    except Exception as e:
        logger.error(f"❌ Erro na busca web: {e}")
        return f"Erro ao buscar na internet: {str(e)}"


def initialize_web_tool() -> FunctionTool:
    """
    Inicializa a ferramenta de busca na internet.
    
    Returns:
        FunctionTool: Ferramenta de busca web configurada
    """
    logger.info("🌐 Inicializando ferramenta de busca web...")
    
    web_tool = FunctionTool.from_defaults(
        fn=search_web,
        name="busca_internet",
        description=(
            "Útil para buscar informações atualizadas na internet. "
            "Use esta ferramenta para perguntas sobre eventos atuais, "
            "notícias, informações que mudam frequentemente, ou qualquer "
            "coisa que não esteja nos arquivos locais do usuário."
        ),
    )
    
    logger.info("   ✓ Ferramenta de busca web inicializada")
    return web_tool


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


def main():
    """Função principal do agente."""
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
        local_tool = initialize_rag_tool()
        web_tool = initialize_web_tool()
        
        # Verificar se pelo menos uma ferramenta está disponível
        tools = []
        if local_tool:
            tools.append(local_tool)
        if web_tool:
            tools.append(web_tool)
        
        if not tools:
            print("\n❌ Erro: Nenhuma ferramenta disponível.")
            print("   Execute 'python ingest.py' para indexar documentos.")
            sys.exit(1)
        
        # Inicializar agente
        logger.info("🤖 Inicializando agente ReAct...")
        agent = ReActAgent.from_tools(
            tools,
            llm=llm,
            verbose=AGENT_VERBOSE,
            max_iterations=10,
        )
        logger.info("   ✓ Agente inicializado com sucesso")
        
        # Exibir mensagem de boas-vindas
        print_welcome_message()
        
        # Loop principal de conversação
        while True:
            try:
                # Solicitar input do usuário
                prompt = input(f"\n{USER_NAME} > ").strip()
                
                # Verificar se está vazio
                if not prompt:
                    continue
                
                # Processar comandos especiais
                if prompt.lower() == "sair":
                    print(f"\n👋 Até logo, {USER_NAME}!")
                    break
                
                elif prompt.lower() == "/help":
                    print_help()
                    continue
                
                elif prompt.lower() == "/clear":
                    agent.reset()
                    print("\n✓ Histórico de conversação limpo.")
                    continue
                
                # Processar pergunta com o agente
                print()  # Linha em branco para melhor formatação
                response = agent.chat(prompt)
                print(f"\nSovereign IA > {response}\n")
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Até logo, {USER_NAME}!")
                break
            
            except Exception as e:
                logger.error(f"❌ Erro ao processar pergunta: {e}")
                print(f"\n❌ Erro: {e}")
                print("Tente novamente ou digite '/help' para ajuda.\n")
        
    except KeyboardInterrupt:
        print(f"\n\n👋 Até logo, {USER_NAME}!")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        logger.exception("Detalhes:")
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()