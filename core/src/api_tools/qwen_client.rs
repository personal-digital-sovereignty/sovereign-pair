use reqwest::Client;
use reqwest_eventsource::{Event, EventSource, RequestBuilderExt};
use crate::models::{QwenRequest, QwenInput, QwenParameters, OpenAIChatMessage, OpenAIChatChunkResponse, OpenAIChatChunkChoice, OpenAITokenUsage, OpenAIChatChunkDelta};
use anyhow::Result;
use serde_json::Value;

pub struct QwenClient {
    client: Client,
    api_key: String,
}

impl QwenClient {
    pub fn new(api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_key,
        }
    }

    /// Stream completions using DashScope API
    pub async fn stream_chat_completions(
        &self,
        model: String,
        messages: Vec<OpenAIChatMessage>,
        temperature: Option<f32>,
        max_tokens: Option<i32>,
    ) -> Result<EventSource> {
        let request = QwenRequest {
            model,
            input: QwenInput { messages },
            parameters: Some(QwenParameters {
                result_format: Some("message".to_string()),
                incremental_output: Some(true),
                temperature,
                max_tokens,
                ..Default::default()
            }),
        };

        let event_source = self.client
            .post("https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header("X-DashScope-SSE", "enable")
            .json(&request)
            .eventsource()?;

        Ok(event_source)
    }

    /// Transform DashScope SSE event to OpenAI compatible chunk
    pub fn transform_event(&self, event: Event) -> Option<OpenAIChatChunkResponse> {
        if let Event::Message(msg) = event {
            if msg.data == "[DONE]" {
                return None;
            }

            if let Ok(data) = serde_json::from_str::<Value>(&msg.data) {
                // DashScope structure: { "output": { "choices": [ { "message": { "content": "...", "role": "assistant" }, "finish_reason": "..." } ] }, "usage": { ... }, "request_id": "..." }
                // Note: with incremental_output=true, content only contains the delta.
                
                let output = data.get("output")?;
                let choices_val = output.get("choices")?;
                let usage_val = data.get("usage");

                let mut choices = Vec::new();
                if let Some(arr) = choices_val.as_array() {
                    for (i, c) in arr.iter().enumerate() {
                        let msg_val = c.get("message")?;
                        let content = msg_val.get("content").and_then(|v| v.as_str()).unwrap_or("");
                        let role = msg_val.get("role").and_then(|v| v.as_str()).unwrap_or("assistant");
                        let finish_reason = c.get("finish_reason").and_then(|v| v.as_str()).map(|s| s.to_string());

                        choices.push(OpenAIChatChunkChoice {
                            index: i as i32,
                            delta: OpenAIChatChunkDelta {
                                role: Some(role.to_string()),
                                content: Some(content.to_string()),
                                tool_calls: None,
                            },
                            finish_reason,
                        });
                    }
                }

                let usage = usage_val.map(|u| OpenAITokenUsage {
                    prompt_tokens: u.get("input_tokens").and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                    completion_tokens: u.get("output_tokens").and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                    total_tokens: u.get("total_tokens").and_then(|v| v.as_i64()).unwrap_or(0) as i32,
                });

                return Some(OpenAIChatChunkResponse {
                    id: data.get("request_id").and_then(|v| v.as_str()).unwrap_or("qwen-req").to_string(),
                    object: "chat.completion.chunk".to_string(),
                    created: chrono::Utc::now().timestamp(),
                    model: "qwen".to_string(),
                    choices,
                    usage,
                });
            }
        }
        None
    }
}
