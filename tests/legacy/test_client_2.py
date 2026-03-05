import requests
import os

token_cmd = os.popen("PYTHONPATH=$(pwd) .venv/bin/python get_token.py | tail -n 1").read().strip()

url = "http://localhost:8000/v1/chat"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token_cmd}"
}
data = {
  "session_id": 1,
  "message": "Extraia a seguinte lista em uma tabela Markdown limpa: Maçã vermelha, Banana roxa, Uva verde.",
  "provider": "ollama",
  "model": "llama3.2:latest",
  "tenant_id": "PDS"
}

with requests.post(url, headers=headers, json=data, stream=True) as r:
    for line in r.iter_lines():
        if line:
            print(line.decode('utf-8'))
