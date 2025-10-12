#!/usr/bin/env python3
"""
Script de configuração interativa para Sovereign Pair RAG.

Este script guia o usuário através da configuração inicial do projeto,
detectando modelos Ollama disponíveis e gerando o arquivo .env automaticamente.
"""

import os
import sys
import requests
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Mapeamento de modelos LLM para embed models recomendados
EMBED_MODEL_MAP = {
    "llama3.2": "nomic-embed-text",
    "llama3.1": "nomic-embed-text",
    "llama3": "nomic-embed-text",
    "llama2": "nomic-embed-text",
    "mistral": "nomic-embed-text",
    "mixtral": "nomic-embed-text",
    "phi": "nomic-embed-text",
    "gemma": "nomic-embed-text",
    "qwen": "nomic-embed-text",
    "codellama": "nomic-embed-text",
    "default": "nomic-embed-text"
}

# Mapeamento de tamanho de modelo para timeout recomendado
MODEL_SIZE_PATTERNS = {
    "small": ["phi", "gemma:2b", "llama3.2:1b"],
    "medium": ["llama3.2", "llama3.1", "llama3", "llama2", "mistral", "gemma:7b"],
    "large": ["mixtral", "llama3:70b", "llama2:70b", "qwen:72b"]
}

TIMEOUT_MAP = {
    "small": 60.0,
    "medium": 120.0,
    "large": 180.0,
    "default": 120.0
}


def print_header():
    """Exibe cabeçalho do script."""
    print("\n" + "=" * 70)
    print(f"{Colors.BOLD}{Colors.CYAN}🤖 SOVEREIGN PAIR - Configuração Interativa{Colors.ENDC}")
    print("=" * 70 + "\n")


def print_step(step_num: int, title: str):
    """Exibe título de uma etapa."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[{step_num}] {title}{Colors.ENDC}")
    print("-" * 70)


def print_success(message: str):
    """Exibe mensagem de sucesso."""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Exibe mensagem de aviso."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def print_error(message: str):
    """Exibe mensagem de erro."""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def detect_ollama() -> Optional[str]:
    """
    Detecta URL do Ollama.
    
    Returns:
        str: URL do Ollama ou None se não encontrado
    """
    # Tentar localhost primeiro
    default_url = "http://localhost:11434"
    
    try:
        response = requests.get(f"{default_url}/api/tags", timeout=3)
        if response.status_code == 200:
            return default_url
    except:
        pass
    
    return None


def list_available_models(base_url: str) -> List[Dict]:
    """
    Lista modelos disponíveis no Ollama.
    
    Args:
        base_url: URL base do Ollama
        
    Returns:
        list: Lista de modelos disponíveis
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return models
        return []
    except Exception as e:
        print_error(f"Erro ao listar modelos: {e}")
        return []


def get_model_size_category(model_name: str) -> str:
    """
    Determina a categoria de tamanho do modelo.
    
    Args:
        model_name: Nome do modelo
        
    Returns:
        str: Categoria (small, medium, large)
    """
    model_lower = model_name.lower()
    
    for size, patterns in MODEL_SIZE_PATTERNS.items():
        for pattern in patterns:
            if pattern in model_lower:
                return size
    
    return "medium"  # Padrão


def get_recommended_embed_model(llm_model: str) -> str:
    """
    Retorna embed model recomendado para o LLM.
    
    Args:
        llm_model: Nome do modelo LLM
        
    Returns:
        str: Nome do embed model recomendado
    """
    model_base = llm_model.split(":")[0].lower()
    return EMBED_MODEL_MAP.get(model_base, EMBED_MODEL_MAP["default"])


def get_recommended_timeout(model_name: str) -> float:
    """
    Calcula timeout recomendado baseado no modelo.
    
    Args:
        model_name: Nome do modelo
        
    Returns:
        float: Timeout em segundos
    """
    size_category = get_model_size_category(model_name)
    return TIMEOUT_MAP.get(size_category, TIMEOUT_MAP["default"])


def select_from_list(items: List[str], prompt: str, default_index: int = 0) -> Tuple[int, str]:
    """
    Permite seleção de item de uma lista.
    
    Args:
        items: Lista de itens
        prompt: Mensagem de prompt
        default_index: Índice padrão
        
    Returns:
        tuple: (índice selecionado, item selecionado)
    """
    print(f"\n{prompt}")
    for i, item in enumerate(items, 1):
        marker = f"{Colors.GREEN}→{Colors.ENDC}" if i - 1 == default_index else " "
        print(f"  {marker} [{i}] {item}")
    
    while True:
        try:
            choice = input(f"\nEscolha (1-{len(items)}) [padrão: {default_index + 1}]: ").strip()
            
            if not choice:
                return default_index, items[default_index]
            
            index = int(choice) - 1
            if 0 <= index < len(items):
                return index, items[index]
            else:
                print_error(f"Por favor, escolha um número entre 1 e {len(items)}")
        except ValueError:
            print_error("Por favor, digite um número válido")
        except KeyboardInterrupt:
            print("\n")
            sys.exit(0)


def interactive_setup() -> Dict[str, str]:
    """
    Executa setup interativo e retorna configurações.
    
    Returns:
        dict: Dicionário com configurações
    """
    config = {}
    
    # Etapa 1: Detectar Ollama
    print_step(1, "Detectando Ollama")
    
    ollama_url = detect_ollama()
    
    if ollama_url:
        print_success(f"Ollama detectado em: {ollama_url}")
        use_default = input(f"\nUsar esta URL? (S/n): ").strip().lower()
        
        if use_default in ['n', 'no', 'não']:
            ollama_url = input("Digite a URL do Ollama: ").strip()
    else:
        print_warning("Ollama não detectado em localhost")
        ollama_url = input("Digite a URL do Ollama (ex: http://localhost:11434): ").strip()
        
        if not ollama_url:
            ollama_url = "http://localhost:11434"
    
    # Validar conexão
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print_success("Conexão com Ollama validada!")
            config["OLLAMA_BASE_URL"] = ollama_url
        else:
            print_error("Não foi possível conectar ao Ollama nesta URL")
            sys.exit(1)
    except Exception as e:
        print_error(f"Erro ao conectar: {e}")
        sys.exit(1)
    
    # Etapa 2: Selecionar modelo LLM
    print_step(2, "Selecionando Modelo LLM")
    
    models = list_available_models(ollama_url)
    
    if not models:
        print_error("Nenhum modelo encontrado!")
        print_warning("Execute 'ollama pull llama3.2' para baixar um modelo")
        sys.exit(1)
    
    model_names = [m["name"] for m in models]
    
    # Tentar encontrar llama3.2 como padrão
    default_idx = 0
    for i, name in enumerate(model_names):
        if "llama3.2" in name.lower():
            default_idx = i
            break
    
    _, selected_model = select_from_list(
        model_names,
        "Modelos disponíveis:",
        default_idx
    )
    
    config["LLM_MODEL"] = selected_model
    print_success(f"Modelo selecionado: {selected_model}")
    
    # Etapa 3: Embed Model
    print_step(3, "Configurando Modelo de Embeddings")
    
    recommended_embed = get_recommended_embed_model(selected_model)
    print(f"\nModelo recomendado: {Colors.CYAN}{recommended_embed}{Colors.ENDC}")
    
    use_recommended = input("Usar modelo recomendado? (S/n): ").strip().lower()
    
    if use_recommended in ['n', 'no', 'não']:
        custom_embed = input("Digite o nome do embed model: ").strip()
        config["EMBED_MODEL"] = custom_embed if custom_embed else recommended_embed
    else:
        config["EMBED_MODEL"] = recommended_embed
    
    print_success(f"Embed model: {config['EMBED_MODEL']}")
    
    # Etapa 4: Timeout
    print_step(4, "Configurando Timeout")
    
    recommended_timeout = get_recommended_timeout(selected_model)
    size_category = get_model_size_category(selected_model)
    
    print(f"\nCategoria do modelo: {Colors.CYAN}{size_category}{Colors.ENDC}")
    print(f"Timeout recomendado: {Colors.CYAN}{recommended_timeout}s{Colors.ENDC}")
    
    use_recommended = input("Usar timeout recomendado? (S/n): ").strip().lower()
    
    if use_recommended in ['n', 'no', 'não']:
        while True:
            try:
                custom_timeout = input("Digite o timeout em segundos: ").strip()
                if custom_timeout:
                    config["REQUEST_TIMEOUT"] = str(float(custom_timeout))
                    break
                else:
                    config["REQUEST_TIMEOUT"] = str(recommended_timeout)
                    break
            except ValueError:
                print_error("Por favor, digite um número válido")
    else:
        config["REQUEST_TIMEOUT"] = str(recommended_timeout)
    
    print_success(f"Timeout: {config['REQUEST_TIMEOUT']}s")
    
    # Etapa 5: Configurações do ChromaDB
    print_step(5, "Configurando ChromaDB")
    
    default_collection = "sovereign_knowledge"
    collection_name = input(f"Nome da coleção [{default_collection}]: ").strip()
    config["CHROMA_COLLECTION_NAME"] = collection_name if collection_name else default_collection
    
    print_success(f"Coleção: {config['CHROMA_COLLECTION_NAME']}")
    
    # Etapa 6: Configurações do Agente
    print_step(6, "Configurando Agente")
    
    # Nome do usuário
    default_user = os.getenv("USER", "Usuário")
    user_name = input(f"Seu nome [{default_user}]: ").strip()
    config["USER_NAME"] = user_name if user_name else default_user
    
    # Modo verbose
    verbose_options = ["true", "false"]
    _, verbose = select_from_list(
        verbose_options,
        "Modo verbose (mostra raciocínio do agente):",
        0  # true por padrão
    )
    config["AGENT_VERBOSE"] = verbose
    
    # Máximo de resultados web
    while True:
        try:
            max_results = input("Máximo de resultados de busca web [3]: ").strip()
            if not max_results:
                config["MAX_WEB_SEARCH_RESULTS"] = "3"
                break
            else:
                config["MAX_WEB_SEARCH_RESULTS"] = str(int(max_results))
                break
        except ValueError:
            print_error("Por favor, digite um número válido")
    
    print_success("Configurações do agente definidas!")
    
    return config


def generate_env_file(config: Dict[str, str]) -> None:
    """
    Gera arquivo .env com as configurações.
    
    Args:
        config: Dicionário com configurações
    """
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    # Fazer backup se .env já existir
    if env_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = project_root / f".env.backup_{timestamp}"
        shutil.copy(env_file, backup_file)
        print_warning(f"Backup do .env existente criado: {backup_file.name}")
    
    # Gerar conteúdo do .env
    env_content = f"""# ============================================================================
# CONFIGURAÇÃO DO OLLAMA
# ============================================================================
OLLAMA_BASE_URL={config['OLLAMA_BASE_URL']}
LLM_MODEL={config['LLM_MODEL']}
EMBED_MODEL={config['EMBED_MODEL']}
REQUEST_TIMEOUT={config['REQUEST_TIMEOUT']}

# ============================================================================
# CONFIGURAÇÃO DO CHROMADB
# ============================================================================
CHROMA_COLLECTION_NAME={config['CHROMA_COLLECTION_NAME']}

# ============================================================================
# CONFIGURAÇÃO DO AGENTE
# ============================================================================
USER_NAME={config['USER_NAME']}
AGENT_VERBOSE={config['AGENT_VERBOSE']}
MAX_WEB_SEARCH_RESULTS={config['MAX_WEB_SEARCH_RESULTS']}
"""
    
    # Escrever arquivo
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print_success(f"Arquivo .env criado com sucesso!")


def print_summary(config: Dict[str, str]):
    """Exibe resumo das configurações."""
    print("\n" + "=" * 70)
    print(f"{Colors.BOLD}{Colors.GREEN}✅ CONFIGURAÇÃO CONCLUÍDA{Colors.ENDC}")
    print("=" * 70)
    
    print(f"\n{Colors.BOLD}Resumo das Configurações:{Colors.ENDC}\n")
    print(f"  🤖 Ollama URL:        {config['OLLAMA_BASE_URL']}")
    print(f"  🧠 Modelo LLM:        {config['LLM_MODEL']}")
    print(f"  📊 Embed Model:       {config['EMBED_MODEL']}")
    print(f"  ⏱️  Timeout:           {config['REQUEST_TIMEOUT']}s")
    print(f"  💾 Coleção ChromaDB:  {config['CHROMA_COLLECTION_NAME']}")
    print(f"  👤 Nome do Usuário:   {config['USER_NAME']}")
    print(f"  🔍 Modo Verbose:      {config['AGENT_VERBOSE']}")
    print(f"  🌐 Max Web Results:   {config['MAX_WEB_SEARCH_RESULTS']}")
    
    print(f"\n{Colors.BOLD}Próximos Passos:{Colors.ENDC}\n")
    print("  1. Adicione documentos em:")
    print("     - data/raw_docs/")
    print("     - data/vault/")
    print("\n  2. Execute a ingestão:")
    print("     $ cd src && python ingest.py")
    print("\n  3. Inicie o agente:")
    print("     $ cd src && python agent.py")
    print("\n" + "=" * 70 + "\n")


def main():
    """Função principal."""
    try:
        print_header()
        
        print("Este assistente irá guiá-lo através da configuração inicial.")
        print("Pressione Ctrl+C a qualquer momento para cancelar.\n")
        
        input("Pressione Enter para começar...")
        
        # Executar setup interativo
        config = interactive_setup()
        
        # Gerar arquivo .env
        print_step(7, "Gerando Arquivo de Configuração")
        generate_env_file(config)
        
        # Exibir resumo
        print_summary(config)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠ Configuração cancelada pelo usuário.{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
