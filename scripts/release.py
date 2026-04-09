#!/usr/bin/env python3
import sys
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path

def print_step(msg):
    print(f"[\033[34m*\033[0m] {msg}")

def print_success(msg):
    print(f"[\033[32m+\033[0m] {msg}")

def print_error(msg):
    print(f"[\033[31m-\033[0m] {msg}")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 release.py <version> (ex: 1.1.0)")
        sys.exit(1)
        
    version = sys.argv[1].strip()
    
    if version.startswith('v') or version.startswith('V'):
        print_error("Prefixos 'v' são estritamente proibidos pela regra de DevSecOps. Use o formato puro (ex: 1.1.0).")
        
    if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", version):
        print_error("A versão fornecida deve ser puramente numérica e semântica no formato X.Y.Z.")

    print(f"\n🚀 Iniciando Regras de Propagação Atômica para a versão: \033[1m{version}\033[0m\n")
    
    base_dir = Path(__file__).resolve().parent.parent
    
    # 1. Update VERSION file
    print_step("Atualizando /VERSION")
    version_file = base_dir / "VERSION"
    if version_file.exists():
        version_file.write_text(version + "\n")
        print_success("VERSION serializado.")
    
    # 2. Update core/Cargo.toml
    print_step("Atualizando core/Cargo.toml (Backend Rust)")
    cargo_core = base_dir / "core" / "Cargo.toml"
    if cargo_core.exists():
        content = cargo_core.read_text()
        content, n = re.subn(r'^version\s*=\s*".*?"', f'version = "{version}"', content, count=1, flags=re.MULTILINE)
        if n > 0:
            cargo_core.write_text(content)
            print_success("core/Cargo.toml sincronizado.")
        else:
            print_error("Atributo 'version' não encontrado em core/Cargo.toml.")
            
    # 3. Update svelte-ui/src-tauri/Cargo.toml
    print_step("Atualizando svelte-ui/src-tauri/Cargo.toml (Tauri Engine)")
    cargo_tauri = base_dir / "svelte-ui" / "src-tauri" / "Cargo.toml"
    if cargo_tauri.exists():
        content = cargo_tauri.read_text()
        # No tauri manifesto, a versão pode estar atrelada em propriedades de pacote. Buscamos a primeira [package] version.
        content, n = re.subn(r'^version\s*=\s*".*?"', f'version = "{version}"', content, count=1, flags=re.MULTILINE)
        if n > 0:
            cargo_tauri.write_text(content)
            print_success("tauri Cargo.toml sincronizado.")
    
    # 4. Update svelte-ui/package.json
    print_step("Atualizando svelte-ui/package.json (Frontend Node/Svelte)")
    pkg_json_path = base_dir / "svelte-ui" / "package.json"
    if pkg_json_path.exists():
        content = pkg_json_path.read_text()
        # Usar regex previne perda de formato de indentação do vite/svelte
        content = re.sub(r'"version":\s*".*?"', f'"version": "{version}"', content, count=1)
        pkg_json_path.write_text(content)
        print_success("package.json sincronizado.")
        
    # 5. Update svelte-ui/src-tauri/tauri.conf.json
    print_step("Atualizando svelte-ui/src-tauri/tauri.conf.json (App Config)")
    tauri_conf_path = base_dir / "svelte-ui" / "src-tauri" / "tauri.conf.json"
    if tauri_conf_path.exists():
        content = tauri_conf_path.read_text()
        content = re.sub(r'"version":\s*".*?"', f'"version": "{version}"', content, count=1)
        tauri_conf_path.write_text(content)
        print_success("tauri.conf.json sincronizado.")
        
    # 6. Mágica do Changelog Parsing e Injeção
    print_step("Automação de CHANGELOG e Commits...")
    changelog_path = base_dir / "CHANGELOG.md"
    
    if changelog_path.exists():
        # Busca a ultima tag no git para gerar diff
        commit_logs = ""
        try:
            last_tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'], stderr=subprocess.DEVNULL).decode().strip()
            git_cmd = f"git log {last_tag}..HEAD --pretty=format:'- %s'"
            log_output = subprocess.check_output(git_cmd, shell=True).decode().strip()
            if log_output:
                commit_logs = log_output
            else:
                commit_logs = "- (Nenhum commit detalhado capturado via script. Resuma aqui.)"
        except Exception:
            commit_logs = "- (Sem histórico prévio de tags via script. Preencha os feats manualmente.)"

        cl_content = changelog_path.read_text()
        
        # Ignora injeção se a versão já existir
        if f"## [{version}]" in cl_content:
            print_step(f"Aviso: Versão {version} já existe no CHANGELOG. Ignorando edição do log para evitar duplicação.")
        else:
            today_date = datetime.now().strftime("%Y-%m-%d")
            new_block = f"## [{version}] - {today_date}\n*Automated Semantic Release*\n\n### Added/Changed\n{commit_logs}\n\n"
            
            split_at = cl_content.find("## [")
            if split_at != -1:
                final_content = cl_content[:split_at] + new_block + cl_content[split_at:]
                changelog_path.write_text(final_content)
                print_success("CHANGELOG.md atualizado com parse automático infundido no topo.")
            else:
                print_error("A âncora '## [' não foi encontrada no CHANGELOG para inferir local de injeção.")
        
        # 7. Mirror para interface Svelte - Copiar arquivo Changelog puro para o Control Hub ler localmente no build
        import shutil
        svelte_data_dir = base_dir / "svelte-ui" / "src" / "lib"
        if not svelte_data_dir.exists():
            svelte_data_dir.mkdir(parents=True, exist_ok=True)
            
        svelte_changelog = svelte_data_dir / "CHANGELOG.md"
        shutil.copy(changelog_path, svelte_changelog)
        print_success(f"Vínculo Direto: CHANGELOG injetado no Frontend! ({svelte_changelog}) renderização autônoma autorizada.")
                
    else:
        print_step("Arquivo CHANGELOG.md não encontrado. Pulo...")
        
    print("\n\033[32m[==== PROPAGAÇÃO SEMÂNTICA CONCLUÍDA ====]\033[0m")
    print("A partir daqui a Sovereign UI já importará o CHANGELOG.md atualizado no Control Hub!")
    print(f"Lembre-se de verificar o git com 'git diff' e finalizar a submissão com: 'git commit -am \"chore(release): Sovereign Pair {version}\"'")

if __name__ == "__main__":
    main()
