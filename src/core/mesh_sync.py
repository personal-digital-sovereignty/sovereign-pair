import time
import logging
import asyncio
import httpx
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from src.config import OCI_MESH_URL, OCI_MESH_TOKEN
from src.api.database import SessionLocal

logger = logging.getLogger(__name__)

class MeshSyncWorker:
    """Malha Mesh Sovereign Async-Sync (Puller Local).
    
    Este Worker roda no Nó Doméstico (Edge). Sua função principal é acordar periodicamente,
    comunicar-se com a nuvem mestra OCI (A1) e fazer PULL de todos os Chunks de inteligência
    raspados pela internet que não estão em nossa base nativa local.
    """
    
    def __init__(self, check_interval_seconds: int = 3600):
        # Default: 1 hora
        self.check_interval = check_interval_seconds
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        
    async def _fetch_and_sync(self):
        if not OCI_MESH_URL:
            return # Mesh Desligada. Sem P2P tunelamento
            
        db: Session = SessionLocal()
        try:
            # 1. Obter a data da nossa inteligência mais recente
            result = db.execute(text("SELECT MAX(created_at) FROM sovereign_chunks"))
            latest_date = result.scalar()
            
            # Parametrizar a Busca na Nuvem Mestra via P2P
            params = {}
            if latest_date:
                # OCI_MESH aguarda formato ISO para parseamento datetime
                params["since"] = latest_date
                
            headers = {}
            if OCI_MESH_TOKEN:
                 headers["Authorization"] = f"Bearer {OCI_MESH_TOKEN}"
                 
            logger.info(f"🌐 [Mesh Sync] Sondando a Nuvem OCI A1 por novos conhecimentos... ({OCI_MESH_URL})")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{OCI_MESH_URL}/v1/blue-collar/sync", params=params, headers=headers)
                
                if response.status_code == 200:
                    chunks = response.json()
                    
                    if not chunks:
                        logger.info("🌐 [Mesh Sync] Edge local já está 100% Sincronizado com a Sabedoria da Nuvem.")
                        return
                        
                    logger.info(f"🌐 [Mesh Sync] Baixando pacote {len(chunks)} Novos Chunks da Nuvem A1!")
                    
                    # 2. Injetar Conhecimento da Nuvem na Memória SQLite Nativa
                    for chunk in chunks:
                        try:
                            # Prevenção simples contra duplata exata usando arquivo + text hash
                            check = db.execute(
                                text("SELECT 1 FROM sovereign_chunks WHERE uuid_reference = :ui AND text_content = :tc"),
                                {"ui": chunk['uuid_reference'], "tc": chunk['text_content']}
                            ).fetchone()
                            
                            if not check:
                                db.execute(
                                    text("""
                                    INSERT INTO sovereign_chunks (uuid_reference, tenant_id, file_path, text_content, metadata_json, created_at)
                                    VALUES (:uuid, :tenant, :fp, :tc, :meta, :ca)
                                    """),
                                    {
                                        "uuid": chunk['uuid_reference'],
                                        "tenant": chunk['tenant_id'],
                                        "fp": chunk['file_path'],
                                        "tc": chunk['text_content'],
                                        "meta": chunk.get('metadata_json', '{}'),
                                        "ca": chunk.get('created_at', str(datetime.now()))
                                    }
                                )
                                # Obs: O TheDadWorker Local engolirá esses textos soltos na tabela base 
                                # ou aplicará os vetores usando GPU local em Fase B.
                        except Exception as inner_e:
                            logger.error(f"🌐 [Mesh Sync] Falha ao injetar clone chunk: {inner_e}")
                            
                    db.commit()
                    logger.info("✅ [Mesh Sync] Sabedoria Baixada e Consolidada no Edge SQLite com Sucesso.")
                else:
                    logger.error(f"❌ [Mesh Sync] Falha de Comunicação com OCI Mestra HTTP {response.status_code} - {response.text}")
                    
        except httpx.RequestError as req_err:
             logger.warning(f"⚠️ [Mesh Sync] Ponto Cego! Nuvem OCI Inacessível: {req_err}")
        except Exception as e:
            logger.error(f"💥 [Mesh Sync] Erro não mapeado no PULL da Malha Local: {e}")
            db.rollback()
        finally:
            db.close()

    async def _worker_loop(self):
        if not OCI_MESH_URL:
            logger.info("🌐 [Mesh Sync] Desligado. (Nó Solitário/Nu - Configure OCI_MESH_URL)")
            return
            
        logger.info(f"🌐 [Mesh Sync] Puller de Conhecimento Iniciado! Acordará a cada {self.check_interval}s para Sync com A1.")
        while self.is_running:
            try:
                await self._fetch_and_sync()
            except Exception as e:
                logger.error(f"[Mesh Sync] Loop Crash: {e}")
            
            await asyncio.sleep(self.check_interval)

    def start(self):
        if self.is_running:
             return
             
        self.is_running = True
        self._task = asyncio.create_task(self._worker_loop())

    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            logger.info("🌐 [Mesh Sync] Dormindo permanentemente.")
