curl -v -X POST http://localhost:38002/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{"model":"gpt-4o","messages":[{"role":"user","content":"Hello"},{"role":"assistant","content":"Hi"},{"role":"user","content":"What"}],"workspace_id":"default","session_id":null,"stream":true,"deep_research":false}'
