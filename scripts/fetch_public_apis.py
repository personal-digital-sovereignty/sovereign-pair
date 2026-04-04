#!/usr/bin/env python3
import urllib.request
import json
import base64
import os
import re

HASH_FILE = "core/.api_hash"
OUT_FILE = "core/src/public_apis.b64"
API_URL = "https://api.github.com/repos/public-api-lists/public-api-lists/commits/master"
RAW_URL = "https://raw.githubusercontent.com/public-api-lists/public-api-lists/master/README.md"

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Sovereign-Pair-Builder/1.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def fetch_text(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Sovereign-Pair-Builder/1.0'})
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def main():
    try:
        commit_data = fetch_json(API_URL)
        latest_sha = commit_data['sha']
        
        if os.path.exists(HASH_FILE):
            with open(HASH_FILE, 'r') as f:
                if f.read().strip() == latest_sha and os.path.exists(OUT_FILE):
                    print("API Catalog is up-to-date. Skipping download.")
                    return

        print(f"New commit detected ({latest_sha}). Downloading latest API Catalog...")
        readme_text = fetch_text(RAW_URL)
        
        categories = {}
        current_category = "General"
        apis = []
        
        # Regex to parse markdown tables: | [Name](URL) | Description | Auth | HTTPS | CORS |
        for line in readme_text.split('\n'):
            line = line.strip()
            
            if line.startswith('### '):
                # E.g. "### Animals"
                current_category = line[4:].strip()
                continue
                
            if line.startswith('|') and len(line) > 5:
                # Skip headers and separators
                if '---|---|' in line or 'API | Description' in line:
                    continue
                
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 5:
                    # Extract markdown link: [Name](URL)
                    name_field = parts[0]
                    link_match = re.search(r'\[(.*?)\]\((.*?)\)', name_field)
                    
                    if link_match:
                        api_name = link_match.group(1)
                        api_url = link_match.group(2)
                        
                        api_obj = {
                            "name": api_name,
                            "url": api_url,
                            "description": parts[1],
                            "auth": parts[2],
                            "https": parts[3],
                            "cors": parts[4],
                            "category": current_category
                        }
                        apis.append(api_obj)
        
        json_dump = json.dumps(apis, indent=2)
        b64_encoded = base64.b64encode(json_dump.encode('utf-8')).decode('utf-8')
        
        # Write to core/src/public_apis.b64
        with open(OUT_FILE, 'w') as f:
            f.write(b64_encoded)
            
        with open(HASH_FILE, 'w') as f:
            f.write(latest_sha)
            
        print(f"Successfully scraped {len(apis)} public APIs into Base64 artifact.")
        
    except Exception as e:
        print(f"Failed to fetch public APIs during build: {e}")
        # Se falhar silencia, para não impedir o build offline se a rede cair,
        # desde que o fallback exista. Se não existir, criaremos um fallback vazio.
        if not os.path.exists(OUT_FILE):
            os.makedirs("core/src", exist_ok=True)
            with open(OUT_FILE, 'w') as f:
                f.write(base64.b64encode(b"[]").decode())

if __name__ == "__main__":
    # Garante que criamos de dentro da pasta raiz do projeto.
    # O build.rs é executado da pasta 'core', então nós vamos subir 1 nível.
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    main()
