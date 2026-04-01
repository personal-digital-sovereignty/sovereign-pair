use serde::{Deserialize, Serialize};
use std::process::Stdio;
use tokio::process::Command;
use tracing::{error, info};

#[derive(Debug, Serialize, Deserialize)]
pub struct WhisperResult {
    pub success: bool,
    pub language: Option<String>,
    pub language_probability: Option<f64>,
    pub text: Option<String>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OcrResult {
    pub success: bool,
    pub text: Option<String>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MidiResult {
    pub success: bool,
    pub output_dir: Option<String>,
    pub message: Option<String>,
    pub error: Option<String>,
}

pub async fn extract_text_from_audio(file_path: &str) -> Result<WhisperResult, String> {
    info!("Iniciando node Python Whisper para: {}", file_path);
    let output = Command::new("python3")
        .arg("../nodes/audio_transcriber.py")
        .arg(file_path)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .await
        .map_err(|e| format!("Falha ao invocar processo Node: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    if !output.status.success() {
        error!("Erro no Node Whisper Python: {}", stderr);
    }

    match serde_json::from_str::<WhisperResult>(&stdout) {
        Ok(mut res) => {
            if !output.status.success() && res.error.is_none() {
                res.error = Some(stderr.to_string());
            }
            Ok(res)
        }
        Err(e) => {
            Err(format!("Falha ao fazer parse do JSON do Node Whisper: {} | Saida Bruta: {}", e, stdout))
        }
    }
}

pub async fn extract_text_from_image(file_path: &str) -> Result<OcrResult, String> {
    info!("Iniciando node Python PaddleOCR para: {}", file_path);
    let output = Command::new("python3")
        .arg("../nodes/vision_ocr.py")
        .arg(file_path)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .await
        .map_err(|e| format!("Falha ao invocar processo Node: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    if !output.status.success() {
        error!("Erro no Node PaddleOCR Python: {}", stderr);
    }

    match serde_json::from_str::<OcrResult>(&stdout) {
        Ok(mut res) => {
            if !output.status.success() && res.error.is_none() {
                res.error = Some(stderr.to_string());
            }
            Ok(res)
        }
        Err(e) => {
            Err(format!("Falha ao fazer parse do JSON do Node PaddleOCR: {} | Saida Bruta: {}", e, stdout))
        }
    }
}

pub async fn extract_midi_from_audio(audio_path: &str, output_dir: &str) -> Result<MidiResult, String> {
    info!("Iniciando node Python Basic Pitch para: {}", audio_path);
    let output = Command::new("python3")
        .arg("../nodes/midi_transcriber.py")
        .arg(audio_path)
        .arg(output_dir)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .await
        .map_err(|e| format!("Falha ao invocar processo Node: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    if !output.status.success() {
        error!("Erro no Node Basic Pitch Python: {}", stderr);
    }

    match serde_json::from_str::<MidiResult>(&stdout) {
        Ok(mut res) => {
            if !output.status.success() && res.error.is_none() {
                res.error = Some(stderr.to_string());
            }
            Ok(res)
        }
        Err(e) => {
            Err(format!("Falha ao fazer parse do JSON do Node Basic Pitch: {} | Saida Bruta: {}", e, stdout))
        }
    }
}
