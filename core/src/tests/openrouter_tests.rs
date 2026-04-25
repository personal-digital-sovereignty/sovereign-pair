#[cfg(test)]
mod tests {
    use crate::db::init_pool;
    use sqlx::Row;

    #[tokio::test]
    async fn test_openrouter_settings_initialization() {
        // Inicializa o pool (que roda as migrações)
        let pool = init_pool().await;

        // Verifica se a entrada do OpenRouter existe em global_settings
        let row = sqlx::query("SELECT value_json FROM global_settings WHERE id = 'openrouter'")
            .fetch_one(&pool)
            .await
            .expect("Falha ao buscar configurações do OpenRouter no banco");

        let value_json: String = row.get("value_json");
        assert!(value_json.contains("https://openrouter.ai/api/v1"), "Base URL incorreta no banco");
        assert!(value_json.contains("\"enabled\": false"), "Enabled deveria ser false por padrão");
        
        println!("✅ OpenRouter settings validated in DB");
    }

    #[tokio::test]
    async fn test_openrouter_api_handlers() {
        use axum::extract::State;
        use axum::Json;
        use std::sync::Arc;
        use crate::AppState;
        use serde_json::json;

        let pool = init_pool().await;
        
        // Mock AppState
        let state = Arc::new(AppState {
            http_client: reqwest::Client::new(),
            vault_path: std::path::PathBuf::from("/tmp"),
            telemetry: Arc::new(std::sync::RwLock::new(crate::telemetry::TelemetryState::new())),
            log_sender: tokio::sync::broadcast::channel(1).0,
            sync_sender: tokio::sync::broadcast::channel(1).0,
            db: pool.clone(),
            adblock_engine: crate::adblocker::AdblockHandle::mock(),
            health: crate::health_gate::new_health_state(),
        });

        // Test POST (Save)
        let payload = json!({
            "api_key": "sk-or-test-key",
            "enabled": true,
            "default_model": "test-model"
        });
        
        let response = crate::api_settings::set_openrouter_settings_handler(
            State(state.clone()),
            Json(payload)
        ).await;

        // Verifica se salvou (indiretamente via GET)
        let get_response = crate::api_settings::get_openrouter_settings_handler(
            State(state.clone())
        ).await;
        
        // Converte a resposta em JSON para validar
        use axum::response::IntoResponse;
        let body = axum::body::to_bytes(get_response.into_response().into_body(), 10000).await.unwrap();
        let json_res: serde_json::Value = serde_json::from_slice(&body).unwrap();
        
        assert_eq!(json_res["api_key"], "sk-or-test-key", "API Key não foi decifrada corretamente");
        assert_eq!(json_res["enabled"], true);
        assert_eq!(json_res["default_model"], "test-model");

        println!("✅ OpenRouter API handlers validated (Encryption/Decryption cycle OK)");
    }
}
