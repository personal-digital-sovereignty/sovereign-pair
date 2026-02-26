import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.ingest import process_single_file
from config import RAW_DOCS_DIRS, RAW_DOCS_DIR, configure_logging, ALLOWED_EXTENSIONS

# Re-use proper logging format
configure_logging()
logger = logging.getLogger("RAG-Watcher")

class RAGIngestHandler(FileSystemEventHandler):
    """
    Handler para interceptar eventos de arquivo e injetar no ChromaDB automaticamente.
    """
    def __init__(self):
        super().__init__()
        # Para evitar enxurradas de eventos, usamos um cache de debounce simples (Path -> timestamp)
        self._last_processed = {}
        self._debounce_seconds = 2.0

    def _is_valid_file(self, path: Path) -> bool:
        if path.is_dir():
            return False
            
        ext = path.suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False
            
        # Ignore arquivos ocultos
        if path.name.startswith('.'):
            return False
            
        return True

    def process_event(self, path_str: str, is_update: bool = False):
        path = Path(path_str)
        if not self._is_valid_file(path):
            return

        now = time.time()
        last_time = self._last_processed.get(str(path), 0)
        if now - last_time < self._debounce_seconds:
            return # Debounced
            
        self._last_processed[str(path)] = now
        
        event_name = "modificado" if is_update else "criado"
        logger.info(f"👀 Watcher detectou arquivo {event_name}: {path.name}")
        
        try:
            # Chama a mesmíssima rotina do endpoint FastAPI com a flag is_update correspondente
            process_single_file(path, is_update=is_update)
            logger.info(f"✅ RAG Inject on-the-fly completo para: {path.name}")
        except Exception as e:
            logger.error(f"❌ Watcher falhou ao injetar arquivo {path.name}: {e}")

    def on_created(self, event):
        if not event.is_directory:
            self.process_event(event.src_path, is_update=False)

    def on_modified(self, event):
        if not event.is_directory:
            self.process_event(event.src_path, is_update=True)


def start_watcher():
    logger.info("Starting Sovereign Pair OS File Watcher Daemon...")
    
    # 1. Obter quais diretorios devemos observar
    dirs_to_watch = RAW_DOCS_DIRS if RAW_DOCS_DIRS else [RAW_DOCS_DIR]
    
    event_handler = RAGIngestHandler()
    observer = Observer()
    
    active_watches = 0
    for watch_dir in dirs_to_watch:
        if not watch_dir.exists():
            try:
                watch_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Watch dir didn't exist and failed to create {watch_dir}: {e}")
                continue
                
        observer.schedule(event_handler, str(watch_dir), recursive=True)
        active_watches += 1
        logger.info(f"👁️  Watching directory (recursive): {watch_dir}")
        
    if active_watches == 0:
        logger.error("No valid directories to watch. Exiting watcher.")
        return
        
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Watcher interrupted by user.")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watcher()
