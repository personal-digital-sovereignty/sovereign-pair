use std::process::Stdio;
use tokio::process::Command;
use tracing::{info, error, debug};
use sqlx::Row;
use serde_json::Value;
use reqwest::Client;
use crate::mesh_router::MeshRouter;

/// The structure that abstracts the OCI Sandbox connection.
pub struct SshGateway;

impl SshGateway {
    /// Executes a strictly isolated bash/python script on the Oracle Cloud VM.
    /// Captures Stdout and Stderr to feed back into the Sovereign Pair 'ReWOO Solver'.
    pub async fn execute_sandboxed_script(script_payload: &str, db: sqlx::SqlitePool) -> Result<String, String> {
        let target_uri: String;
        let mut key_path = String::new();

        let client = Client::new();
        // 1. TENTA ROTEAMENTO INTELIGENTE NA MALHA (Mesh Router P2P)
        if let Some((mesh_uri, mesh_key)) = MeshRouter::find_best_coder_node(&client).await {
            info!("🌐 [Zero-Trust Gateway] O Orquestrador P2P sequestrou o deploy! Executando Job no Nó da Malha: {}", mesh_uri);
            target_uri = mesh_uri;
            key_path = mesh_key;
        } else {
            // 2. FALLBACK PARA O BANCO DE DADOS LOCAL OCI
            // GAP-O02: Reads from the new 'cloud_target' settings first (host_ip + pem_key AES-GCM).
            // Falls back to legacy 'system_settings' oci_sandbox_* fields for backward compat.
            let cloud_row = sqlx::query("SELECT value_json FROM global_settings WHERE id = 'cloud_target'")
                .fetch_optional(&db)
                .await
                .ok()
                .flatten();

            let mut target_ip = String::new();
            let mut target_user = "ubuntu".to_string(); // sensible OCI default

            if let Some(r) = cloud_row {
                let val: String = r.get("value_json");
                let parsed: serde_json::Value = serde_json::from_str(&val).unwrap_or(serde_json::json!({}));

                let raw_ip = parsed.get("host_ip").and_then(|v| v.as_str()).unwrap_or("").to_string();
                let encrypted_pem = parsed.get("pem_key").and_then(|v| v.as_str()).unwrap_or("").to_string();

                if !raw_ip.is_empty() && !encrypted_pem.is_empty() {
                    // Decrypt PEM from AES-GCM vault
                    match crate::kms::decrypt_vault_secret(&encrypted_pem) {
                        Some(pem_content) => {
                            // Write PEM to a secure temp file with 0600 permissions
                            let tmp_path = std::env::temp_dir().join(format!("sovereign_oci_{}.pem", std::process::id()));
                            match std::fs::write(&tmp_path, pem_content.as_bytes()) {
                                Ok(_) => {
                                    #[cfg(unix)]
                                    {
                                        use std::os::unix::fs::PermissionsExt;
                                        let _ = std::fs::set_permissions(&tmp_path, std::fs::Permissions::from_mode(0o600));
                                    }
                                    target_ip = raw_ip;
                                    key_path = tmp_path.to_string_lossy().to_string();
                                    info!("🔑 [Zero-Trust Gateway] OCI PEM decrypted from Vault and staged at temp path.");
                                },
                                Err(e) => {
                                    error!("❌ [Zero-Trust Gateway] Failed to write PEM temp file: {}", e);
                                }
                            }
                        },
                        None => {
                            error!("❌ [Zero-Trust Gateway] KMS decryption of OCI PEM failed. Key may be corrupted.");
                        }
                    }
                }
            }

            // Legacy fallback: system_settings oci_sandbox_* fields
            if target_ip.is_empty() {
                let row = sqlx::query("SELECT value_json FROM global_settings WHERE id = 'system_settings'")
                    .fetch_optional(&db)
                    .await
                    .map_err(|e| format!("Database connection err: {}", e))?;

                if let Some(r) = row {
                    let val: String = r.get("value_json");
                    let parsed: Value = serde_json::from_str(&val).unwrap_or(serde_json::json!({}));
                    target_ip = parsed.get("oci_sandbox_ip").and_then(|v| v.as_str()).unwrap_or("").to_string();
                    target_user = parsed.get("oci_sandbox_user").and_then(|v| v.as_str()).unwrap_or("ubuntu").to_string();
                    key_path = parsed.get("oci_sandbox_key").and_then(|v| v.as_str()).unwrap_or("").to_string();
                }
            }

            if target_ip.is_empty() || key_path.is_empty() {
                error!("❌ [Zero-Trust Gateway] Nenhum Nó de Malha Sandboxed encontrado E credenciais OCI do KMS ausentes.");
                return Err("Missing Zero-Trust Sandbox Parameters. No Mesh Nodes available and no KMS configs.".to_string());
            }
            target_uri = format!("{}@{}", target_user, target_ip);
            info!("🛡️ [Zero-Trust Gateway] Opening SSH Pipe to Oracle Cloud VM: {}", target_uri);
        }

        debug!("🛡️ [Zero-Trust Gateway] SSH Key Auth: {}", key_path);

        // Dispara o subprocesso CLI do OpenSSH de forma nativa e injeta o Payload via Stdin
        let mut ssh_cmd = Command::new("ssh");
        ssh_cmd.arg("-o").arg("StrictHostKeyChecking=accept-new")
               .arg("-o").arg("ConnectTimeout=5")
               .arg("-i").arg(&key_path)
               .arg(&target_uri)
               .arg("bash")     // Roda como bash remotor
               .stdin(Stdio::piped())
               .stdout(Stdio::piped())
               .stderr(Stdio::piped());

        let mut child = match ssh_cmd.spawn() {
            Ok(c) => c,
            Err(e) => {
                error!("❌ [Zero-Trust Gateway] SSH Fork Error: {}", e);
                return Err(format!("SSH Fork Error: {}", e));
            }
        };

        // Pipe o script gerado pelo O.S (The Coder) para dentro do terminal Ubuntu remoto
        if let Some(mut stdin) = child.stdin.take() {
            use tokio::io::AsyncWriteExt;
            if let Err(e) = stdin.write_all(script_payload.as_bytes()).await {
                error!("❌ [Zero-Trust Gateway] Falha ao injetar script no Stdin SSH: {}", e);
            }
        }

        // Aguarda a execução final
        match child.wait_with_output().await {
            Ok(output) => {
                let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
                let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();

                if output.status.success() {
                    info!("✅ [Zero-Trust Gateway] The Coder (Oracle) execution success.");
                    Ok(format!("STDOUT:\n{}", stdout))
                } else {
                    error!("⚠️ [Zero-Trust Gateway] The Coder script returned Exit Code != 0.");
                    Err(format!("STDOUT:\n{}\n\nSTDERR:\n{}", stdout, stderr))
                }
            }
            Err(e) => {
                error!("❌ [Zero-Trust Gateway] Process Wait Error: {}", e);
                Err(format!("Runtime Execution failed: {}", e))
            }
        }
    }
}
