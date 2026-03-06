import os
import logging
from fastapi import Request, Response

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent, Resource
from src.config import VAULT_DIR

logger = logging.getLogger(__name__)

mcp_server = Server("sovereign-pair-mcp")

@mcp_server.list_resources()
async def list_resources() -> list[Resource]:
    """Expõe arquivos do Sovereign Vault como Recursos URI para o MCP."""
    resources = []
    if os.path.exists(VAULT_DIR):
        for root, dirs, files in os.walk(VAULT_DIR):
            for file in files:
                if file.endswith('.md'):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, VAULT_DIR)
                    uri = f"file://{path}"
                    
                    resources.append(
                        Resource(
                            uri=uri,
                            name=file,
                            mimeType="text/markdown",
                            description=f"Sensus Vault Document: {rel_path}"
                        )
                    )
    return resources

@mcp_server.read_resource()
async def read_resource(uri: str) -> str | bytes:
    """Permite ao MCP (Cline/VSCode) ler arquivos do Vault nativamente."""
    if uri.startswith("file://"):
        path = uri[7:]
        # Validação RFI básica (Directory Traversal Prevention)
        if os.path.exists(path) and str(path).startswith(str(VAULT_DIR)):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                raise ValueError(f"Failed to read resource: {e}")
    raise ValueError(f"Recurso não encontrado ou acesso negado (Zero-Trust): {uri}")

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """Exposição das capacidades da IA Soberana para a rede via MCP Tools."""
    return [
        Tool(
            name="sensus_vault_search",
            description="Busca na base de vetorial semântica do projeto local. Use isso para extrair contexto de documentações e códigos registrados.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Linguagem natural da busca, ex: 'regras de roteamento da API'"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="sensus_project_context",
            description="Retorna a arquitetura corporativa e o contexto estrutural mapeado.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Nome do projeto opcional."}
                }
            }
        ),
        Tool(
            name="the_doctor_reasoning",
            description="Aciona o Agente Especialista Tier 4 (The Doctor) para resolução de tarefas sistêmicas pesadas ou análise profunda.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Comando para o Agente"}
                },
                "required": ["prompt"]
            }
        )
    ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Intercepta chamadas de Ferramentas via IDE Cliente ou N8N."""
    
    if name == "sensus_vault_search":
        try:
            from src.core.the_dad import VectorStoreManager
            query = arguments.get("query")
            if not query:
                return [TextContent(type="text", text="Erro: 'query' é obrigatória.")]
                
            vs = VectorStoreManager(tenant_id="default")
            results = vs.similarity_search(query, k=5)
            if not results:
                return [TextContent(type="text", text="Nenhuma informação vetorial mapeada no Sovereign Vault para esta Query.")]
                
            # Extração limpa para Model Context Protocol
            combined = "\n\n---\n\n".join([f"Path: {r.metadata.get('file_path', 'N/A')}\nConteúdo: {r.page_content}" for r in results])
            return [TextContent(type="text", text=f"Contexto Recuperado:\n{combined}")]
        except Exception as e:
            logger.error(f"[MCP Vault Search] Error: {e}")
            return [TextContent(type="text", text=f"Erro fatal executando Sensus Vault Search: {str(e)}")]

    elif name == "sensus_project_context":
        return [TextContent(type="text", text="Arquitetura ativa: Sovereign Pair RAG e Cibrid Mesh. Nenhuma sub-estruturação Context7 registrada ainda.")]

    elif name == "the_doctor_reasoning":
        try:
            from src.engine_builder import resolve_dynamic_llm
            from src.config import llm as default_llm
            from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
            
            prompt = arguments.get("prompt")
            # Invoca dinamicamente o LLM ativo no config
            llm = resolve_dynamic_llm("ollama", os.getenv("LLM_MODEL", "qwen2.5"), default_llm)
            
            messages = [
                LlamaMsg(role=MessageRole.SYSTEM, content="Você é The Doctor, agente especialista rodando embarcado no IDE via Protocolo MCP. Baseie-se apenas em fatos de engenharia de software e RAG."),
                LlamaMsg(role=MessageRole.USER, content=prompt)
            ]
            
            response = await llm.achat(messages)
            return [TextContent(type="text", text=str(response.message.content))]
        except Exception as e:
            logger.error(f"[MCP Doctor] Error: {e}")
            return [TextContent(type="text", text=f"Erro fatal executando The Doctor: {str(e)}")]
            
    return [TextContent(type="text", text=f"Tool não mapeada ou desconhecida: {name}")]

def mount_mcp_server(app):
    """Acopla o Transportador HTTP/SSE da Anthropic na instância do FastAPI."""
    
    sse_transport = SseServerTransport("/mcp/messages")
    
    @app.get("/mcp/sse")
    async def mcp_setup_sse(request: Request):
        try:
            async with sse_transport.connect_sse(request.scope, request.receive, request._send) as sse:
                await mcp_server.run(sse, mcp_server.create_initialization_options())
        except BaseException:
            pass

    @app.post("/mcp/messages")
    async def mcp_receive_message(request: Request):
        await sse_transport.handle_post_message(request.scope, request.receive, request._send)
        return Response(status_code=202)
