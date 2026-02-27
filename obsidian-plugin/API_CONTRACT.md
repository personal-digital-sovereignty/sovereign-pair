# Sovereign Pair Plugin - API Contract

This document outlines the REST API contract required to build a custom backend that is fully compatible with the **Sovereign Pair Obsidian Plugin**. 

By adhering to this contract, you can implement your own RAG backend in Go, Rust, Ruby, or any other language, and seamlessly connect it to the Obsidian Plugin using the "API Base URL" settings.

## Global Requirements

1. **Authentication:** All requests must accept a Bearer Token in the `Authorization` header.
   ```http
   Authorization: Bearer <your-sovereign-token>
   ```
2. **CORS:** Ensure your backend responds with `Access-Control-Allow-Origin: *` (or the `app://obsidian.md` origin) for all preflight `OPTIONS` requests.
3. **Content-Type:** All payloads are `application/json` (except `/v1/ingest` which uses `multipart/form-data`).

---

## 1. Engine Configuration
**Endpoint:** `GET /v1/config`

This is the first endpoint the plugin hits when the user opens the Settings Tab. It populates the available LLM Providers and Models in the drop-down menus.

### Response `200 OK`
```json
{
  "system_config": {
    "engine": {
      "temperature": 0.7,
      "providers": {
        "ollama": {
          "models": ["llama3", "mistral", "qwen2.5"]
        },
        "openai": {
          "models": ["gpt-4o", "gpt-4-turbo"]
        }
      },
      "default_provider": "ollama",
      "default_model": "mistral"
    }
  }
}
```

---

## 2. Generate Chat (Streaming)
**Endpoint:** `POST /v1/chat`

Handles the actual chat request and streams the response back to the Obsidian UI.

### Request Body
```json
{
  "message": "Qual é a capital da França?",
  "session_id": "optional-uuid",
  "provider": "ollama",
  "model": "mistral",
  "search_mode": "local",
  "temperature": 0.5,
  "system_prompt": "You are a helpful assistant."
}
```
*Note: `search_mode` can be `local` (Vector DB), `web` (DuckDuckGo), or `none`.*

### Response `200 OK` (Server-Sent Events)
The plugin expects standard Server-Sent Events (SSE).
```text
data: {"response": "A", "sources": []}
data: {"response": " capital", "sources": []}
data: {"response": " da França", "sources": []}
data: {"response": " é Paris.", "sources": [{"title": "Geografia", "url": "doc_id_1"}]}
```

---

## 3. Session Management

### List Sessions
**Endpoint:** `GET /v1/sessions`

Returns the chat history grouped in the sidebar.
```json
[
  {
    "id": "uuid-1234",
    "title": "Discussão Python",
    "created_at": "2026-02-27T10:00:00Z",
    "tags": ["python", "dev"]
  }
]
```

### Get Session Details
**Endpoint:** `GET /v1/sessions/{session_id}`

Loads previous messages when clicking a session.
```json
{
  "id": "uuid-1234",
  "title": "Discussão Python",
  "messages": [
    {"role": "user", "content": "Olá"},
    {"role": "assistant", "content": "Olá! Como ajudo?"}
  ]
}
```

### Delete Session
**Endpoint:** `DELETE /v1/sessions/{session_id}`

### Update Session
**Endpoint:** `PUT /v1/sessions/{session_id}`
```json
{
  "title": "Novo Título",
  "tags": ["nova-tag"]
}
```

---

## 4. File Ingestion
**Endpoint:** `POST /v1/ingest`
**Content-Type:** `multipart/form-data`

Automatically sends Markdown files to standard Vector Databases.

### Form Data
- `file`: The `.md` file blob
- `force_overwrite`: `true` or `false` (Boolean string)

### Response `200 OK`
```json
{
  "status": "success",
  "message": "Documento indexado com sucesso",
  "doc_id": "file-123",
  "chunks": 15
}
```

## Need Help?
Check the reference Python FastAPI implementation in our official GitHub repository to see how we handled Vector embedding and Streaming in the Official Engine!
