import requests

url = "http://localhost:8000/v1/chat"
headers = {"Content-Type": "application/json"}
payload = {"messages": [{"role": "user", "content": "Teste backend"}]}

try:
    res = requests.post(url, json=payload, headers=headers)
    print(f"Status: {res.status_code}")
    print(res.text[:500])
except Exception as e:
    print(f"Erro Real: {e}")
