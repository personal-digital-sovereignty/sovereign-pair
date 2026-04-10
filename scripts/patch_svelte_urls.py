import os
import re

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.svelte') or file.endswith('.ts') or file.endswith('.js'):
                filepath = os.path.join(root, file)
                process_file(filepath)

def process_file(filepath):
    if 'env_config.ts' in filepath:
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    has_api = False
    has_ollama = False

    # Check matches
    if re.search(r'http://(localhost|127\.0\.0\.1):38001', content):
        has_api = True
    if re.search(r'http://(localhost|127\.0\.0\.1):11434', content):
        has_ollama = True

    if not has_api and not has_ollama:
        return

    # Replace straight URL constants like const API_BASE_URL = 'http://localhost:38001';
    content = re.sub(
        r"const API_BASE_URL\s*=\s*['\"]http://(localhost|127\.0\.0\.1):38001['\"];",
        r"",
        content
    )

    # 1. Replace API URLs inside backticks (template literals)
    # e.g. `http://localhost:38001/v1/sessions/${id}` -> `${API_BASE_URL}/v1/sessions/${id}`
    content = re.sub(
        r"http://(?:localhost|127\.0\.0\.1):38001",
        r"${API_BASE_URL}",
        content
    )
    
    content = re.sub(
        r"http://(?:localhost|127\.0\.0\.1):11434",
        r"${OLLAMA_BASE_URL}",
        content
    )

    # Fix strings that used to be single/double quotes but now have ${}
    # e.g. 'http://.../xyz' or "http://.../xyz" -> `${...}/xyz`
    def fix_quotes(match):
        inner = match.group(2)
        return f"`{inner}`"
        
    content = re.sub(r"(['\"])(.*?\$\{API_BASE_URL\}.*?)\1", fix_quotes, content)
    content = re.sub(r"(['\"])(.*?\$\{OLLAMA_BASE_URL\}.*?)\1", fix_quotes, content)
    
    # 2. Add imports at the top of the <script> block for .svelte files, or just top of file for .ts
    imports = []
    if has_api:
        imports.append("API_BASE_URL")
    if has_ollama:
        imports.append("OLLAMA_BASE_URL")
        
    import_stmt = f"import {{ {', '.join(imports)} }} from '$lib/env_config';\n"
    
    if filepath.endswith('.svelte'):
        if '<script context="module">' in content:
            content = content.replace('<script context="module">', f'<script context="module">\n{import_stmt}', 1)
        elif '<script' in content:
            # find end of <script ...>
            content = re.sub(r'(<script[^>]*>)', r'\1\n' + import_stmt, content, count=1)
        else:
            # no script tag, prepend one
            content = f"<script>\n{import_stmt}</script>\n{content}"
    else:
        # For .ts / .js files
        content = import_stmt + content
        
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[+] Patched URLs in {filepath}")

process_directory('svelte-ui/src/lib')
process_directory('svelte-ui/src/routes')
