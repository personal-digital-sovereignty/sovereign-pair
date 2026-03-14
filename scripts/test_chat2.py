import requests

base_url = "http://127.0.0.1:8000/v1"

# Primeiro, logar para pegar token
login_data = {"password": "pwd"}
try:
    auth_res = requests.post(f"{base_url}/auth/login", json=login_data)
    token = auth_res.json().get("access_token")
    if not token:
        print("Erro de auth:", auth_res.text)
        exit(1)
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    payload = {
        "messages": [{"role": "user", "content": "Olá The Doctor!"}],
        "rag_mode": False
    }

    print("Enviando POST /chat...")
    res = requests.post(f"{base_url}/chat", json=payload, headers=headers)
    print(f"Status: {res.status_code}")
    print("Response Content:")
    print(res.text[:500])
except Exception as e:
    print(f"Erro Real: {e}")
