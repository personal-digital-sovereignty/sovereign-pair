use std::io::{self, Write};
use std::process::Command;
use tracing::{info, warn, error};

pub async fn run_interactive_installer() {
    println!("\n=======================================================");
    println!("🕸️  SOVEREIGN MESH: Zero-Touch Auto-Deployment Wizard");
    println!("=======================================================\n");

    println!("Este assistente configurará um novo Node P2P da malha copiando fisicamente este mesmo binário para o servidor de destino.\n");

    // Validação Tática do SSH OS-Level (Windows/Mac/Linux fallback graceful)
    match Command::new("ssh").arg("-V").output() {
        Ok(_) => {},
        Err(_) => {
            error!("❌ CRÍTICO: Executável 'ssh' não encontrado no PATH do Sistema!");
            println!("No Windows: Instale o 'OpenSSH Client' em Recursos Opcionais do Sistema.");
            println!("No Linux/MacOS: Instale o pacote openssh-client via apt/pacman/brew.");
            return;
        }
    }

    let ip = prompt("Endpoint Remoto (IP ou Hostname): ", "");
    let user = prompt("SSH Username [default: opc]: ", "opc");
    let key_path = prompt("Caminho absoluto para Chave SSH [default: ~/.ssh/id_rsa]: ", "~/.ssh/id_rsa");

    println!("\n🚀 Preparando Invasão Tática Cíbrida para P2P (Alvo: {}@{})", user, ip);

    // 1. Descobrir o próprio binário do Rust corrente local
    let current_exe = match std::env::current_exe() {
        Ok(path) => path,
        Err(e) => {
            error!("❌ Falha ao encontrar o próprio binário Rust O.S ativo: {}", e);
            return;
        }
    };
    let exe_str = current_exe.to_string_lossy().to_string();

    // 2. Transmissão do Binário (SCP)
    println!("⏳ [1/3] Realizando Upload Físico do Core Engine (SCP)...");
    let target_uri = format!("{}@{}", user, ip);
    let scp_cmd = Command::new("scp")
        .arg("-i").arg(&key_path)
        .arg("-o").arg("StrictHostKeyChecking=accept-new")
        .arg(&exe_str)
        .arg(format!("{}:/tmp/sovereign-core", target_uri))
        .status();

    match scp_cmd {
        Ok(status) if status.success() => println!("✅ SCP File Transfer Concluído com Sucesso."),
        _ => {
            error!("❌ Falha ao transferir binário para a nuvem. Cheque sua chave private.");
            return;
        }
    }

    // 3. Template do Serviço Embutido no Binário (Injeção via SSH)
    println!("⏳ [2/3] Escalando privilégios e injetando o Daemon Systemd...");
    
    let service_template = r#"
[Unit]
Description=Sovereign Pair Cibrid Node
After=network-online.target

[Service]
Type=simple
User=root
# Garanta que a nuvem execute com fallback loop
WorkingDirectory=/opt/sovereign/
ExecStart=/usr/local/bin/sovereign-core --host 127.0.0.1
Restart=always
RestartSec=5
Environment="SOVEREIGN_RUN_ENV=production"

[Install]
WantedBy=multi-user.target
"#;

    // Shell remota: Move executable, creates dir, writes systemd, starts background daemon
    let remote_setup_script = format!(
        "sudo mv /tmp/sovereign-core /usr/local/bin/ && \
         sudo chmod +x /usr/local/bin/sovereign-core && \
         sudo mkdir -p /opt/sovereign && \
         cat << 'EOF' | sudo tee /etc/systemd/system/sovereign.service \n{}\nEOF\n \
         sudo systemctl daemon-reload && \
         sudo systemctl enable --now sovereign",
        service_template
    );

    let setup_cmd = Command::new("ssh")
        .arg("-i").arg(&key_path)
        .arg("-o").arg("StrictHostKeyChecking=accept-new")
        .arg(&target_uri)
        .arg(remote_setup_script)
        .status();

    match setup_cmd {
        Ok(status) if status.success() => println!("✅ [3/3] Systemd Provisionado e Daemon Engine inciada na Porta Reversa."),
        _ => {
            error!("❌ A instalação explodiu durante a injeção do daemon Systemd via SSH. Verifique privilegios na Nuvem.");
            return;
        }
    }

    println!("\n=======================================================");
    println!("🎯 MESH NODE DEPLOYED SUCCESSFULLY!");
    println!("=======================================================");
    println!("O servidor remoto agora hospeda o Sovereign Core silenciosamente na porta 38001.");
    println!("Para ligar sua máquina master a ele, execute a rotina de P2P Link Tunnel.\n");
}

fn prompt(message: &str, default: &str) -> String {
    print!("{}", message);
    io::stdout().flush().unwrap();
    let mut input = String::new();
    io::stdin().read_line(&mut input).unwrap();
    let trimmed = input.trim();
    if trimmed.is_empty() {
        default.to_string()
    } else {
        trimmed.to_string()
    }
}
