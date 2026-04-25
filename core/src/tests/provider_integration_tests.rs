#[cfg(test)]
mod tests {
    use crate::db::init_pool;
    use sqlx::Row;
    use axum::extract::State;
    use axum::Json;
    use std::sync::Arc;
    use crate::AppState;
    use serde_json::json;
    use crate::models::{QwenSettings, NvidiaSettings};
    use axum::response::IntoResponse;

    async fn setup_mock_state() -> Arc<AppState> {
        let pool = init_pool().await;
        Arc::new(AppState {
            http_client: reqwest::Client::new(),
            vault_path: std::path::PathBuf::from("/tmp"),
            telemetry: Arc::new(std::sync::RwLock::new(crate::telemetry::TelemetryState::new())),
            log_sender: tokio::sync::broadcast::channel(1).0,
            sync_sender: tokio::sync::broadcast::channel(1).0,
            db: pool,
            adblock_engine: crate::adblocker::AdblockHandle::mock(),
            health: crate::health_gate::new_health_state(),
        })
    }

    #[tokio::test]
    async fn test_qwen_settings_persistence_cycle() {
        let state = setup_mock_state().await;
        
        let payload = QwenSettings {
            api_key: "qwen-secret-key".to_string(),
            enabled: true,
            default_model: "qwen-max-test".to_string()
        };

        // Save
        let _ = crate::api_settings::set_qwen_settings_handler(
            State(state.clone()),
            Json(payload)
        ).await;

        // Load
        let response = crate::api_settings::get_qwen_settings_handler(
            State(state.clone())
        ).await;

        let body = axum::body::to_bytes(response.into_response().into_body(), 10000).await.unwrap();
        let json_res: serde_json::Value = serde_json::from_slice(&body).unwrap();
        
        assert_eq!(json_res["api_key"], "qwen-secret-key");
        assert_eq!(json_res["enabled"], true);
        assert_eq!(json_res["default_model"], "qwen-max-test");

        // Verify DB contains ENCRYPTED key
        let row = sqlx::query("SELECT value_json FROM global_settings WHERE id = 'qwen'")
            .fetch_one(&state.db)
            .await
            .unwrap();
        let db_val: String = row.get("value_json");
        assert!(!db_val.contains("qwen-secret-key"), "A chave API não deveria estar em texto plano no banco");

        println!("✅ Qwen settings persistence cycle validated (KMS + DB)");
    }

    #[tokio::test]
    async fn test_nvidia_settings_persistence_cycle() {
        let state = setup_mock_state().await;
        
        let payload = NvidiaSettings {
            api_key: "nvidia-secret-key".to_string(),
            enabled: true,
            default_model: "nvidia/llama-3-test".to_string()
        };

        // Save
        let _ = crate::api_settings::set_nvidia_settings_handler(
            State(state.clone()),
            Json(payload)
        ).await;

        // Load
        let response = crate::api_settings::get_nvidia_settings_handler(
            State(state.clone())
        ).await;

        let body = axum::body::to_bytes(response.into_response().into_body(), 10000).await.unwrap();
        let json_res: serde_json::Value = serde_json::from_slice(&body).unwrap();
        
        assert_eq!(json_res["api_key"], "nvidia-secret-key");
        assert_eq!(json_res["enabled"], true);
        assert_eq!(json_res["default_model"], "nvidia/llama-3-test");

        // Verify DB contains ENCRYPTED key
        let row = sqlx::query("SELECT value_json FROM global_settings WHERE id = 'nvidia'")
            .fetch_one(&state.db)
            .await
            .unwrap();
        let db_val: String = row.get("value_json");
        assert!(!db_val.contains("nvidia-secret-key"), "A chave API não deveria estar em texto plano no banco");

        println!("✅ NVIDIA settings persistence cycle validated (KMS + DB)");
    }
}
