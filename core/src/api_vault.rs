use axum::{
    extract::{Path as AxumPath, State},
    response::IntoResponse,
    Json,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use crate::AppState;
use std::path::{Path, PathBuf};
use tokio::fs;

#[derive(Serialize)]
pub struct VaultNode {
    pub id: String,
    pub filename: String,
    #[serde(rename = "is_dir")]
    pub is_dir: bool,
    pub r#type: String, // "file" or "directory"
    pub path: String,
    pub children: Vec<VaultNode>,
}

/// Escaneia recursivamente o FileSystem nativo do Rust
#[async_recursion::async_recursion]
async fn scan_directory(path: &Path, root_path: &Path) -> Vec<VaultNode> {
    let mut nodes = Vec::new();

    if let Ok(mut entries) = fs::read_dir(path).await {
        while let Ok(Some(entry)) = entries.next_entry().await {
            let metadata = entry.metadata().await;
            if metadata.is_err() { continue; }
            let metadata = metadata.unwrap();

            let filename = entry.file_name().to_string_lossy().to_string();
            
            // Ignorar ocultos/sistemas
            if filename.starts_with('.') || filename.ends_with('~') { continue; }

            let abs_path = entry.path();
            // Id relativo para a navegação do Vue
            let rel_id = abs_path.strip_prefix(root_path).unwrap_or(&abs_path).to_string_lossy().to_string();

            if metadata.is_dir() {
                let children = scan_directory(&abs_path, root_path).await;
                nodes.push(VaultNode {
                    id: rel_id.clone(),
                    filename,
                    is_dir: true,
                    r#type: "directory".to_string(),
                    path: abs_path.to_string_lossy().to_string(),
                    children,
                });
            } else {
                nodes.push(VaultNode {
                    id: rel_id.clone(),
                    filename,
                    is_dir: false,
                    r#type: "file".to_string(),
                    path: abs_path.to_string_lossy().to_string(),
                    children: vec![],
                });
            }
        }
    }

    // Ordenar: Pastas Primeiro, depois Arquivos alfabeticamente
    nodes.sort_by(|a, b| {
        if a.r#type == b.r#type {
            a.filename.cmp(&b.filename)
        } else if a.r#type == "directory" {
            std::cmp::Ordering::Less
        } else {
            std::cmp::Ordering::Greater
        }
    });

    nodes
}

/// Rota GET /v1/vault/tree - Varredura Brutal e Instantânea do Disco
pub async fn vault_tree_handler(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    let root = state.vault_path.clone();
    
    // Constrói a Arvore Assincronamente 
    let children = scan_directory(&root, &root).await;

    // A raiz do diretório pro Front Vue
    let root_node = VaultNode {
        id: "root".to_string(),
        filename: "The Vault O.S".to_string(),
        is_dir: true,
        r#type: "directory".to_string(),
        path: root.to_string_lossy().to_string(),
        children,
    };

    Json(vec![root_node]).into_response()
}

/// Rota GET /v1/vault/document/:id - Leitura direta do O.S Binário
pub async fn vault_document_read(
    AxumPath(file_id): AxumPath<String>,
    State(state): State<Arc<AppState>>
) -> impl IntoResponse {
    // Decodifica a URL String e monta no Root
    let decoded_id = urlencoding::decode(&file_id).unwrap_or(std::borrow::Cow::Borrowed(&file_id)).to_string();
    let abs_path = state.vault_path.join(&decoded_id);

    match fs::read_to_string(&abs_path).await {
        Ok(content) => {
            let res = serde_json::json!({
                "id": decoded_id,
                "file_path": abs_path.to_string_lossy().to_string(),
                "content": content,
            });
            Json(res).into_response()
        },
        Err(e) => {
            let err_res = serde_json::json!({
                "error": true,
                "message": format!("Sovereign OS File System Error: {}", e)
            });
            Json(err_res).into_response()
        }
    }
}

// ------------------- CRUD MUTATIONS -------------------

#[derive(Deserialize)]
pub struct FsCreateReq {
    pub r#type: String, // "folder" or "file"
    pub name: String,
    pub path: String,
}

pub async fn vault_fs_create_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<FsCreateReq>,
) -> impl IntoResponse {
    let parent = if req.path.is_empty() {
        state.vault_path.clone()
    } else {
        PathBuf::from(&req.path)
    };
    
    if !parent.starts_with(&state.vault_path) {
        return (axum::http::StatusCode::FORBIDDEN, Json(serde_json::json!({"detail":"Path manipulation prevented"}))).into_response();
    }
    
    let target = parent.join(&req.name);

    if req.r#type == "folder" {
        if let Err(e) = fs::create_dir_all(&target).await {
            return (axum::http::StatusCode::INTERNAL_SERVER_ERROR, Json(serde_json::json!({"detail": format!("Failed to create folder: {}", e)}))).into_response();
        }
    } else {
        if let Err(e) = fs::File::create(&target).await {
            return (axum::http::StatusCode::INTERNAL_SERVER_ERROR, Json(serde_json::json!({"detail": format!("Failed to create file: {}", e)}))).into_response();
        }
    }

    (axum::http::StatusCode::OK, Json(serde_json::json!({"status":"created"}))).into_response()
}

#[derive(Deserialize)]
pub struct FsRenameReq {
    pub path: String,
    pub new_name: String,
}

pub async fn vault_fs_rename_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<FsRenameReq>,
) -> impl IntoResponse {
    let current = PathBuf::from(&req.path);
    if !current.starts_with(&state.vault_path) {
        return (axum::http::StatusCode::FORBIDDEN, Json(serde_json::json!({"detail":"Path manipulation prevented"}))).into_response();
    }

    let parent = current.parent().unwrap_or(&state.vault_path);
    let target = parent.join(&req.new_name);

    if let Err(e) = fs::rename(&current, &target).await {
        return (axum::http::StatusCode::INTERNAL_SERVER_ERROR, Json(serde_json::json!({"detail": format!("Failed to rename: {}", e)}))).into_response();
    }

    (axum::http::StatusCode::OK, Json(serde_json::json!({"status":"renamed"}))).into_response()
}

#[derive(Deserialize)]
pub struct FsDeleteReq {
    pub path: String,
}

pub async fn vault_fs_delete_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<FsDeleteReq>,
) -> impl IntoResponse {
    let target = PathBuf::from(&req.path);
    if !target.starts_with(&state.vault_path) {
        return (axum::http::StatusCode::FORBIDDEN, Json(serde_json::json!({"detail":"Path manipulation prevented"}))).into_response();
    }

    let metadata = match fs::metadata(&target).await {
        Ok(m) => m,
        Err(e) => return (axum::http::StatusCode::NOT_FOUND, Json(serde_json::json!({"detail": format!("File/Folder not found: {}", e)}))).into_response(),
    };

    if metadata.is_dir() {
        if let Err(e) = fs::remove_dir_all(&target).await {
            return (axum::http::StatusCode::INTERNAL_SERVER_ERROR, Json(serde_json::json!({"detail": format!("Failed to delete folder: {}", e)}))).into_response();
        }
    } else {
        if let Err(e) = fs::remove_file(&target).await {
            return (axum::http::StatusCode::INTERNAL_SERVER_ERROR, Json(serde_json::json!({"detail": format!("Failed to delete file: {}", e)}))).into_response();
        }
    }

    (axum::http::StatusCode::OK, Json(serde_json::json!({"status":"deleted"}))).into_response()
}

#[derive(Deserialize)]
pub struct WriteDocReq {
    pub content: String,
}

pub async fn vault_document_write(
    AxumPath(file_id): AxumPath<String>,
    State(state): State<Arc<AppState>>,
    Json(req): Json<WriteDocReq>,
) -> impl IntoResponse {
    let decoded_id = urlencoding::decode(&file_id).unwrap_or(std::borrow::Cow::Borrowed(&file_id)).to_string();
    let abs_path = if Path::new(&decoded_id).is_absolute() {
        PathBuf::from(&decoded_id)
    } else {
        state.vault_path.join(&decoded_id)
    };

    if !abs_path.starts_with(&state.vault_path) {
        return (axum::http::StatusCode::FORBIDDEN, Json(serde_json::json!({"detail":"Path manipulation prevented"}))).into_response();
    }

    if let Err(e) = fs::write(&abs_path, req.content).await {
        return (axum::http::StatusCode::INTERNAL_SERVER_ERROR, Json(serde_json::json!({"detail": format!("Failed to write to file: {}", e)}))).into_response();
    }

    (axum::http::StatusCode::OK, Json(serde_json::json!({"status":"saved"}))).into_response()
}
