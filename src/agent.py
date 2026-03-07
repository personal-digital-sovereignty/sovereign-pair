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

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

import chromadb
from typing import Optional

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.tools import QueryEngineTool, ToolMetadata

from config import (
    CHROMA_DIR,
    CHROMA_COLLECTION_NAME,
    CHROMA_SYSTEM_COLLECTION_NAME,
    OWNER_NAME,
    AGENT_VERBOSE,
    llm,
    get_embed_model,
    validate_ollama_connection,
    validate_ollama_models
)
from web_search import search_web

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

# Configurar logger
logger = logging.getLogger(__name__)

# Configurar logger
logger = logging.getLogger(__name__)

console = Console()

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
        chroma_collection = db.get_or_create_collection(CHROMA_SYSTEM_COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=get_embed_model(),
            storage_context=storage_context
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



def print_welcome_message():
    """Exibe mensagem de boas-vindas."""
    welcome_text = f"""
Oi, **{OWNER_NAME}**! 👋

Eu posso ajudar você com:
- Buscar informações nos seus **arquivos locais**
- Buscar informações atualizadas na **internet**
- Responder perguntas e auxiliar no desenvolvimento

**Comandos especiais:**
- `/help`          - Mostrar esta mensagem
- `/clear`         - Limpar histórico de conversação
- `/web <query>`   - Buscar na internet (DuckDuckGo)
- `sair`           - Encerrar o programa
    """
    console.print(Panel(
        Markdown(welcome_text.strip()), 
        title="🤖 SOVEREIGN PAIR - Agente de Pair Programming", 
        border_style="cyan"
    ))


def print_help():
    """Exibe mensagem de ajuda."""
    help_text = """
**Comandos disponíveis:**
- `/help`   - Mostrar esta mensagem de ajuda
- `/clear`  - Limpar o histórico de conversação
- `sair`    - Encerrar o programa

**Dicas:**
- Seja específico nas suas perguntas
- O agente escolherá automaticamente entre busca local ou web
- Para forçar busca local, mencione "nos meus arquivos"
- Para forçar busca web, mencione "na internet" ou "atualizado"
    """
    console.print(Panel(
        Markdown(help_text.strip()),
        title="📖 AJUDA - Sovereign Pair",
        border_style="blue"
    ))


async def main():
    """Função principal do agente (Assíncrona)."""
    try:
        import config
        # Fallback local para testes da CLI fora da Docker network
        if "http://ollama:" in config.OLLAMA_BASE_URL:
            config.OLLAMA_BASE_URL = config.OLLAMA_BASE_URL.replace("http://ollama:", "http://localhost:")
            logger.info(f"Substituição de rede Docker ativada para modo CLI puro. Ollama em {config.OLLAMA_BASE_URL}")

        # Validar conexão com Ollama
        console.print("[yellow]🔍 Validando conexão com Ollama...[/yellow]")
        logger.info("🔍 Validando conexão com Ollama...")
        if not validate_ollama_connection():
            console.print("\n[bold red]❌ Erro: Não foi possível conectar ao Ollama.[/bold red]")
            console.print("   Certifique-se de que o Ollama está rodando:")
            console.print("   [cyan]$ ollama serve[/cyan]")
            sys.exit(1)
        
        # Validar modelos
        console.print("[yellow]🔍 Validando modelos Ollama...[/yellow]")
        logger.info("🔍 Validando modelos Ollama...")
        models_ok, missing_models = validate_ollama_models()
        if not models_ok:
            console.print(f"\n[bold yellow]⚠️  Modelos faltando no Ollama: {', '.join(missing_models)}[/bold yellow]")
            console.print("   Iniciando download automático (isso pode demorar minutos ou horas dependendo da sua conexão)...")
            for model in missing_models:
                console.print(f"   Baixando {model}...")
                try:
                    subprocess.run(["ollama", "pull", model], check=True)
                    console.print(f"   [bold green]✓ {model} baixado com sucesso![/bold green]")
                except FileNotFoundError:
                    console.print("\n[bold red]❌ Erro: O comando 'ollama' não foi encontrado no seu sistema.[/bold red]")
                    console.print("   Por favor, instale o Ollama em https://ollama.com/")
                    sys.exit(1)
                except subprocess.CalledProcessError:
                    console.print(f"\n[bold red]❌ Erro ao baixar o modelo {model}.[/bold red]")
                    console.print(f"   Por favor, rode manualmente: ollama pull {model}")
                    sys.exit(1)
            console.print("   [bold green]✓ Todos os modelos prontos![/bold green]")
        
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
            console.print("\n[bold red]❌ Erro: Nenhuma ferramenta disponível.[/bold red]")
            console.print("   Execute 'python ingest.py' para indexar documentos.")
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
        
        model_name = getattr(chat_engine._llm, "model", "Motor Desconhecido")
        
        console.print(f"\n[bold cyan]💡 Dica:[/bold cyan] Modo Turbo Ativado! (Usando {model_name})")
        console.print("   Pergunte sobre seus arquivos. Digite 'sair' para encerrar.\n")
        
        # Configurar prompt_toolkit
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import WordCompleter
        from prompt_toolkit.history import InMemoryHistory
        
        command_completer = WordCompleter([
            '/help', '/clear', '/web', 'sair', 'exit', 'quit'
        ], ignore_case=True)
        
        session = PromptSession(
            history=InMemoryHistory(),
            completer=command_completer,
        )

        
        while True:
            try:
                # Usar prompt_toolkit em vez de input()
                prompt_text = session.prompt(f"\n{OWNER_NAME} > ").strip()
                
                if not prompt_text:
                    continue
                
                if prompt_text.lower() in ['sair', 'exit', 'quit']:
                    console.print(f"\n👋 [bold green]Até logo, {OWNER_NAME}![/bold green]")
                    break
                
                if prompt_text == '/help':
                    print_welcome_message()
                    continue
                
                if prompt_text == '/clear':
                    console.print("\n🧹 Limpando histórico local...")
                    chat_engine.reset()
                    continue
                
                if prompt_text.startswith('/web'):
                    web_args = prompt_text[4:].strip()
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
                        console.print(f"\n🌐 Buscando na web...{time_info}\n")
                        web_result = search_web(web_query, timelimit=timelimit)
                        console.print(Markdown(web_result))
                        print()
                    else:
                        console.print("\n⚠️  [yellow]Uso: /web <query>[/yellow]")
                        console.print("   Filtros: /web -d (dia), /web -w (semana), /web -m (mês), /web -y (ano)")
                    continue

                # Processar pergunta (Stream para velocidade percebida)
                # Gerar resposta (Streaming para evitar timeout visual e dar feedback imediato)
                streaming_response = chat_engine.stream_chat(prompt_text)
                
                console.print("[bold purple]Sovereign IA >[/bold purple]", end=" ")
                full_response = ""
                
                from rich.live import Live
                
                with Live(Markdown(""), refresh_per_second=15, console=console) as live:
                    for token in streaming_response.response_gen:
                        full_response += token
                        live.update(Markdown(full_response))
                
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
                        console.print("\n\n**Fontes:**")
                        for source in sorted(unique_sources):
                            console.print(f"  - [cyan]{source}[/cyan]")
                
                print("\n")
            except KeyboardInterrupt:
                console.print(f"\n👋 [bold green]Até logo, {OWNER_NAME}![/bold green]")
                break
            except EOFError:
                # Ctrl+D
                console.print(f"\n👋 [bold green]Até logo, {OWNER_NAME}![/bold green]")
                break
            except Exception as e:
                logger.error(f"❌ Erro ao processar pergunta: {e}")
                console.print(f"\n[bold red]❌ Erro: {e}[/bold red]")
                console.print("Tente novamente ou digite '/help' para ajuda.\n")
        
    except KeyboardInterrupt:
        logger.info("\n\n👋 Encerrando o programa...")
        sys.exit(0)
    except Exception as e:
        logger.exception("❌ Erro fatal não tratado:")
        console.print(f"\n[bold red]❌ Erro fatal: {e}[/bold red]")
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