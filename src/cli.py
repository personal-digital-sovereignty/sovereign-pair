#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
from pathlib import Path

# Adiciona o diretório atual ao PYTHONPATH para imports corretos do src
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

def main():
    parser = argparse.ArgumentParser(description="Sovereign Pair RAG - Terminal Automático")
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Comando 'start'
    parser_start = subparsers.add_parser("start", help="Inicia o Sovereign Pair")
    parser_start.add_argument("--full", action="store_true", help="Inicia Backend API e Web UI simultaneamente")
    parser_start.add_argument("--web", action="store_true", help="Inicia apenas o Front-end Web UI")
    parser_start.add_argument("--server", "--local", action="store_true", help="Inicia apenas o Backend (Padrão)")
    parser_start.add_argument("--port", type=int, default=8000, help="Porta para o RAG Backend (Padrão: 8000)")
    
    # Argumentos Override
    parser_start.add_argument("--provider", type=str, help="Força provedor LLM (ex: ollama, openai)")
    parser_start.add_argument("--model", type=str, help="Força o modelo LLM")
    parser_start.add_argument("--temperatura", type=float, help="Temperatura do LLM")
    parser_start.add_argument("--persona", type=str, help="System Prompt Base")
    parser_start.add_argument("--user", type=str, help="Nome do Dono da IA (Identidade)")
    parser_start.add_argument("--nickname", type=str, help="Apelido preferido do usuário")
    parser_start.add_argument("--language", type=str, help="Idioma nativo ou sotaque")
    parser_start.add_argument("--geolocation", type=str, help="Cidade/País base para contexto")
    parser_start.add_argument("--occupation", type=str, help="Ocupação/Profissão principal")
    parser_start.add_argument("--about-user", type=str, help="Regras ou interesses da memória do usuário")
    parser_start.add_argument("--sovereign-name", type=str, help="Nome da IA (Identidade da IA)")
    parser_start.add_argument("--conf", type=str, help="Caminho do arquivo de configuração alternativo sovereign.conf")

    # Comando 'ingest'
    parser_ingest = subparsers.add_parser("ingest", help="Força a ingestão manual de pastas (ignora Watcher)")
    parser_ingest.add_argument("path", type=str, nargs="?", help="Caminho opcional para processar. Se não passado, usa o padrão do conf.")
    parser_ingest.add_argument("--conf", type=str, help="Caminho do arquivo de configuração alternativo sovereign.conf")
    
    # Comando 'setup'
    parser_setup = subparsers.add_parser("setup", help="Assistente passo a passo da CLI para Gerar ~/.config/sovereign.conf")  # noqa: F841

    # Comando 'chat'
    parser_chat = subparsers.add_parser("chat", help="Modo Interativo 100% Terminal (Agente RAG Local)")
    # Argumentos Override para Chat
    parser_chat.add_argument("--provider", type=str, help="Força provedor LLM (ex: ollama, openai)")
    parser_chat.add_argument("--model", type=str, help="Força o modelo LLM")
    parser_chat.add_argument("--temperatura", type=float, help="Temperatura do LLM")
    parser_chat.add_argument("--persona", type=str, help="System Prompt Base")
    parser_chat.add_argument("--nickname", type=str, help="Apelido preferido do usuário")
    parser_chat.add_argument("--language", type=str, help="Idioma nativo ou sotaque")
    parser_chat.add_argument("--geolocation", type=str, help="Cidade/País base")
    
    args, unknown = parser.parse_known_args()
    
    # Processar arquivo de configuração global override (Cobre qualquer comando)
    if hasattr(args, 'conf') and args.conf:
        os.environ["SOVEREIGN_CONF"] = args.conf

    if args.command == "setup":
        run_setup()
        return

    if args.command == "ingest":
        run_ingest(args)
        return

    if args.command == "chat":
        # Argumentos também engatilham vars de ambiente no bloco abaixo
        pass

    # Comportamento padrão se não enviar sub-comando: assume 'start --server'
    if not args.command:
        # Verifica se passou flags soltas sem "start", como `python cli.py --full`
        if "--full" in sys.argv or "--web" in sys.argv or "--server" in sys.argv or "--local" in sys.argv:
             parser.parse_args(["start"] + sys.argv[1:], namespace=args)
        else:
             setattr(args, "server", True)
             setattr(args, "full", False)
             setattr(args, "web", False)
             setattr(args, "port", 8000)

    # Overrides no environ para o config.py puxar magicamente
    if hasattr(args, 'provider') and args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
    if hasattr(args, 'model') and args.model:
        os.environ["LLM_MODEL"] = args.model
    if hasattr(args, 'temperatura') and args.temperatura is not None:
        os.environ["LLM_TEMPERATURE"] = str(args.temperatura)
    if hasattr(args, 'persona') and args.persona:
        os.environ["SYSTEM_PROMPT"] = args.persona
    if hasattr(args, 'user') and args.user:
        os.environ["OWNER_NAME"] = args.user
    if hasattr(args, 'nickname') and args.nickname:
        os.environ["OWNER_NICKNAME"] = args.nickname
    if hasattr(args, 'language') and args.language:
        os.environ["LANGUAGE"] = args.language
    if hasattr(args, 'geolocation') and args.geolocation:
        os.environ["GEOLOCATION"] = args.geolocation
    if hasattr(args, 'occupation') and args.occupation:
        os.environ["OCCUPATION"] = args.occupation
    if hasattr(args, 'about_user') and args.about_user:
        os.environ["ABOUT_USER"] = args.about_user
    if hasattr(args, 'sovereign_name') and args.sovereign_name:
        os.environ["SOVEREIGN_NAME"] = args.sovereign_name

    # O import do config MUDADO para DEPOIS do env injection
    import src.config as config

    # Se chamou start explícito ou fallback via sys.argv flags
    if args.command == "start" or getattr(args, "full", False) or getattr(args, "web", False) or getattr(args, "server", False):
        if hasattr(args, "full") and args.full:
            port = getattr(args, "port", 8000)
            print(f"🚀 Iniciando Sovereign Pair ({config.SOVEREIGN_NAME}) no modo FULL na porta {port}...")
            api_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", str(port)])
            try:
                subprocess.run(["npm", "run", "dev"], cwd=str(config.BASE_DIR / "web-ui"))
            except KeyboardInterrupt:
                api_process.terminate()
        elif hasattr(args, "web") and args.web:
            print("🚀 Iniciando Web UI de forma isolada...")
            subprocess.run(["npm", "run", "dev"], cwd=str(config.BASE_DIR / "web-ui"))
        else:
            port = getattr(args, "port", 8000)
            print(f"🚀 Iniciando RAG Backend ({config.SOVEREIGN_NAME}) para uso do(a) {config.OWNER_NICKNAME} na porta {port}...")
            import uvicorn
            uvicorn.run("src.api.main:app", host="0.0.0.0", port=port)
            
    elif args.command == "chat":
        print(f"🤖 Iniciando Sovereign Pair ({config.SOVEREIGN_NAME}) no Modo Chat Interativo (Terminal)...")
        chat_env = os.environ.copy()
        chat_env["PYTHONPATH"] = f"{config.BASE_DIR}{os.pathsep}{chat_env.get('PYTHONPATH', '')}"
        subprocess.run([sys.executable, "src/agent.py"], env=chat_env)

def run_ingest(args):
    import src.config as config
    from src.ingest import index_documents
    if args.path:
        print(f"📖 Ingerindo documentos da nova Fonte específica em: {args.path}")
        index_documents(data_dir=args.path, interactive=False)
    else:
        print(f"📖 Ingerindo documentos do Vault padrão configurado para o usuário {config.OWNER_NAME}...")
        for bpath in config.RAW_DOCS_DIRS:
            index_documents(data_dir=str(bpath), interactive=False)

def run_setup():
    print("=========================================================================")
    print("🛡️ Sovereign Pair RAG: Assistente de Configuração Global e Soberania Local")
    print("=========================================================================")
    
    conf_path = Path("~/.config/sovereign.conf").expanduser()
    if conf_path.exists():
        print(f"\\n[Aviso] Já existe uma configuração antiga em {conf_path}.")
        if input("Deseja sobrescrever tudo e recomeçar? (y/N): ").lower() != 'y':
            return
    
    conf_path.parent.mkdir(parents=True, exist_ok=True)
    
    dono = input("\\n1. Como você se chama? (Usuário Mestre): [Jeferson] ") or "Jeferson"
    nickname = input(f"2. Tem algum apelido como prefere ser chamado? [{dono}]: ") or dono
    ia = input("3. Como deseja batizar a sua IA Pessoal? [Sovereign Pair]: ") or "Sovereign Pair"
    language = input("4. Qual o idioma ou sotaque principal para a IA adotar? [Português do Brasil]: ") or "Português do Brasil"
    geo = input("5. Qual a sua cidade/base (Geolocalização)? [Em Branco]: ") or ""
    occ = input("6. Qual a sua ocupação ou área de atuação primária? [Em Branco]: ") or ""
    provider = input("7. Qual o motor LLM padrão que será usado? (ollama/openai/gemini) [ollama]: ") or "ollama"
    
    print("\\n🔧 Configurações Adicionais:")
    origins = input("8. CORS: Quais URLs (Domínio Web UI) estarão permitidas bater na API? [http://localhost:5173]: ") or "http://localhost:5173,http://localhost:3000"
    
    with open(conf_path, "w") as f:
        f.write("# SOVEREIGN PAIR RAG - GLOBAL CONFIGURATION\\n")
        f.write(f"OWNER_NAME={dono}\\n")
        f.write(f"OWNER_NICKNAME={nickname}\\n")
        f.write(f"SOVEREIGN_NAME={ia}\\n")
        f.write(f"LANGUAGE={language}\\n")
        f.write(f"GEOLOCATION={geo}\\n")
        f.write(f"OCCUPATION={occ}\\n")
        f.write(f"LLM_PROVIDER={provider}\\n")
        f.write(f"ALLOWED_ORIGINS={origins}\\n")
    
    print(f"\\n✅ Excelente! Confidencialidade e configurações salvas firmemente em: {conf_path}\\n")
    print("Execute 'python src/cli.py --full' para ligar o Motor da Inteligência.")

if __name__ == "__main__":
    main()
