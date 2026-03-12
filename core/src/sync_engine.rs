use notify::{Event, RecommendedWatcher, RecursiveMode, Watcher, Config};
use std::path::{Path, PathBuf};
use tokio::sync::broadcast;
use serde::Serialize;
use tracing::{info, warn, error};
use std::time::Duration;
use uuid::Uuid;
use tokio::time::sleep;

#[derive(Serialize, Clone, Debug)]
pub struct IngestionJob {
    pub id: String,
    pub filename: String,
    pub status: String,
    #[serde(rename = "currentStep")]
    pub current_step: u8,
    pub progress_ms: u64,
}

pub struct SyncEngine {
    pub tx: broadcast::Sender<IngestionJob>,
    vault_path: PathBuf,
}

impl SyncEngine {
    pub fn new(vault_path: PathBuf) -> Self {
        let (tx, _) = broadcast::channel(100);
        Self { tx, vault_path }
    }

    pub async fn start_watcher(&self) {
        let vault_path = self.vue_path();
        let current_tx = self.tx.clone();

        tokio::spawn(async move {
            info!("🔬 [Sensus Sync Engine] Watcher ativado no Vault: {:?}", vault_path);
            
            let (watcher_tx, mut watcher_rx) = tokio::sync::mpsc::channel(100);

            // Closure síncrona do Notify
            let mut watcher: RecommendedWatcher = Watcher::new(
                move |res| {
                    if let Ok(event) = res {
                        let _ = watcher_tx.blocking_send(event);
                    }
                },
                Config::default(),
            ).expect("Sovereign falhou ao criar FSEvent Watcher");

            watcher.watch(Path::new(&vault_path), RecursiveMode::Recursive).expect("Falha ao assistir pasta Vault");

            // Loop assíncrono recebendo eventos
            while let Some(event) = watcher_rx.recv().await {
                if let notify::event::EventKind::Create(_) | notify::event::EventKind::Modify(notify::event::ModifyKind::Data(_)) = event.kind {
                    for path in event.paths {
                        if path.is_file() {
                            let filename = path.file_name().unwrap_or_default().to_string_lossy().to_string();
                            
                            // Impede re-processamento de backups e arquivos ocultos
                            if filename.starts_with('.') || filename.ends_with('~') {
                                continue;
                            }

                            info!("📄 [Sensus Sync Engine] Novo artefato detectado: {}", filename);
                            
                            let job_id = Uuid::new_v4().to_string();
                            let job = IngestionJob {
                                id: job_id.clone(),
                                filename: filename.clone(),
                                status: "queued".to_string(),
                                current_step: 0,
                                progress_ms: 0,
                            };
                            
                            let _ = current_tx.send(job.clone());
                            
                            // Lança simulador de processamento assíncrono para o Frontend RAG Core
                            let sim_tx = current_tx.clone();
                            tokio::spawn(async move {
                                Self::simulate_ingestion_pipeline(job, sim_tx).await;
                            });
                        }
                    }
                }
            }
        });
    }

    fn vue_path(&self) -> PathBuf {
        self.vault_path.clone()
    }

    async fn simulate_ingestion_pipeline(mut job: IngestionJob, tx: broadcast::Sender<IngestionJob>) {
        // Step 1: O OCR/Parse
        job.status = "processing".to_string();
        job.current_step = 0;
        let _ = tx.send(job.clone());
        sleep(Duration::from_millis(1500)).await;

        // Step 2: Doc Chunking
        job.current_step = 1;
        let _ = tx.send(job.clone());
        sleep(Duration::from_millis(1200)).await;

        // Step 3: Embedding Vector
        job.current_step = 2;
        let _ = tx.send(job.clone());
        sleep(Duration::from_millis(2500)).await;

        // Step 4: SQLite Store
        job.current_step = 3;
        let _ = tx.send(job.clone());
        sleep(Duration::from_millis(800)).await;

        // Completed
        job.status = "completed".to_string();
        job.current_step = 4;
        let _ = tx.send(job.clone());
        info!("✅ [Sensus Sync] Ingestão Concluída no Vault: {}", job.filename);
    }
}
