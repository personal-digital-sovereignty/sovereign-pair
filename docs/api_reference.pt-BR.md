# Sovereign Pair - Integration API Reference

**Status da Arquitetura:** Estável (Release 3.3.0)
**Protocolo:** HTTP/RESTful + Server-Sent Events (SSE)
**Segurança (Auth):** Bearer Token (JWT / Tailscale M2M)

Este documento destina-se a Engenheiros de Integração (SRE/DevOps) e desenvolvedores de ferramentas secundárias (como scripts auxiliares, N8N, ou clientes Obsidian customizados). Ele detalha as assinaturas RESTful hospedadas pela porta central do motor FastAPI on-premises do Sovereign Pair, habilitando o manuseio externo da malha RAG (Retrieval-Augmented Generation) sob infraestrutura Zero-Trust.

---

## Autenticação e Topologia de Acesso

O Sovereign Pair descarta roteamento público. Os acessos aos endpoints documentados requerem tráfego encapsulado via túnel autorizado (Tailscale Darknet IP) ou `localhost`.

Toda requisição externa originada pela malha VPN (Ex: Oracle OCI instanciando N8N) obriga a presença temporal do cabeçalho canônico de Autorização contendo a string Bearer assinada pela *Secret-Key* da infraestrutura ou um M2M Auth gerado via Tailscale:

```http
Authorization: Bearer <seu_jwt_de_sessao_blindada>
```

---

## 1. Inference Engine (LLM & RAG)

### Invocação de Motor Reativo Assíncrono (`POST /v1/chat`)
Endpoint vital para dialogar com a malha Cibrid RAG. Injeta prompts crus baseando-se no contexto orgânico da máquina do usuário. Suporta respostas atômicas padronizadas ou Stream Server-Sent Events (SSE) para renderização progressiva UX em tempo real.

**Endpoint:** `POST /api/v1/chat`
**Headers:** `Content-Type: application/json`

**Payload JSON:**
```json
{
  "message": "Qual a senha root documentada no manual OCI?",
  "stream": true,
  "agent_role": "the_coder",
  "folder_context": "Projetos Corporativos"
}
```

**Propriedades do Corpo (Trade-Offs):**
*   `message` *(obrigatório)*: A injetiva (prompt) do usuário em string crua.
*   `stream` *(opcional, default falso)*: Habilita chunking em `text/event-stream`. Quando marcado como `true`, a latência percebida cai drasticamente. Recomendado para interfaces humanas (Vue/React).
*   `agent_role` *(opcional)*: Sobrescreve a Persona inferencial. Redireciona os parâmetros de Prompt do sistema (ex: `"the_coder"` aciona densidade de blocos lógicos Python, `"the_doctor"` aciona taxonomia causal e filosófica minuciosa). Ausência assume a diretriz The Mom/The Dad.
*   `folder_context` *(opcional)*: Trava a busca em um compartimento semântico em detrimento da leitura global de toda estrutura do `/home/`, impedindo contaminação cruzada das fontes RAG ao limitar o retriever BM25/Cosseno.

**Retorno de Streaming (SSE - HTTP 200):**
O limite de pacotes devolvidos se subdivide em tokens renderizáveis até o acoplamento das referências exatas utilizadas pelo Llama.
```text
data: {"token": "A", "done": false}
data: {"token": " senha", "done": false}
data: {"token": " root", "done": false}
data: {"token": " é", "done": false}
data: {"token": " 123", "done": false}
data: {"sources": ["file:///vault/dev/oracle.md"], "done": true}
```

**Retorno Atômico (HTTP 200 - Quando `stream`: false):**
```json
{
  "response": "A senha root é 123.",
  "sources": [
    "file:///vault/dev/oracle.md"
  ]
}
```

---

## 2. Ingestion Trigger (Operações Vetoriais)

### Recálculo do Sensus Vault (`POST /v1/ingest`)
Força a reavaliação dos vetores de memória do banco de dados (ChromaDB) inspecionando diferenças, deleções e adições não mapeadas do subsistema de arquivos no sistema operativo hospedeiro.

**Aviso Operacional:** 
Dada a natureza intensiva de I/O em CPU, as chamadas à este módulo enfileiram os processamentos em Threads Assíncronas limitados pelo Python Global Interpreter Lock (GIL), operando o `compute_hashes_parallel` internamente a taxas 4x superior ao IO blocking clássico. Disparos massivos (DDoS) sem rate-limit estagnarão recursos da interface visual local, portando trate este Trigger exclusivamente via instâncias restritas corporativas ou Webhooks de File Watcher controlados pelo Cronjob/N8N.

**Endpoint:** `POST /api/v1/ingest`

**Retorno de Validação Assíncrona (HTTP 200):**
```json
{
   "status": "success",
   "message": "Operação de varredura diferencial engatilhada nas filas do Background.",
   "total_dirty_files_queued": 14
}
```

---

*Nota Interna da Equipe (QA): Endpoints legados baseados em utilitários monolíticos Python puros foram extintos localmente, sendo encapsulados na SDK de integração MCP da Anthropic nas fases subsequentes.*
