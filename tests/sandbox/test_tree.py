import requests

try:
    auth_res = requests.post("http://127.0.0.1:8000/v1/auth/login", json={"password": "pwd"})
    token = auth_res.json().get("access_token")
    if token:
        res = requests.get("http://127.0.0.1:8000/v1/vault/tree", headers={"Authorization": f"Bearer {token}"})
        print(res.status_code)
        print(res.text[:500])
    else:
        print("Auth error, trying without auth as local may bypass or just checking logs in UI is better.")
except Exception as e:
    print(e)
