import asyncio
import sys
import logging
import os

# Ajustar PYTHONPATH para rodar direto do diretório raiz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.mcp_server import mcp_server

# Desabilitar logs na saída padrão STDOUT que quebrariam o protocolo JSON-RPC.
# Todos os logs agora vão para STDERR.
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    logger.info("Iniciando Sovereign Pair MCP Server no modo STDIO (Standard IO Transport)...")
    
    # Importar modulo Stdio apenas quando necessário
    from mcp.server.stdio import stdio_server
    
    try:
        # A sintaxe de inicialização nativa do mcp-python sdk via stdio
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Transporter STDIO conectado. Escutando requisições do Client (VSCode/Cline) no formato JSON-RPC...")
            await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())
    except Exception as e:
        logger.error(f"Erro fatal executando protocolo MCP via STDIO: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
