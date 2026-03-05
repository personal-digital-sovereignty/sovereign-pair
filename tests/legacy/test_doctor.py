import requests
import os
import time

token_cmd = os.popen("PYTHONPATH=$(pwd) .venv/bin/python get_token.py | tail -n 1").read().strip()

url = "http://localhost:8000/v1/chat"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token_cmd}"
}
data = {
  "session_id": 1,
  "message": "Escreva um ensaio filosófico sobre o significado do conhecimento e a soberania digital humana na arquitetura moderna de software.",
  "provider": "ollama",
  "model": "llama3.2:latest",
  "tenant_id": "PDS"
}

print(f"[{time.strftime('%X')}] 🔬 Enviando prompt cabuloso para The Doctor...")
start_time = time.time()
first_token_time = None
total_time = 0

with requests.post(url, headers=headers, json=data, stream=True) as r:
    for line in r.iter_lines():
        if line:
            if not first_token_time:
                first_token_time = time.time()
                ttft = first_token_time - start_time
                print(f"\n[!] Time-To-First-Token (TTFT) da API: {ttft:.2f} segundos\n")
            print(line.decode('utf-8'))
            
total_time = time.time() - start_time
print(f"\n\n[{time.strftime('%X')}] ✅ Teste The Doctor concluído. Tempo Total: {total_time:.2f} segundos")
