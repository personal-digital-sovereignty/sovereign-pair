import sys
import json
import logging
from src.config import VAULT_DIR
import os

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("mcp_server")

def handle_sensus_project_context(params):
    project = params.get("project_name", "default")
    tree = {}
    
    if os.path.exists(VAULT_DIR):
        for root, dirs, files in os.walk(VAULT_DIR):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            rel_path = os.path.relpath(root, VAULT_DIR)
            if rel_path == '.':
                tree['/'] = files
            else:
                tree[rel_path] = files
                
    return {
        "project": project,
        "mode": "stdio",
        "context7_depth": "Layer 3 (File Tree Map)",
        "tree": tree
    }

def handle_sensus_vault_search(params):
    query = params.get("query", "")
    return {
        "result": f"Busca local stdio recebida para '{query}'. Conectando ao Banco Vetorial..."
    }

def main():
    logger.info("Initializing Sovereign Pair MCP Stdio Server...")
    
    # Simple JSON-RPC or line-based JSON stdio loop
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            req = json.loads(line)
            tool_name = req.get("tool")
            params = req.get("parameters", {})
            
            if tool_name == "sensus_project_context":
                result = handle_sensus_project_context(params)
            elif tool_name == "sensus_vault_search":
                result = handle_sensus_vault_search(params)
            else:
                result = {"error": f"Tool {tool_name} not found"}
                
            # Respond back to stdout
            print(json.dumps({"response": result}), flush=True)
            
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from stdin.")
            print(json.dumps({"error": "Invalid JSON"}), flush=True)

if __name__ == "__main__":
    main()
