use std::path::{Path, PathBuf};
use serde_json::json;

/// Retorna os Schemas da OpenAI / Vercel SDK convertidos das extensões do Model Context Protocol
/// Que o Cíbrido suportará em modo nativo via OS.
pub fn get_mcp_tools() -> Vec<serde_json::Value> {
    vec![
        json!({
            "type": "function",
            "function": {
                "name": "mcp_list_directory",
                "description": "[MCP] Lista os arquivos e pastas dentro de um diretório protegido.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": { "type": "string", "description": "Caminho relativo ou absoluto" }
                    },
                    "required": ["path"]
                }
            }
        }),
        json!({
            "type": "function",
            "function": {
                "name": "mcp_read_file",
                "description": "[MCP] Carrega o conteúdo extraído em texto de um arquivo interno.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": { "type": "string", "description": "Caminho do arquivo a ser lido" }
                    },
                    "required": ["path"]
                }
            }
        }),
        json!({
            "type": "function",
            "function": {
                "name": "mcp_write_file",
                "description": "[MCP] Modifica ou cria um arquivo local no disco de forma determinística.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": { "type": "string", "description": "Diretório e nome do arquivo" },
                        "content": { "type": "string", "description": "O Código bruto ou texto a ser implementado" }
                    },
                    "required": ["path", "content"]
                }
            }
        })
    ]
}

/// A "Sandbox Layer": Garante que o Agente não tente escapar do /home/user/workspace especificado
fn validate_safe_path(vault_root: &Path, target: &str) -> std::io::Result<PathBuf> {
    let mut resolved = vault_root.to_path_buf();
    let target_path = Path::new(target);
    
    if target_path.is_absolute() {
        if target_path.starts_with(vault_root) {
            resolved = target_path.to_path_buf();
        } else {
             return Err(std::io::Error::new(std::io::ErrorKind::PermissionDenied, "MCP Security Violation: Filepath Root Escaping Locked."));
        }
    } else {
        resolved.push(target);
    }
    
    // Normalização canônica (evita payloads tipo `../../etc/passwd`)
    if let Ok(canon) = std::fs::canonicalize(&resolved) {
        if canon.starts_with(vault_root) {
            return Ok(canon);
        }
    } else {
         // O arquivo pode não existir ainda (No caso do mcp_write_file). 
         // Validamos apenas se a pasta PAI do arquivo novo está permitida.
         if let Some(parent) = resolved.parent() {
             if let Ok(canon_parent) = std::fs::canonicalize(parent) {
                 if canon_parent.starts_with(vault_root) {
                     return Ok(resolved);
                 }
             }
         }
    }
    
    Err(std::io::Error::new(std::io::ErrorKind::PermissionDenied, "MCP Security Violation: Path unresolvable inside restricted scope."))
}

/// Resolutor unificado (O Executante) de todas as capacidades MCP providenciadas ao Ollama  
pub async fn execute_mcp_tool(vault_root: &Path, tool_name: &str, args: &serde_json::Value) -> String {
    match tool_name {
        "mcp_list_directory" => {
            let path_str = args.get("path").and_then(|v| v.as_str()).unwrap_or("");
            match validate_safe_path(vault_root, path_str) {
                Ok(safe_path) => {
                    match std::fs::read_dir(&safe_path) {
                        Ok(entries) => {
                            let mut results = Vec::new();
                            for entry in entries.flatten() {
                                let name = entry.file_name().to_string_lossy().to_string();
                                let tag = if entry.path().is_dir() { "[DIR]" } else { "[FILE]" };
                                results.push(format!("{} {}", tag, name));
                            }
                            format!("Directory Listing of {}:\n{}", path_str, results.join("\n"))
                        },
                        Err(e) => format!("MCP Error reading directory: {}", e)
                    }
                },
                Err(e) => format!("MCP Access Error: {}", e)
            }
        },
        "mcp_read_file" => {
            let path_str = args.get("path").and_then(|v| v.as_str()).unwrap_or("");
            match validate_safe_path(vault_root, path_str) {
                Ok(safe_path) => {
                    std::fs::read_to_string(&safe_path).unwrap_or_else(|e| format!("MCP Error reading file: {}", e))
                },
                Err(e) => format!("MCP Access Error: {}", e)
            }
        },
        "mcp_write_file" => {
            let path_str = args.get("path").and_then(|v| v.as_str()).unwrap_or("");
            let content = args.get("content").and_then(|v| v.as_str()).unwrap_or("");
            match validate_safe_path(vault_root, path_str) {
                Ok(safe_path) => {
                    match std::fs::write(&safe_path, content) {
                        Ok(_) => format!("Success. The Content was safely injected at {}.", path_str),
                        Err(e) => format!("MCP Error writing file: {}", e)
                    }
                },
                Err(e) => format!("MCP Access Error: {}", e)
            }
        },
        _ => format!("MCP Tool unrecognized by Engine: {}", tool_name)
    }
}
