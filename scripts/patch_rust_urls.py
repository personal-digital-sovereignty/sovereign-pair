import os
import re

RUST_FILES = [
    "core/src/api.rs",
    "core/src/api_settings.rs",
    "core/src/api_trainer.rs",
    "core/src/auto_evaluator.rs",
    "core/src/os_installer.rs",
    "core/src/plan_execute.rs",
    "core/src/realtime.rs",
    "core/src/sync_engine.rs"
]

def process_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Patches Ollama (11434)
    # Match strings starting with quotes + http://127.0.0.1:11434 or localhost:11434
    
    # 1. Replace straight base urls
    content = re.sub(
        r'"http://(127\.0\.0\.1|localhost):11434"', 
        r'std::env::var("OLLAMA_BASE_URL").unwrap_or_else(|_| "http://127.0.0.1:11434".to_string())', 
        content
    )
    
    # 2. Replace URL prefixes (e.g. "http://127.0.0.1:11434/api/something") using format!
    # Regex captures the path after the base url
    content = re.sub(
        r'"http://(127\.0\.0\.1|localhost):11434(/[^"]*)"',
        r'format!("{}{}", std::env::var("OLLAMA_BASE_URL").unwrap_or_else(|_| "http://127.0.0.1:11434".to_string()), "\2")',
        content
    )
    
    # Patches Sovereign Multimodal (38001)
    content = re.sub(
        r'"http://(127\.0\.0\.1|localhost):38001"', 
        r'std::env::var("SOVEREIGN_API_URL").unwrap_or_else(|_| "http://127.0.0.1:38001".to_string())', 
        content
    )
    
    content = re.sub(
        r'"http://(127\.0\.0\.1|localhost):38001(/[^"]*)"',
        r'format!("{}{}", std::env::var("SOVEREIGN_API_URL").unwrap_or_else(|_| "http://127.0.0.1:38001".to_string()), "\2")',
        content
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[+] Patched URLs in {filepath}")

for f in RUST_FILES:
    process_file(f)
