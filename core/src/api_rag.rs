use axum::{extract::{Path, State}, Json};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use crate::AppState;
use sqlx::Row;

#[derive(Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct RoutingRule {
    pub id: String,
    pub name: String,
    pub target_model: String,
    pub latency_badge: String,
    pub icon: String,
    pub is_active: bool,
    pub order_index: i32,
}

#[derive(Deserialize)]
pub struct CreateRoutingRulePayload {
    pub name: String,
    pub target_model: String,
    pub latency_badge: String,
    pub icon: String,
}

#[derive(Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct RemoteModel {
    pub id: String,
    pub name: String,
    pub provider: String,
    pub icon_url: Option<String>,
    pub latency_ms: i32,
    pub cost_per_1k: f64,
    pub success_rate: f64,
    pub status: String,
}

#[derive(Deserialize)]
pub struct CreateRemoteModelPayload {
    pub name: String,
    pub provider: String,
    pub latency_ms: i32,
    pub cost_per_1k: f64,
}

#[derive(Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct KnowledgeGap {
    pub id: String,
    pub query: String,
    pub frequency: i32,
    pub context: String,
    pub sentiment: String,
}

#[derive(Serialize, Deserialize, Clone)]
pub struct RadarMetrics {
    pub global_score: i32,
    pub faithfulness: i32,
    pub precision: i32,
}

pub async fn get_routing_rules_handler(State(state): State<Arc<AppState>>) -> Json<Vec<RoutingRule>> {
    let rules = sqlx::query_as::<_, RoutingRule>(
        r#"SELECT id, name, target_model, latency_badge, icon, is_active, order_index FROM routing_rules ORDER BY order_index ASC"#
    )
    .fetch_all(&state.db)
    .await
    .unwrap_or_default();

    if rules.is_empty() {
        let default_rules = vec![
            RoutingRule {
                id: "1".to_string(),
                name: "Simples / Saudações".to_string(),
                target_model: "Llama-3 (Local/Rápido)".to_string(),
                latency_badge: "0.02s latency".to_string(),
                icon: "chat_bubble".to_string(),
                is_active: true,
                order_index: 0,
            },
            RoutingRule {
                id: "2".to_string(),
                name: "Complexo / Análise".to_string(),
                target_model: "GPT-4o / Claude 3.5 (Nuvem)".to_string(),
                latency_badge: "High Intelligence".to_string(),
                icon: "psychology".to_string(),
                is_active: true,
                order_index: 1,
            }
        ];
        
        for r in &default_rules {
            let _ = sqlx::query(
                "INSERT INTO routing_rules (id, name, target_model, latency_badge, icon, is_active, order_index) VALUES (?, ?, ?, ?, ?, ?, ?)"
            )
            .bind(&r.id)
            .bind(&r.name)
            .bind(&r.target_model)
            .bind(&r.latency_badge)
            .bind(&r.icon)
            .bind(r.is_active)
            .bind(r.order_index)
            .execute(&state.db).await;
        }
        return Json(default_rules);
    }
    Json(rules)
}

pub async fn create_routing_rule_handler(State(state): State<Arc<AppState>>, Json(payload): Json<CreateRoutingRulePayload>) -> Json<serde_json::Value> {
    let new_id = uuid::Uuid::new_v4().to_string();
    let order: (i32,) = sqlx::query_as("SELECT COALESCE(MAX(order_index), 0) + 1 FROM routing_rules").fetch_one(&state.db).await.unwrap_or((1,));
    
    let res = sqlx::query("INSERT INTO routing_rules (id, name, target_model, latency_badge, icon, is_active, order_index) VALUES (?, ?, ?, ?, ?, ?, ?)")
        .bind(&new_id)
        .bind(&payload.name)
        .bind(&payload.target_model)
        .bind(&payload.latency_badge)
        .bind(&payload.icon)
        .bind(true)
        .bind(order.0)
        .execute(&state.db).await;

    if res.is_ok() { Json(serde_json::json!({"success": true, "id": new_id})) } else { Json(serde_json::json!({"success": false})) }
}

pub async fn delete_routing_rule_handler(State(state): State<Arc<AppState>>, Path(id): Path<String>) -> Json<serde_json::Value> {
    let res = sqlx::query("DELETE FROM routing_rules WHERE id = ?").bind(id).execute(&state.db).await;
    if res.is_ok() { Json(serde_json::json!({"success": true})) } else { Json(serde_json::json!({"success": false})) }
}

pub async fn get_remote_models_handler(State(state): State<Arc<AppState>>) -> Json<Vec<RemoteModel>> {
    let models = sqlx::query_as::<_, RemoteModel>(
        r#"SELECT id, name, provider, icon_url, latency_ms, cost_per_1k, success_rate, status FROM remote_models ORDER BY cost_per_1k DESC"#
    )
    .fetch_all(&state.db)
    .await
    .unwrap_or_default();

    if models.is_empty() {
        let default_models = vec![
            RemoteModel {
                id: "gpt-4o".to_string(),
                name: "GPT-4o".to_string(),
                provider: "Cloud API (v1.2)".to_string(),
                icon_url: None,
                latency_ms: 840,
                cost_per_1k: 0.005,
                success_rate: 0.992,
                status: "Operational".to_string(),
            },
            RemoteModel {
                id: "claude-3-5".to_string(),
                name: "Claude 3.5 Sonnet".to_string(),
                provider: "Direct Endpoint".to_string(),
                icon_url: None,
                latency_ms: 1200,
                cost_per_1k: 0.003,
                success_rate: 0.978,
                status: "Operational".to_string(),
            },
            RemoteModel {
                id: "llama-3-70b".to_string(),
                name: "Llama-3-70B".to_string(),
                provider: "Self-Hosted / GPU Cluster".to_string(),
                icon_url: None,
                latency_ms: 120,
                cost_per_1k: 0.0,
                success_rate: 1.0,
                status: "Operational".to_string(),
            }
        ];

        for m in &default_models {
            let _ = sqlx::query(
                "INSERT INTO remote_models (id, name, provider, icon_url, latency_ms, cost_per_1k, success_rate, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            )
            .bind(&m.id)
            .bind(&m.name)
            .bind(&m.provider)
            .bind(&m.icon_url)
            .bind(m.latency_ms)
            .bind(m.cost_per_1k)
            .bind(m.success_rate)
            .bind(&m.status)
            .execute(&state.db).await;
        }
        return Json(default_models);
    }
    Json(models)
}

pub async fn create_remote_model_handler(State(state): State<Arc<AppState>>, Json(payload): Json<CreateRemoteModelPayload>) -> Json<serde_json::Value> {
    let new_id = uuid::Uuid::new_v4().to_string();
    
    let res = sqlx::query("INSERT INTO remote_models (id, name, provider, icon_url, latency_ms, cost_per_1k, success_rate, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
        .bind(&new_id)
        .bind(&payload.name)
        .bind(&payload.provider)
        .bind(Option::<String>::None)
        .bind(payload.latency_ms)
        .bind(payload.cost_per_1k)
        .bind(1.00) // Default 100% success rate
        .bind("Operational")
        .execute(&state.db).await;

    if res.is_ok() { Json(serde_json::json!({"success": true, "id": new_id})) } else { Json(serde_json::json!({"success": false})) }
}

pub async fn delete_remote_model_handler(State(state): State<Arc<AppState>>, Path(id): Path<String>) -> Json<serde_json::Value> {
    let res = sqlx::query("DELETE FROM remote_models WHERE id = ?").bind(id).execute(&state.db).await;
    if res.is_ok() { Json(serde_json::json!({"success": true})) } else { Json(serde_json::json!({"success": false})) }
}

pub async fn get_knowledge_gaps_handler(State(state): State<Arc<AppState>>) -> Json<Vec<KnowledgeGap>> {
    let gaps = sqlx::query_as::<_, KnowledgeGap>(
        "SELECT id, query, frequency, context, sentiment FROM knowledge_gaps ORDER BY frequency DESC LIMIT 10"
    )
    .fetch_all(&state.db)
    .await
    .unwrap_or_default();

    if gaps.is_empty() {
        let defaults = vec![
            KnowledgeGap { id: "1".to_string(), query: "New vacation policy 2024 updates".to_string(), frequency: 142, context: "HR / Employee Benefits".to_string(), sentiment: "Frustrated".to_string() },
            KnowledgeGap { id: "2".to_string(), query: "ERP password reset flow for external vendors".to_string(), frequency: 89, context: "IT Support / Identity".to_string(), sentiment: "Neutral".to_string() },
            KnowledgeGap { id: "3".to_string(), query: "Sustainability report Q4 board slides".to_string(), frequency: 56, context: "Corporate Strategy".to_string(), sentiment: "Inquisitive".to_string() },
        ];
        for g in &defaults {
            let _ = sqlx::query("INSERT INTO knowledge_gaps (id, query, frequency, context, sentiment) VALUES (?, ?, ?, ?, ?)")
                .bind(&g.id).bind(&g.query).bind(g.frequency).bind(&g.context).bind(&g.sentiment)
                .execute(&state.db).await;
        }
        return Json(defaults);
    }
    Json(gaps)
}

pub async fn get_radar_metrics_handler(State(state): State<Arc<AppState>>) -> Json<RadarMetrics> {
    let row = sqlx::query("SELECT AVG(faithfulness_score) as f_avg, AVG(precision_score) as p_avg FROM evaluations WHERE status = 'completed'")
        .fetch_one(&state.db)
        .await
        .unwrap();

    let f_avg: f64 = row.try_get("f_avg").unwrap_or(94.0);
    let p_avg: f64 = row.try_get("p_avg").unwrap_or(82.0);
    
    let f = if f_avg == 0.0 { 94 } else { f_avg as i32 };
    let p = if p_avg == 0.0 { 82 } else { p_avg as i32 };
    let global = ((f + p) / 2) as i32;

    Json(RadarMetrics {
        global_score: global,
        faithfulness: f,
        precision: p,
    })
}
