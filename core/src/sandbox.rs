use std::env;
use std::path::PathBuf;
use std::process::Command;
use tokio::fs;
use tracing::{info, warn, error};
use uuid::Uuid;

/// Retorna o caminho base do ecossistema Sovereign
/// Windows: %LOCALAPPDATA%\sovereign-pair\sandbox
/// Linux:   ~/.local/share/sovereign-pair/sandbox
/// MacOS:   ~/Library/Application Support/sovereign-pair/sandbox
fn get_base_path() -> PathBuf {
    dirs::data_local_dir()
        .unwrap_or_else(|| {
            // Fallback robusto: tenta HOME/USERPROFILE, depois diretório atual
            let home = env::var("HOME")
                .or_else(|_| env::var("USERPROFILE"))
                .unwrap_or_else(|_| ".".to_string());
            PathBuf::from(home)
        })
        .join("sovereign-pair")
        .join("sandbox")
}

/// Retorna o caminho do Python standalone baixado pelo Sovereign
/// Este Python é 100% autocontido — não depende de nenhuma instalação do sistema.
fn get_standalone_python_bin() -> PathBuf {
    let base = get_base_path().join("python");
    if cfg!(target_os = "windows") {
        base.join("python.exe")
    } else {
        base.join("bin").join("python3")
    }
}

/// Retorna o caminho do executável Python dentro da bolha (Venv)
/// Windows: venv\Scripts\python.exe
/// Unix:    venv/bin/python3
pub fn get_hermetic_python_bin() -> PathBuf {
    let base = get_base_path().join("venv");
    if cfg!(target_os = "windows") {
        base.join("Scripts").join("python.exe")
    } else {
        base.join("bin").join("python3")
    }
}

/// Retorna o caminho do Pip dentro da bolha
pub fn get_hermetic_pip_bin() -> PathBuf {
    let base = get_base_path().join("venv");
    if cfg!(target_os = "windows") {
        base.join("Scripts").join("pip.exe")
    } else {
        base.join("bin").join("pip")
    }
}

/// Tenta localizar qualquer Python >= 3.10 no sistema.
/// Retorna None se nenhum Python adequado existir (Mac novo, por exemplo).
fn find_system_python() -> Option<PathBuf> {
    // 1. Caminhos absolutos conhecidos
    let candidates: Vec<&str> = if cfg!(target_os = "windows") {
        vec!["C:\\Python312\\python.exe", "C:\\Python311\\python.exe", "C:\\Python310\\python.exe"]
    } else if cfg!(target_os = "macos") {
        vec![
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3",
            "/Library/Frameworks/Python.framework/Versions/Current/bin/python3",
            "/usr/bin/python3",
        ]
    } else {
        vec!["/usr/bin/python3", "/usr/local/bin/python3", "/usr/bin/python"]
    };

    for c in &candidates {
        let p = PathBuf::from(c);
        if p.exists() { return Some(p); }
    }

    // 2. which/where (resolve via PATH)
    let (which, probe) = if cfg!(target_os = "windows") { ("where", "python") } else { ("which", "python3") };
    if let Ok(out) = Command::new(which).arg(probe).output() {
        if out.status.success() {
            let resolved = String::from_utf8_lossy(&out.stdout).trim().to_string();
            if !resolved.is_empty() {
                let p = PathBuf::from(&resolved);
                if p.exists() { return Some(p); }
            }
        }
    }

    None
}

// ─────────────────────────────────────────────────────────────
// Auto-Provisioning: Baixa um Python standalone se não existir
// Usa builds oficiais do Astral (python-build-standalone)
// Mesma infraestrutura usada pelo uv/rye — confiável e FOSS
// ─────────────────────────────────────────────────────────────

/// Versão do CPython standalone a baixar (formato Astral release)
const STANDALONE_PYTHON_VERSION: &str = "3.12.13";
const STANDALONE_RELEASE_TAG: &str = "20260414";

/// Constrói a URL de download correta baseada no OS e arch atuais
fn get_standalone_download_url() -> Option<String> {
    let arch = if cfg!(target_arch = "aarch64") { "aarch64" }
    else if cfg!(target_arch = "x86_64") { "x86_64" }
    else { return None; };

    let platform = if cfg!(target_os = "macos") { "apple-darwin" }
    else if cfg!(target_os = "linux") { "unknown-linux-gnu" }
    else if cfg!(target_os = "windows") { "pc-windows-msvc" }
    else { return None; };

    Some(format!(
        "https://github.com/astral-sh/python-build-standalone/releases/download/{tag}/cpython-{ver}+{tag}-{arch}-{plat}-install_only_stripped.tar.gz",
        tag = STANDALONE_RELEASE_TAG,
        ver = STANDALONE_PYTHON_VERSION,
        arch = arch,
        plat = platform
    ))
}

/// Baixa e extrai o Python standalone na sandbox do Sovereign.
/// Retorna o caminho do binário python3 extraído.
async fn provision_standalone_python() -> Result<PathBuf, String> {
    let url = get_standalone_download_url()
        .ok_or_else(|| "Arquitetura ou S.O. não suportado para auto-provisioning Python.".to_string())?;

    let sandbox_dir = get_base_path();
    let python_dir = sandbox_dir.join("python");
    let tarball_path = sandbox_dir.join("cpython-standalone.tar.gz");

    info!("🌐 [Sovereign Sandbox] Baixando Python {STANDALONE_PYTHON_VERSION} standalone (~24MB)...");
    info!("🌐 [Sovereign Sandbox] URL: {}", url);

    // Download via reqwest (já é dependência do core)
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(300))
        .build()
        .map_err(|e| format!("Falha ao criar HTTP client: {}", e))?;

    let response = client.get(&url).send().await
        .map_err(|e| format!("Falha ao baixar Python standalone: {}", e))?;

    if !response.status().is_success() {
        return Err(format!("Download falhou com HTTP {}: {}", response.status(), url));
    }

    let bytes = response.bytes().await
        .map_err(|e| format!("Falha ao ler body do download: {}", e))?;

    // Salvar tarball no disco
    let _ = fs::create_dir_all(&sandbox_dir).await;
    fs::write(&tarball_path, &bytes).await
        .map_err(|e| format!("Falha ao salvar tarball: {}", e))?;

    info!("📦 [Sovereign Sandbox] Download concluído ({:.1} MB). Extraindo...", bytes.len() as f64 / 1_048_576.0);

    // Extrair via tar nativo (Unix) ou tar.exe (Windows)
    // O tarball contém um diretório "python/" na raiz
    let extract_status = if cfg!(target_os = "windows") {
        Command::new("tar")
            .arg("-xzf").arg(&tarball_path)
            .arg("-C").arg(&sandbox_dir)
            .status()
    } else {
        Command::new("tar")
            .arg("-xzf").arg(&tarball_path)
            .arg("-C").arg(&sandbox_dir)
            .status()
    };

    // Limpar tarball após extração
    let _ = fs::remove_file(&tarball_path).await;

    match extract_status {
        Ok(s) if s.success() => {
            let python_bin = get_standalone_python_bin();
            if python_bin.exists() {
                info!("✅ [Sovereign Sandbox] Python {STANDALONE_PYTHON_VERSION} standalone extraído com sucesso em {:?}", python_dir);
                Ok(python_bin)
            } else {
                Err(format!("Extração concluída mas binário não encontrado em {:?}", python_bin))
            }
        },
        Ok(s) => Err(format!("tar retornou código de saída {:?}", s.code())),
        Err(e) => Err(format!("Falha ao executar tar: {}", e)),
    }
}

/// Inicializa e provisiona a sandbox na inicialização do sistema.
/// Fluxo:
///   1. Se venv já existe → retorna true (hot path)
///   2. Tenta usar Python do sistema (Homebrew, APT, etc.)
///   3. Se não existir → baixa Python standalone (python-build-standalone / Astral)
///   4. Cria venv + instala pacotes analíticos
pub async fn setup_python_sandbox() -> bool {
    let sandbox_dir = get_base_path();
    let venv_dir = sandbox_dir.join("venv");

    if venv_dir.exists() {
        return true; // Já está provisionado
    }

    info!("📦 [Sovereign Sandbox] Provisionando ambiente Python Hermético na raiz do usuário...");
    if !sandbox_dir.exists() {
        let _ = fs::create_dir_all(&sandbox_dir).await;
    }

    // ── FASE 1: Encontrar ou provisionar o Python base ──
    let python_bin = if let Some(sys_python) = find_system_python() {
        info!("🐍 [Sovereign Sandbox] Python do sistema encontrado: {:?}", sys_python);
        sys_python
    } else if get_standalone_python_bin().exists() {
        info!("🐍 [Sovereign Sandbox] Python standalone já provisionado anteriormente.");
        get_standalone_python_bin()
    } else {
        // Auto-provisioning: baixa Python standalone
        info!("⚠️ [Sovereign Sandbox] Nenhum Python detectado no sistema. Iniciando auto-download...");
        match provision_standalone_python().await {
            Ok(bin) => bin,
            Err(e) => {
                error!("❌ [Sovereign Sandbox] Auto-provisioning falhou: {}. \
                        Instale Python 3.10+ manualmente: \
                        MacOS: `brew install python3` | \
                        Linux: `sudo apt install python3 python3-venv` | \
                        Windows: python.org/downloads", e);
                return false;
            }
        }
    };

    // ── FASE 2: Criar o Venv usando o Python encontrado ──
    let venv_status = Command::new(&python_bin)
        .arg("-m")
        .arg("venv")
        .arg(&venv_dir)
        .status();

    if !venv_status.is_ok_and(|st| st.success()) {
        // Fallback: se -m venv falha (ex: Python standalone sem ensurepip), tentar com --without-pip
        info!("⚠️ [Sovereign Sandbox] venv padrão falhou. Tentando --without-pip...");
        let fallback_status = Command::new(&python_bin)
            .arg("-m")
            .arg("venv")
            .arg("--without-pip")
            .arg(&venv_dir)
            .status();

        if !fallback_status.is_ok_and(|st| st.success()) {
            error!("❌ [Sovereign Sandbox] Falha ao criar venv com {:?}!", python_bin);
            return false;
        }

        // Se criou sem pip, precisa bootstrap-ar o pip manualmente
        info!("📥 [Sovereign Sandbox] Bootstrap do pip via ensurepip...");
        let hermetic_python = get_hermetic_python_bin();
        let _ = Command::new(&hermetic_python)
            .arg("-m")
            .arg("ensurepip")
            .arg("--default-pip")
            .status();
    }

    info!("🐍 [Sovereign Sandbox] Venv criado. Instalando pacotes analíticos universais (Numpy, Pandas, etc)...");
    
    // ── FASE 3: Instalar Pacotes Críticos via pip hermético ──
    let pip_bin = get_hermetic_pip_bin();
    let install_status = Command::new(&pip_bin)
        .arg("install")
        .arg("--disable-pip-version-check")
        .arg("-q") // Modo silencioso
        .arg("pandas")
        .arg("numpy")
        .arg("yfinance")
        .arg("requests")
        .arg("duckduckgo-search")
        .arg("duckdb")
        .status();

    if install_status.is_ok_and(|st| st.success()) {
        info!("✅ [Sovereign Sandbox] Ambiente Matemático e Analítico isolado com sucesso!");
        return true;
    }
    
    warn!("⚠️ [Sovereign Sandbox] Venv criado, mas a instalação de pacotes via pip falhou.");
    false
}


/// Executa um script Python puramente dentro da bolha hermética.
/// Retorna Stdout puro ou Err(Stderr).
pub async fn execute_python_code(code: &str) -> Result<String, String> {
    let python_bin = get_hermetic_python_bin();
    if !python_bin.exists() {
        return Err("A Sovereign Sandbox não foi inicializada neste S.O.".to_string());
    }

    let script_name = format!("sovereign_execute_{}.py", Uuid::new_v4());
    let temp_dir = env::temp_dir();
    let script_path = temp_dir.join(&script_name);

    if let Err(e) = fs::write(&script_path, code).await {
        return Err(format!("Falha ao injetar script no sistema de arquivos: {}", e));
    }

    let _ = tracing_subscriber::fmt::format(); // Silencia logs de formatação
    info!("⚙️ [Plan & Execute] Disparando script na Sandbox Hermética: {}", script_name);

    // AST Jail Injection (Epic 9) — usa resolve_python_workers_dir() para compatibilidade com MacOS App Bundle
    let jail_script = crate::api_trainer::resolve_python_workers_dir().join("ast_jail.py");
    
    let output = if jail_script.exists() {
        Command::new(&python_bin)
            .arg(&jail_script)
            .arg(&script_path)
            .current_dir(&temp_dir)
            .output()
    } else {
        // Fallback or panic
        Command::new(&python_bin)
            .arg(&script_path)
            .current_dir(&temp_dir)
            .output()
    };

    // Tentar apagar o script de forma silenciosa para não poluir /tmp
    let _ = fs::remove_file(&script_path).await;

    match output {
        Ok(out) => {
            let stdout_str = String::from_utf8_lossy(&out.stdout).to_string();
            let stderr_str = String::from_utf8_lossy(&out.stderr).to_string();

            if out.status.success() {
                Ok(stdout_str)
            } else {
                Err(format!("{}\n{}", stdout_str, stderr_str))
            }
        },
        Err(e) => {
            Err(format!("Falha Crítica ao invocar Sandbox Core: {}", e))
        }
    }
}
