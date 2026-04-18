use std::path::PathBuf;
use std::fs;
use std::env;
use tracing::{info, warn};
use serde_json::{json, Value};
use sqlx::{SqlitePool, Row};
use std::path::Path;

/// Inicializa a arquitetura flexível do Vault baseada em Segurança Isolada (Airgap).
/// Agora utilizado apenas para inicializar o banco como 'Origin Vault'.
pub fn init_vault() -> PathBuf {
    let vault_path = env::var("SOVEREIGN_VAULT_PATH")
        .map(PathBuf::from)
        .unwrap_or_else(|_| {
            // P2-02: graceful fallback — sem panics
            dirs::home_dir()
                .or_else(|| {
                    warn!("⚠️ [Sovereign RAG] HOME dir não detectado. Usando diretório atual como Vault.");
                    std::env::current_dir().ok()
                })
                .unwrap_or_else(|| PathBuf::from("."))
                .join("Vault")
        });

    if !vault_path.exists() {
        info!("📦 [Sovereign RAG] Gerando Vault Físico (Airgap) em: {:?}", vault_path);
        // P2-02: .expect() -> graceful match
        if let Err(e) = fs::create_dir_all(&vault_path) {
            warn!("⚠️ [Sovereign RAG] Não foi possível criar o Vault em {:?}: {}. Operando sem persistência física.", vault_path, e);
        }
    } else {
        info!("📦 [Sovereign RAG] Vault Localizador Ativo em: {:?}", vault_path);
    }

    vault_path
}

/// Parseador de Alta Performance em BD (Abstração Zero de FS).
/// Varre os resumos semânticos no SQLite para o Workspace ativo em milissegundos evitando Context Bombing.
pub async fn parse_vault_documents(workspace_id: &str, db: &SqlitePool) -> String {
    let mut combined_knowledge = String::new();
    let mut doc_count = 0;

    // Realiza query apenas dos documentos vinculados ao Workspace
    if let Ok(rows) = sqlx::query("SELECT file_path, summary, content_raw FROM sensus_documents WHERE workspace_id = ?")
        .bind(workspace_id)
        .fetch_all(db)
        .await 
    {
        for row in rows {
            let file_path: String = row.try_get("file_path").unwrap_or_default();
            let summary: String = row.try_get("summary").unwrap_or_default();
            let raw_content: String = row.try_get("content_raw").unwrap_or_default();
            
            let filename = Path::new(&file_path).file_name().unwrap_or_default().to_string_lossy();
            
            // Limitador de Profiling Crítico: Evitar OOM/Context Bombing no Servidor
            // O Vault inteiro (ex: 5MB) jamais deve ir cruçado no System Prompt.
            let snippet = if !summary.is_empty() {
                summary
            } else {
                let safe_trunc: String = raw_content.chars().take(2000).collect();
                format!("{}... (truncado)", safe_trunc)
            };
            
            if combined_knowledge.len() < 16000 {
                combined_knowledge.push_str(&format!("\n\n--- Documento: {} ---\n{}\n", filename, snippet));
                doc_count += 1;
            } else {
                warn!("⚠️ [Sovereign RAG] Fim de memória de contexto estourado para LLM Inject.");
                break;
            }
        }
    }

    info!("🧠 [Sovereign RAG/DB] Indexou {} documentos do DB (Safe Limit) na memória no Workspace '{}'.", doc_count, workspace_id);
    combined_knowledge
}

/// Constrói o Córtex Sistêmico da IA (Injeção via System Prompt)
pub async fn build_rag_context_message(workspace_id: &str, db: &SqlitePool) -> Option<Value> {
    let knowledge = parse_vault_documents(workspace_id, db).await;
    if knowledge.trim().is_empty() {
        return None;
    }

    let sys_prompt = format!(
        "Sovereign Protocol Enforced. You operate on an Air-Gapped Local-First Architecture. \
         Below is the User's Digital Cortex (Physical Vault for Active Workspace). Treat it as the absolute source of truth:\n\n{}", 
        knowledge
    );

    Some(json!({
        "role": "system",
        "content": sys_prompt
    }))
}