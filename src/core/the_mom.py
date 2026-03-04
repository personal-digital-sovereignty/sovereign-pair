import os
import re
import yaml
import uuid
import time
from datetime import datetime
import uuid
from typing import Dict, Any, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

class VaultWatcher(FileSystemEventHandler):
    """Watches the Sensus Vault for file changes using Inotify/FSEvents."""
    
    def __init__(self, tenant_id: str, vault_paths: List[str] = None):
        self.vault_paths = vault_paths or []
        self.tenant_id = tenant_id
        self.observer = Observer()
        self._last_processed = {}

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
                        if file.endswith(".md"):
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

    def start(self):
        import os
        for vault_path in self.vault_paths:
            if os.path.exists(vault_path):
                print(f"[The Mom] Starting silent watch on Workspace: {vault_path}")
                self.observer.schedule(self, vault_path, recursive=True)
            else:
                print(f"[Warning] Path {vault_path} not found. Skipping watch.")
                
        if self.vault_paths:
            self.observer.start()
            # Após ligar o guardião de tempo real, indexamos o retroativo:
            self.initial_sweep()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def process_file(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
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
