mod api;
mod models;

use axum::{routing::post, Router};
use reqwest::Client;
use std::sync::Arc;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

// Estado Global (Músculo Cíbrido) compartilhado entre Threads
pub struct AppState {
    pub http_client: Client,
}

#[tokio::main]
async fn main() {
    // Inicializa a Telemetria (Logs avançados estilo Uvicorn)
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "sovereign_core=debug,axum=debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    tracing::info!("🦀 Sovereign Core (Rust) Initializing...");

    // Cria o Roteador Axum (A fundação dos Cíbridos)
    let state = Arc::new(AppState {
        http_client: Client::new(),
    });

    let app = Router::new()
        .route("/opencode/v1/chat/completions", post(api::chat_completions_handler))
        .with_state(state);

    // Configura o TcpListener (Roda na porta 8001 para não colidir com o FastAPI se estiver aberto)
    let listener = tokio::net::TcpListener::bind("127.0.0.1:8001")
        .await
        .unwrap();
    
    tracing::info!("🚀 Core Listening on {}", listener.local_addr().unwrap());
    
    // Inicia o Servidor Nativo
    axum::serve(listener, app).await.unwrap();
}
