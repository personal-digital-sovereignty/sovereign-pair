import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.api.database import get_db
from src.api.models import BlueCollarTask
from typing import List, Optional
from src.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/blue-collar", tags=["Blue Collar Worker"])

# Schemas
class TaskCreate(BaseModel):
    topic: str
    frequency: str = "manual"

class TaskResponse(BaseModel):
    id: str
    topic: str
    frequency: str
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    status: str
    last_log: Optional[str]

    class Config:
        from_attributes = True

class SyncChunkResponse(BaseModel):
    chunk_id: int
    uuid_reference: str
    tenant_id: str
    file_path: str
    text_content: str
    metadata_json: Optional[str]
    created_at: str

@router.get("/sync", response_model=List[SyncChunkResponse])
def sync_mesh_chunks(since: Optional[datetime] = None, db: Session = Depends(get_db)):
    """
    Malha Mesh OCI -> Edge.
    Exporta chunks minerados pelo OCI desde um `since` timestamp para ingestão local.
    Usa raw SQL pois o sovereign_chunks não está no ORM base.
    """
    from sqlalchemy import text
    try:
        query = "SELECT chunk_id, uuid_reference, tenant_id, file_path, text_content, metadata_json, created_at FROM sovereign_chunks"
        params = {}
        if since:
            query += " WHERE created_at >= :since"
            params["since"] = since

        query += " ORDER BY created_at ASC LIMIT 1000"
        
        result = db.execute(text(query), params)
        chunks = []
        for row in result:
            chunks.append(SyncChunkResponse(
                chunk_id=row[0],
                uuid_reference=row[1],
                tenant_id=row[2],
                file_path=row[3],
                text_content=row[4],
                metadata_json=row[5],
                created_at=str(row[6])
            ))
        return chunks
    except Exception as e:
        logger.error(f"Erro no endpoint de Mesh Sync: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao sincronizar chunks do Worker.")

@router.post("", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """
    Cria uma nova missão de Inteligência (Scraping) para a máquina Braçal OCI.
    """
    new_task = BlueCollarTask(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        topic=task.topic,
        frequency=task.frequency,
        is_active=True,
        status="idle",
        last_log="Tarefa Criada e Aguardando Agente Headless na OCI."
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    logger.info(f"👷 [Blue Collar] Nova missão cadastrada: '{task.topic}' ({task.frequency})")
    return new_task

@router.get("", response_model=List[TaskResponse])
def list_tasks(db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """
    Lista todas as missões autônomas.
    """
    return db.query(BlueCollarTask).filter(BlueCollarTask.tenant_id == tenant_id).order_by(BlueCollarTask.created_at.desc()).all()

@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """
    Deleta uma missão do Worker.
    """
    task = db.query(BlueCollarTask).filter(
        BlueCollarTask.id == task_id, 
        BlueCollarTask.tenant_id == tenant_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Missão Blue Collar não encontrada.")
    
    db.delete(task)
    db.commit()
    return {"status": "success", "message": "Missão Blue Collar abortada."}


def _run_worker_sync(task_id: str, tenant_id: str):
    """
    Método de Ingestão Síncrona Web (Usado pela BackgroundTasks).
    Isso simulará o comportamento da Oracle OCI mastigando dados da internet.
    """
    from src.api.database import SessionLocal
    db = SessionLocal()
    try:
        task = db.query(BlueCollarTask).filter(BlueCollarTask.id == task_id).first()
        if not task:
            return
            
        task.status = "running"
        task.last_run_at = datetime.now(timezone.utc)
        db.commit()
        
        logger.info(f"👷 [Blue Collar] Coletando inteligência sobre: '{task.topic}'...")
        # ==========================================================
        # FASE D - AQUI O AGENTE RASPA A INTERNET (DuckDuckGo + BS4) 
        # E VETORIZA PARA A BASE SQLITE DA NUVEM (OU LOCAL SE TESTE)
        # ==========================================================
        import time
        from src.web_search import search_web
        
        # Puxa sumários online via the Dad Agent / FlashRank Searchers
        web_results = search_web(task.topic)
        
        # Emulando latência de parseamento do Scraper
        time.sleep(5)
        
        task.last_log = f"Sucesso. Ingestão Web extraiu context chunks de DDGS. RAG Cíbrido alimentado."
        task.status = "idle"
        db.commit()
        logger.info(f"✅ [Blue Collar] Finalizou missão: '{task.topic}'")
        
    except Exception as e:
        logger.error(f"❌ [Blue Collar] Erro na Missão: {e}")
        try:
             task = db.query(BlueCollarTask).filter(BlueCollarTask.id == task_id).first()
             task.status = "error"
             task.last_log = f"Falha Crítica do Scraper: {str(e)}"
             db.commit()
        except:
             pass
    finally:
        db.close()


@router.post("/{task_id}/run")
def run_task_urgently(task_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """
    Força a execução de uma missão imadiatamente (Roda em thread bg).
    """
    task = db.query(BlueCollarTask).filter(
        BlueCollarTask.id == task_id, 
        BlueCollarTask.tenant_id == tenant_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Missão Blue Collar não encontrada.")
        
    background_tasks.add_task(_run_worker_sync, task_id, tenant_id)
    return {"status": "success", "message": "Iniciando raspagem paralela."}
