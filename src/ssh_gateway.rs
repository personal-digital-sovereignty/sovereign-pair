use std::process::Stdio;
use tokio::process::Command;
use tracing::{info, error, debug};
use std::env;

/// The structure that abstracts the OCI Sandbox connection.
pub struct SshGateway;

impl SshGateway {
    /// Executes a strictly isolated bash/python script on the Oracle Cloud VM.
    /// Captures Stdout and Stderr to feed back into the Sovereign Pair 'ReWOO Solver'.
    pub async fn execute_sandboxed_script(script_payload: &str) -> Result<String, String> {
        let target_ip = match env::var("OCI_HOST") {
            Ok(ip) => ip,
            Err(_) => {
                error!("❌ [Zero-Trust Gateway] OCI_HOST não está configurado na variável de ambiente.");
                return Err("Missing OCI_HOST in .env variables.".to_string());
            }
        };
        let target_user = env::var("OCI_USER").unwrap_or_else(|_| "ubuntu".to_string());
        let key_path = env::var("OCI_SSH_KEY").unwrap_or_else(|_| {
            let mut p = dirs::home_dir().unwrap_or_default();
            p.push(".ssh/id_ed25519");
            p.to_string_lossy().to_string()
        });

        let target_uri = format!("{}@{}", target_user, target_ip);

        info!("🛡️ [Zero-Trust Gateway] Opening SSH Pipe to Oracle VM: {}", target_uri);
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
