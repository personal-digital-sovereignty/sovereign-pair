use reqwest::Client;
use reqwest_eventsource::{EventSource, RequestBuilderExt};
use crate::models::{OpenAIChatRequest, OpenAIChatMessage};
use anyhow::Result;

pub struct NvidiaClient {
    client: Client,
    api_key: String,
    base_url: String,
}

impl NvidiaClient {
    pub fn new(api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_key,
            base_url: "https://integrate.api.nvidia.com/v1".to_string(),
        }
    }

    /// Stream completions using NVIDIA NIM API (OpenAI Compatible)
    pub async fn stream_chat_completions(
        &self,
        model: String,
        messages: Vec<OpenAIChatMessage>,
        temperature: Option<f32>,
        max_tokens: Option<i32>,
    ) -> Result<EventSource> {
        let payload = OpenAIChatRequest {
            model,
            messages,
            stream: Some(true),
            temperature,
            max_tokens,
            ..Default::default()
        };

        let event_source = self.client
            .post(format!("{}/chat/completions", self.base_url))
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header("Accept", "text/event-stream")
            .json(&payload)
            .eventsource()?;

        Ok(event_source)
    }
}
