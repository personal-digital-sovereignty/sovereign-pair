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
}
