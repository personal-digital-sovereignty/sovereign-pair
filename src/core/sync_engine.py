import os
import yaml
from datetime import datetime, timezone
from typing import Dict, Any, Union

from src.api.models import ProjectModel, TaskModel, NoteModel
from src.config import VAULT_DIR

# -------------------------------------------------------------------------
# SENSUS VAULT: BINDING ENGINE (TWO-WAY SYNC)
# -------------------------------------------------------------------------
# O Sync Engine é o elo mágico entre o Banco de Dados Rígido (SQLite)
# e a "Soberania de Arquivo" do usuário (Markdown).

def serialize_to_frontmatter(entity: Union[ProjectModel, TaskModel, NoteModel], entity_type: str) -> Dict[str, Any]:
    """Extrai os metadados do banco para construir o Frontmatter YAML."""
    if entity_type == "project":
        return {
            "sensus_id": entity.id,
            "type": "project",
            "status": entity.traction_status,
            "energy_level": entity.energy_level,
            "progress": f"{entity.progress_percent}%",
            "deadline": entity.deadline or "",
            "last_synced": datetime.now(timezone.utc).isoformat()
        }
    elif entity_type == "task":
        return {
            "sensus_id": entity.id,
            "project_id": entity.project_id,
            "type": "task",
            "status": entity.status,
            "priority": entity.priority,
            "deadline": entity.deadline or "",
            "last_synced": datetime.now(timezone.utc).isoformat()
        }
    elif entity_type == "note":
        return {
            "sensus_id": entity.id,
            "project_id": entity.project_id,
            "type": "note",
            "pinned": entity.is_pinned,
            "tags": entity.tags or [],
            "last_synced": datetime.now(timezone.utc).isoformat()
        }
    return {}

def build_markdown_content(entity: Union[ProjectModel, TaskModel, NoteModel], entity_type: str) -> str:
    """Monta a string final do Arquivo (YAML Frontmatter + Body)."""
    frontmatter = serialize_to_frontmatter(entity, entity_type)
    yaml_header = yaml.dump(frontmatter, sort_keys=False, allow_unicode=True)
    
    content_blocks = [f"---\n{yaml_header}---\n"]
    
    # Body Builder
    if entity_type == "project":
        content_blocks.append(f"# {entity.name}\n\n")
        if entity.purpose:
            content_blocks.append(f"## Purpose\n{entity.purpose}\n\n")
        if entity.next_action:
            content_blocks.append(f"## Next Action\n{entity.next_action}\n\n")
        if entity.friction_radar:
            content_blocks.append(f"## Friction Radar\n{entity.friction_radar}\n\n")
            
    elif entity_type == "task":
        content_blocks.append(f"# {entity.title}\n\n")
        if entity.description:
            content_blocks.append(f"{entity.description}\n\n")
            
    elif entity_type == "note":
        content_blocks.append(f"# {entity.title}\n\n")
        if entity.content:
            content_blocks.append(f"{entity.content}\n\n")

    return "".join(content_blocks)

def save_to_markdown(entity: Union[ProjectModel, TaskModel, NoteModel], entity_type: str) -> str:
    """
    Grava o estado atual do banco no sistema de arquivos físico (Markdown).
    Retorna o filepath absoluto.
    """
    # Define a pasta destino de acordo com o tipo
    # Ex: ~/Documents/Projects/Sovereign-Pair/Projects/
    folder_mapping = {
        "project": "Projects",
        "task": "Tasks",
        "note": "Notes"
    }
    
    target_folder = VAULT_DIR / folder_mapping.get(entity_type, "Uncategorized")
    target_folder.mkdir(parents=True, exist_ok=True)
    
    # Sanitiza o nome do arquivo (title ou name)
    raw_name = getattr(entity, 'name', getattr(entity, 'title', entity.id))
    safe_name = "".join([c if c.isalnum() else "_" for c in raw_name]).strip("_")
    filename = f"{safe_name}.md"
    
    file_path = target_folder / filename
    markdown_content = build_markdown_content(entity, entity_type)
    
    # Escrita Física
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    return str(file_path.resolve())

def check_sync_status(file_path: str, db_updated_at: datetime) -> dict:
    """
    Analisa se o arquivo Markdown bate com a fonte de verdade do banco (SQLite).
    Se o 'mtime' do arquivo for mais novo que a gravação do SQLite, há conflito (Diff needed).
    """
    if not file_path or not os.path.exists(file_path):
        return {"status": "LOST", "message": "File not found on disk."}
        
    file_stat = os.stat(file_path)
    # Convert file mtime to UTC timezone-aware datetime
    file_mtime = datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc)
    
    # Calculando a diferença em segundos (margem de tolerância de 2 segundos para atrasos de file system)
    diff_seconds = (file_mtime - db_updated_at).total_seconds()
    
    if diff_seconds > 2.0:
        return {
            "status": "CONFLICT",
            "message": "Markdown file is newer than Database record.",
            "file_mtime": file_mtime.isoformat(),
            "db_update": db_updated_at.isoformat(),
            "diff_seconds": diff_seconds
        }
    else:
        return {
            "status": "SYNCED",
            "message": "Database is the single source of truth.",
        }
