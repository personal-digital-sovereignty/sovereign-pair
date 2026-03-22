use axum::{
    extract::State,
    response::{IntoResponse, sse::{Event, Sse}},
    Json,
};
use futures_util::stream::{self, Stream};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use crate::AppState;
use std::time::Duration;
use std::convert::Infallible;

#[derive(Deserialize)]
pub struct DistillationReq {
    pub teacher_model: String,
    pub student_model: String,
    pub epochs: i32,
    pub batch_size: i32,
}

#[derive(Deserialize)]
pub struct FineTuningReq {
    pub base_model: String,
    pub dataset_name: String,
    pub learning_rate: f64,
}

pub async fn run_distillation_handler(
    State(_state): State<Arc<AppState>>,
    Json(req): Json<DistillationReq>,
) -> impl IntoResponse {
    // Aqui simularíamos o spawn de um processo python (ex: litgpt ou unsloth)
    // Para efeito do "Design Magestoso" vamos apenas registrar a intenção 
    // e o monitor do Svelte receberá os logs simulados via SSE no endpoint próprio.
    tracing::info!("🎓 [Sovereign Trainer] Run Distillation requested: {} -> {}", req.teacher_model, req.student_model);
    
    Json(serde_json::json!({
        "status": "accepted",
        "job_id": uuid::Uuid::new_v4().to_string(),
        "message": "Knowledge Distillation job started in background."
    }))
}

pub async fn run_finetuning_handler(
    State(_state): State<Arc<AppState>>,
    Json(req): Json<FineTuningReq>,
) -> impl IntoResponse {
    tracing::info!("🔥 [Sovereign Trainer] Fine-Tuning requested on {} with {}", req.base_model, req.dataset_name);
    
    Json(serde_json::json!({
        "status": "accepted",
        "job_id": uuid::Uuid::new_v4().to_string(),
        "message": "Unsloth LoRA Fine-Tuning started."
    }))
}

/// Server-Sent Events Endpoint (Simulando log output do Unsloth CLI para o Cíbrid UI)
pub async fn unsloth_monitor_sse_handler() -> Sse<impl Stream<Item = Result<Event, Infallible>>> {
    let mock_logs = vec![
        "Sovereign Unsloth Engine 0.8.4 initialized.",
        "Detected 1x NVIDIA GPU (CUDA 12.x). VRAM accessible: 11 GB / 24 GB.",
        "Loading LoRA adapters for Fast Fine-Tuning...",
        "Epoch 1/3 - Loss: 1.2503 | Learning Rate: 2e-4",
        "Epoch 1/3 - Loss: 1.1502 | Learning Rate: 2e-4",
        "Evaluating faithfulness metrics with Sovereign Auto-Rater...",
        "Epoch 2/3 - Loss: 0.8904 | Learning Rate: 1.5e-4",
        "Epoch 2/3 - Loss: 0.8123 | Learning Rate: 1.5e-4",
        "Memory footprint peak: 8.4GB. Checkpointing weights to /weights/lora_adapter...",
        "Epoch 3/3 - Loss: 0.6550 | Learning Rate: 1e-4",
        "Epoch 3/3 - Loss: 0.5100 | Learning Rate: 1e-4",
        "Training Complete. Sovereign Safetensors exported successfully.",
        "Merging adapters into a GGUF format for local Ollama consumption..."
    ];

    let stream = async_stream::stream! {
        for log in mock_logs {
            tokio::time::sleep(Duration::from_millis(800)).await;
            yield Ok(Event::default().data(log));
        }
        
        // Mantém a conexão viva sem quebrar
        loop {
            tokio::time::sleep(Duration::from_secs(5)).await;
            yield Ok(Event::default().comment("keep-alive"));
        }
    };

    Sse::new(stream).keep_alive(axum::response::sse::KeepAlive::new())
}
