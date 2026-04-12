use crate::api_trainer::TRAINER_LOGS;

pub async fn fire_eviction_protocol(model_name: &str) {
    let base_url = std::env::var("OLLAMA_BASE_URL").unwrap_or_else(|_| "http://127.0.0.1:11434".to_string());
    let endpoint = format!("{}/api/generate", base_url);
    
    // Aumentando o timeout para 10s: Garantindo que o motor do Ollama receba o pacote e execute a limpeza em paz.
    // Como a execução já acontece em um tokio::spawn paralelo, não afeta a latência do usuário.
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(10))
        .build()
        .unwrap_or_else(|_| reqwest::Client::new());

    // É boa prática passar um prompt vazio quando forçamos keep_alive: 0 na api/generate.
    let payload = serde_json::json!({
        "model": model_name,
        "prompt": "",
        "keep_alive": 0
    });

    let _ = TRAINER_LOGS.send(format!("⚡ Sovereign Swap Ativo: Evicting '{}' da VRAM para isolamento cognitivo.", model_name));

    // Dispara via background sem bloquear a pipeline sincrona.
    tokio::spawn(async move {
        let _ = client.post(&endpoint).json(&payload).send().await;
    });
}
