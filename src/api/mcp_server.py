import os
import logging
from fastapi import Request, Response

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)

mcp_server = Server("sovereign-pair-mcp")

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """Exposição das capacidades da IA Soberana para a rede via MCP Tools."""
    return [
        Tool(
            name="the_doctor_query",
            description="Executa um prompt complexo com o Agente Especialista (The Doctor). Útil para código ou análise profunda de regras.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "A pergunta ou comando para o agente."}
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="the_nurse_search",
            description="Pesquisa no banco de dados vetorial Sovereign Vault e retorna o texto puro (RAG) sem edição. Útil para extração de fatos.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "O termo ou frase a ser pesquisado semanticamente."}
                },
                "required": ["query"]
            }
        )
    ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Intercepta as chamadas do N8N ou clientes corporativos via MCP."""
    if name == "the_nurse_search":
        try:
            from src.core.the_dad import VectorStoreManager
            query = arguments.get("query")
            if not query:
                return [TextContent(type="text", text="Erro: 'query' é obrigatória.")]
                
            vs = VectorStoreManager(tenant_id="default")
            results = vs.similarity_search(query, k=3)
            if not results:
                return [TextContent(type="text", text="Nenhuma informação encontrada no Sovereign Vault.")]
                
            combined = "\n\n---\n\n".join([r.page_content for r in results])
            return [TextContent(type="text", text=f"Contexto Recuperado:\n{combined}")]
        except Exception as e:
            logger.error(f"[MCP Nurse] Error: {e}")
            return [TextContent(type="text", text=f"Erro fatal executando The Nurse: {str(e)}")]

    elif name == "the_doctor_query":
        try:
            from src.llm_factory import get_llm
            from llama_index.core.base.llms.types import ChatMessage, MessageRole
            
            prompt = arguments.get("prompt")
            llm = get_llm("ollama", os.getenv("LLM_MODEL", "qwen2.5"), temperature=0.1)
            
            messages = [
                ChatMessage(role=MessageRole.SYSTEM, content="Você é The Doctor, agente especialista rodando sobre o Model Context Protocol (MCP). Baseie-se apenas em fatos. Seja conciso."),
                ChatMessage(role=MessageRole.USER, content=prompt)
            ]
            response = llm.chat(messages)
            return [TextContent(type="text", text=response.message.content)]
        except Exception as e:
            logger.error(f"[MCP Doctor] Error: {e}")
            return [TextContent(type="text", text=f"Erro fatal executando The Doctor: {str(e)}")]
            
    return [TextContent(type="text", text=f"Tool não mapeada: {name}")]

def mount_mcp_server(app):
    """Acopla o Transportador SSE do Anthropic MCP como Servidor dentro da instância FastAPI (Starlette)."""
    
    # Rota absoluta de callback que o MCP envia as mensagens (/mcp/messages)
    sse_transport = SseServerTransport("/mcp/messages")
    
    @app.get("/mcp/sse")
    async def mcp_setup_sse(request: Request):
        """Endpoint para iniciar hand-shake Server-Sent Events do MCP."""
        try:
            async with sse_transport.connect_sse(request.scope, request.receive, request._send) as sse:
                await mcp_server.run(sse, mcp_server.create_initialization_options())
        except BaseException:
            # Em ASGI, exceptions de streamings são comuns no disconnect do cliente (CancelledError)
            pass

    @app.post("/mcp/messages")
    async def mcp_receive_message(request: Request):
        """Endpoint onde clientes MCP batem os POSTs da sessão."""
        await sse_transport.handle_post_message(request.scope, request.receive, request._send)
        return Response(status_code=202)
