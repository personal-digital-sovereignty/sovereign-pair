import os
import re
import yaml
import uuid
import time
import threading
from datetime import datetime
import uuid
from typing import Dict, Any, List, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.core.the_sentinel import TheSentinel
from src.api.models import SensusDocumentModel, QuarantineLog

# --- OS Sniffing for Docker Desktop Bind Mounts (Graceful Degradation) ---
def should_use_polling() -> bool:
    if os.environ.get("SENSUS_FORCE_POLLING", "").lower() == "true":
        return True
    try:
        # Check if running in Linux (Docker) and using a virt/fuse mount typical of MacOS/Windows Hosts
        with open("/proc/mounts", "r") as f:
            mounts = f.read()
            if "fuse.grpc" in mounts or "virtiofs" in mounts or "9p" in mounts or "osxfs" in mounts:
                return True
    except Exception:
        pass
    return False

# --- Ignore Parser ---
def get_ignores(base_path: str) -> Set[str]:
    """Parses .sovereignignore and returns a set of directory names to skip (protecting inotify descriptor limits)."""
    ignores = {".git", "node_modules", ".venv", "venv", "env", ".obsidian", "__pycache__", "dist", "build"}
    ignore_file = os.path.join(base_path, ".sovereignignore")
    if os.path.exists(ignore_file):
        try:
            with open(ignore_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Trata globs básicos removendo barras p/ bater com obj de diretório
                        name = line.rstrip("/")
                        ignores.add(name)
        except Exception as e:
            print(f"[The Mom] Aviso: falha ao ler .sovereignignore em {base_path}: {e}")
    return ignores

from src.api.schemas import SensusDocument

class MarkdownParser:
    """The Mom: Deterministic parsing of Markdown files with O(1) matching"""
    
    # Regex Patterns - Compiled once on startup for zero-latency execution
    TODO_PATTERN = re.compile(r'^[\s]*[-*+]\s+\[([\sxX])\]\s+(.*)$', re.MULTILINE)
    LINK_PATTERN = re.compile(r'\[\[(.*?)\]\]')
    TAG_PATTERN = re.compile(r'(?<!\S)#([a-zA-Z0-9_/-]+)(?!\S)')
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.MULTILINE | re.DOTALL)

    @classmethod
    def parse_content(cls, content: str, file_path: str, tenant_id: str) -> SensusDocument:
        """Parses the raw text content of a Markdown file."""
        frontmatter: Dict[str, Any] = {}
        cleaned_content = content
        
        # 1. Parse Frontmatter
        fm_match = cls.FRONTMATTER_PATTERN.search(content)
        if fm_match:
            try:
                fm_text = fm_match.group(1)
                parsed_yaml = yaml.safe_load(fm_text)
                if isinstance(parsed_yaml, dict):
                    # Sanitize dates and other objects for JSON serialization
                    for k, v in parsed_yaml.items():
                        if isinstance(v, (datetime, uuid.UUID)):
                            parsed_yaml[k] = str(v)
                        # Specific check for datetime.date (PyYAML converts '2008-01-01' natively)
                        elif type(v).__name__ == 'date':
                            parsed_yaml[k] = str(v)
                    frontmatter = parsed_yaml
                # Remove frontmatter from content to avoid false tag/todo matches inside YAML
                cleaned_content = content[fm_match.end():]
            except yaml.YAMLError as e:
                print(f"[The Mom] YAML Error in {file_path}: {e}")

        # 2. Extract To-Dos
        todos = []
        for match in cls.TODO_PATTERN.finditer(cleaned_content):
            status = match.group(1).lower()
            task_text = match.group(2).strip()
            # We could store status as well, but for now we extract the raw text
            is_done = status == 'x'
            todos.append(f"{'[x]' if is_done else '[ ]'} {task_text}")

        # 3. Extract Links
        links = cls.LINK_PATTERN.findall(cleaned_content)
        links = list(set([str(link).strip() for link in links]))  # Unique links

        # 4. Extract Tags
        tags = cls.TAG_PATTERN.findall(cleaned_content)
        tags = list(set([str(tag).strip() for tag in tags])) # Unique tags

        return SensusDocument(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            file_path=file_path,
            content=content,
            frontmatter=frontmatter,
            extracted_todos=todos,
            extracted_tags=tags,
            extracted_links=links,
            vector_id=None,
            semantic_summary=None
        )

    @classmethod
    def parse_file(cls, file_path: str, tenant_id: str) -> SensusDocument:
        """Reads a file from disk and parses metadata heuristically without LLMs."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return cls.parse_content(content=content, file_path=file_path, tenant_id=tenant_id)
        except Exception as e:
            print(f"[The Mom] Error reading {file_path}: {e}")
            raise

class SensusSmartPoller(threading.Thread):
    """
    [Aresta CISO - Fritura de SSD]: Polling Customizado com Backoff Exponencial.
    Lê apenas metadados (st_mtime, st_size) e relaxa até 5 minutos se a pasta estiver inerte.
    Protege volumes Docker Bind Mounted de 100% de I/O em discos NVMe.
    """
    def __init__(self, watcher_instance, vault_paths: List[str]):
        super().__init__(daemon=True)
        self.watcher = watcher_instance
        self.vault_paths = vault_paths
        self.running = False
        self.base_interval = 3.0
        self.max_interval = 300.0 # 5 minutos
        self.current_interval = self.base_interval
        self._state_cache = {}

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        print(f"[The Mom Poller] SensusSmartPoller iniciado com Backoff Exponencial (Max: {self.max_interval}s)")
        
        # Pre-fill cache on boot without triggering events
        self._sweep(trigger_events=False)
        
        while self.running:
            time.sleep(self.current_interval)
            
            changes_detected = self._sweep(trigger_events=True)
            
            if changes_detected:
                self.current_interval = self.base_interval
                print(f"[The Mom Poller] Alterações via I/O leve. Backoff resetado para {self.current_interval}s")
            else:
                old_interval = self.current_interval
                self.current_interval = min(self.current_interval * 1.5, self.max_interval)
                if old_interval != self.max_interval and self.current_interval == self.max_interval:
                    print(f"[The Mom Poller] Vault Inerte. Atingiu Backoff Máximo ({self.max_interval}s) para preservar vida útil do SSD.")

    def _sweep(self, trigger_events: bool) -> bool:
        changes = False
        for vault in self.vault_paths:
            if not os.path.exists(vault):
                continue
            ignores = get_ignores(vault)
            for root, dirs, files in os.walk(vault):
                # Apply sovereignignore filter
                dirs[:] = [d for d in dirs if d not in ignores and not d.startswith('.')]
                
                for f in files:
                    if not f.endswith((".md", ".pdf")):
                        continue
                        
                    full_path = os.path.join(root, f)
                    try:
                        stats = os.stat(full_path)
                        state_signature = f"{stats.st_mtime}_{stats.st_size}"
                        
                        if full_path not in self._state_cache:
                            self._state_cache[full_path] = state_signature
                            if trigger_events:
                                self._trigger(full_path)
                                changes = True
                        elif self._state_cache[full_path] != state_signature:
                            self._state_cache[full_path] = state_signature
                            if trigger_events:
                                self._trigger(full_path)
                                changes = True
                    except OSError:
                        # File deleted mid-sweep
                        pass
        return changes
        
    def _trigger(self, full_path: str):
        class DummyEvent:
            is_directory = False
            src_path = full_path
        self.watcher.process_file(DummyEvent())


class VaultWatcher(FileSystemEventHandler):
    """Watches the Sensus Vault for file changes using Inotify/FSEvents or Smart Polling for Bind Mounts."""
    
    def __init__(self, tenant_id: str, vault_paths: List[str] = None):
        self.vault_paths = vault_paths or []
        self.tenant_id = tenant_id
        
        # Decide the engine physics based on OS Due Diligence
        self.use_polling = should_use_polling()
        if self.use_polling:
            print("[The Mom] ⚠️ O.S. Sniffing detetou Bind Mount (Mac/Windows). Ativando SensusSmartPoller.")
            self.observer = SensusSmartPoller(self, self.vault_paths)
        else:
            self.observer = Observer()
            
        self._last_processed = {}
        self._ignores_cache = {}

    def initial_sweep(self):
        """Varre o diretório no boot da API buscando arquivos pré-existentes (Ex: Markdown antigos)."""
        import os
        from src.api.database import SessionLocal
        from src.api.models import SensusDocumentModel
        
        print(f"[The Mom] Inciando varredura histórica (Backfill) em {len(self.vault_paths)} Workspaces Globais")
        db = SessionLocal()
        try:
            # Pegar todos arquivos que já existem no DB para não re-processar atoa
            existing_paths = {doc.file_path for doc in db.query(SensusDocumentModel.file_path).all()}
            
            for vault_path in self.vault_paths:
                if not os.path.exists(vault_path):
                    continue
                for root, dirs, files in os.walk(vault_path):
                    # Ignorar pastas ocultas (como .obsidian, .git)
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        if file.endswith((".md", ".pdf")):
                            full_path = os.path.join(root, file)
                            if full_path not in existing_paths:
                                # Fingimos um evento 'on_created' para cada arquivo antigo
                                class DummyEvent:
                                    is_directory = False
                                    src_path = full_path
                                print(f"[The Mom] Arquivo histórico detectado: {full_path}")
                                self.process_file(DummyEvent())
        finally:
            db.close()
        print(f"[The Mom] Varredura histórica concluída.")

    def schedule_recursively(self, base_path: str):
        """
        Substitui o `recursive=True` do watchdog original para evitar o colapso
        do limite inotify (fs.inotify.max_user_watches) por pastas como node_modules.
        """
        import os
        ignores = get_ignores(base_path)
        self._ignores_cache[base_path] = ignores
        
        count = 0
        for root, dirs, files in os.walk(base_path):
            # Filtra os diretórios in-place para que o os.walk não adentre raízes mortas
            dirs[:] = [d for d in dirs if d not in ignores and not d.startswith('.')]
            
            try:
                self.observer.schedule(self, root, recursive=False)
                count += 1
            except OSError as e:
                print(f"[The Mom] ❌ Limite de Inotify O.S. estourado ao agendar {root}. O sistema de arquivos é grande demais. Use .sovereignignore ou SENSUS_FORCE_POLLING=true. Erro: {e}")
                break
        print(f"[The Mom] Agendado {count} diretórios granulares em {base_path} (Ignorando: {', '.join(list(ignores)[:3])}...)")

    def start(self):
        import os
        for vault_path in self.vault_paths:
            if os.path.exists(vault_path):
                print(f"[The Mom] Starting watch on Workspace: {vault_path}")
                if not self.use_polling:
                    self.schedule_recursively(vault_path)
            else:
                print(f"[Warning] Path {vault_path} not found. Skipping watch.")
                
        if self.vault_paths:
            self.observer.start()
            # Após ligar o guardião de tempo real, indexamos o retroativo:
            self.initial_sweep()

    def stop(self):
        self.observer.stop()
        if not self.use_polling:
            self.observer.join()

    def process_file(self, event):
        if event.is_directory or not event.src_path.lower().endswith(('.md', '.pdf')):
            return
            
        # Basic debouncing
        current_time = time.time()
        if event.src_path in self._last_processed and current_time - self._last_processed[event.src_path] < 1.0:
            return
            
        self._last_processed[event.src_path] = current_time
        
        # Debounce/Wait for file to be actually written to disk (Editors create an empty file first, then write)
        time.sleep(0.5)
        
        print(f"[The Mom] Detected change: {event.src_path} - Parsing deterministic data...")
        try:
            is_pdf = event.src_path.lower().endswith('.pdf')
            # 1. Pipeline para PDFs e The Sentinel Guardrails
            if is_pdf:
                print(f"[The Mom] Starting PDF Extraction via PyMuPDF...")
                raw_text = TheSentinel.dehydrate_pdf(event.src_path)
                
                print(f"[The Mom] Sentinel Guardrail Triggered. Analyzing for Prompt Injections...")
                sentinel_result = TheSentinel.analyze_for_injection(raw_text, self.tenant_id)
                
                if sentinel_result["is_malicious"]:
                    print(f"🚨 [The Mom] ALERTA DE SEGURANÇA: PDF Bloqueado por {sentinel_result['reason']}")
                    from src.api.database import SessionLocal
                    db_session = SessionLocal()
                    try:
                        q_log = QuarantineLog(
                            tenant_id=self.tenant_id,
                            file_path=event.src_path,
                            file_name=os.path.basename(event.src_path),
                            reason=sentinel_result["reason"],
                            ai_confidence=sentinel_result["confidence"],
                            content_snippet=raw_text[:500]
                        )
                        db_session.add(q_log)
                        db_session.commit()
                        print(f"[The Mom] Arquivo '{os.path.basename(event.src_path)}' jogado na Quarentena de Segurança.")
                    except Exception as e:
                        db_session.rollback()
                        print(f"[The Mom] Database Error Logging Quarantine: {e}")
                    finally:
                        db_session.close()
                    return # ABORTA INSERÇÃO NO CHROMA/POSTGRES
                
                # Documento seguro: Montamos a entidade
                doc = SensusDocument(
                    id=uuid.uuid4(),
                    tenant_id=self.tenant_id,
                    file_path=event.src_path,
                    content=raw_text,
                    frontmatter={},
                    extracted_todos=[],
                    extracted_tags=[],
                    extracted_links=[],
                    vector_id=None,
                    semantic_summary=None
                )
            else:
                doc = MarkdownParser.parse_file(file_path=event.src_path, tenant_id=self.tenant_id)
                print(f"[The Mom] Successfully extracted {len(doc.extracted_todos)} todos, {len(doc.extracted_links)} links, {len(doc.extracted_tags)} tags.")
            
            # Save to SQLite
            from src.api.database import SessionLocal
            from src.api.models import SensusDocumentModel
            from sqlalchemy.orm import Session
            
            db: Session = SessionLocal()
            try:
                # Upsert logic based on file_path
                existing = db.query(SensusDocumentModel).filter(SensusDocumentModel.file_path == event.src_path).first()
                if existing:
                    existing.content = doc.content
                    existing.frontmatter = doc.frontmatter
                    existing.extracted_todos = doc.extracted_todos
                    existing.extracted_tags = doc.extracted_tags
                    existing.extracted_links = doc.extracted_links
                else:
                    new_doc = SensusDocumentModel(
                        id=str(doc.id),
                        tenant_id=doc.tenant_id,
                        file_path=doc.file_path,
                        frontmatter=doc.frontmatter,
                        extracted_todos=doc.extracted_todos,
                        extracted_tags=doc.extracted_tags,
                        extracted_links=doc.extracted_links
                    )
                    db.add(new_doc)
                db.commit()
                print(f"[The Mom] Saved deterministic data to Sensus Vault SQLite.")
            except Exception as e:
                db.rollback()
                print(f"[The Mom] DB Error parsing {event.src_path}: {e}")
            finally:
                db.close()
                
        except Exception as e:
            print(f"[The Mom] Failed to process {event.src_path}: {e}")

    def on_created(self, event):
        if event.is_directory:
            name = os.path.basename(event.src_path)
            # Default fallback ignores to protect kernel
            ignores = {".git", "node_modules", ".venv", "venv", ".obsidian", "__pycache__"}
            if name not in ignores and not name.startswith('.'):
                print(f"[The Mom] Novo diretório detetado: {event.src_path}. Injetando watch de inotify sob demanda.")
                try:
                    self.observer.schedule(self, event.src_path, recursive=False)
                except Exception as e:
                    print(f"[The Mom] Erro ao injetar novo listener dinâmico: {e}")
        else:
            self.process_file(event)

    def on_modified(self, event):
        self.process_file(event)

if __name__ == "__main__":
    import time
    # Quick standalone test
    test_vault = os.path.join(os.getcwd(), "data", "test_vault")
    os.makedirs(test_vault, exist_ok=True)
    watcher = VaultWatcher(tenant_id="test_tenant", vault_paths=[test_vault])
    watcher.start()
    try:
        print("[The Mom] Type Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()
