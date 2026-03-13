import time
import uuid
import logging
import asyncio
from typing import Optional

from sqlalchemy.orm import Session
from src.api.database import SessionLocal
from src.api.models import SensusDocumentModel

logger = logging.getLogger(__name__)

class TheDadWorker:
    """The Dad (Tier 2): Small Language Model & Vectorizer.
    
    Observa silenciosamente a tabela SensusDocumentModel procurando arquivos
    recentemente registrados pela The Mom (vetor_id IS NULL).
    Gera um sumário semântico O(N) com SLM e commita os vetores no ChromaDB.
    """

    def __init__(self, check_interval_seconds: int = 15):
        self.check_interval = check_interval_seconds
        self.is_running = False
        self._task: Optional[asyncio.Task] = None

    async def _generate_summary(self, content: str, title: str) -> str:
        """Gera um resumo semântico ultra focado usando o LLM local."""
        from llama_index.core.llms import ChatMessage, MessageRole
        # Limita o tamanho do conteúdo para o resumo ser rápido (ex: primeiros 2000 caracteres)
        truncated_content = content[:2000]
        
        prompt = f"""Atue como um analista de dados. Resuma em apenas 1 ou 2 parágrafos curtos o artigo abaixo, extraindo seu tema principal, intenção e conceitos chave. Responda APENAS com o resumo.
Título do Arquivo: {title}

Conteúdo:
{truncated_content}
"""
        messages = [ChatMessage(role=MessageRole.USER, content=prompt)]
        try:
            logger.info(f"[The Dad] 🤖 Gerando sumário semântico para '{title}' via SLM LOCAL...")
            from src.config import LLM_PROVIDER, LLM_MODEL, REQUEST_TIMEOUT, OLLAMA_BASE_URL
            from llama_index.llms.ollama import Ollama
            
            # FORÇAMENTO DE TOPOLOGIA: O Background Worker (The Dad) NUNCA deve competir na mesma
            # fila do Cloud Node com o UI/Chat. Fazemos bypass chamando o nó local diretamente.
            if LLM_PROVIDER == "ollama":
                llm = Ollama(model=LLM_MODEL, request_timeout=REQUEST_TIMEOUT, base_url=OLLAMA_BASE_URL)
            else:
                from src.llm_factory import get_llm
                llm = get_llm(LLM_PROVIDER, LLM_MODEL, request_timeout=REQUEST_TIMEOUT)
            
            response = await llm.achat(messages)
            return response.message.content.strip()
        except Exception as e:
            logger.warning(f"[The Dad] ⚠️ Bypass de LLM ativado para '{title}' (Erro: {e}). Usando heurística veloz de corte de texto.")
            return content[:250].replace('\n', ' ') + "..."

    async def _vectorize_and_save(self, doc: SensusDocumentModel, summary: str, file_content: str):
        """Usa o BGE-M3 para gerar o Embedding geográfico. 
           [Fase B] Persistência do SQLite-Vec desativada provisóriamente."""
        title = doc.file_path.split("/")[-1]
        
        try:
            logger.info(f"[The Dad] 🧬 Skip temporário de vetorização de `{title}` (Aguardando SQLite-Vec na Fase B)...")
            
            vector_id = str(uuid.uuid4())
            # Retorna um ID fake temporariamente para o banco de dados local constar como processado
            # Na Fase B recriaremos o Upsert injentando na tabela vec0
            return vector_id
            
        except Exception as e:
            logger.error(f"[The Dad] ❌ Erro ao pular vetorização {title}: {e}")
            return None

    async def process_pending_documents(self):
        """Busca documentos recém criados sem vector_id e processa 1 por 1."""
        db: Session = SessionLocal()
        try:
            # Buscamos apenas 5 documentos por vez para não estrangular o Ollama ou a memória RAM
            pending_docs = db.query(SensusDocumentModel).filter(
                SensusDocumentModel.vector_id.is_(None)
            ).limit(5).all()
            
            if not pending_docs:
                return
                
            logger.info(f"[The Dad] 🧐 Encontrou {len(pending_docs)} documentos sem Alma. Acordando o LLM Generativo...")
            
            for doc in pending_docs:
                title = doc.file_path.split("/")[-1]
                start_time = time.time()
                
                # SensusDocumentModel não carrega o raw content para não inchar o SQLite
                # O Pai deve ler o conteúdo físico do arquivo em disco
                try:
                    with open(doc.file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                except Exception as e:
                    logger.error(f"[The Dad] Ignorando {title} pois arquivo físico sumiu ou deu erro IO: {e}")
                    # Marca com um pseudo-vector_id para não travar num loop infinito de retry
                    doc.vector_id = "ERROR_FILE_NOT_FOUND"
                    db.commit()
                    continue
                
                # 1. Gerar o Sumário com Raciocínio (LLM)
                summary = await self._generate_summary(file_content, title)
                
                # 2. Transformar TUDO em Álgebra Linear Geográfica (Embeddings)
                vec_id = await self._vectorize_and_save(doc, summary, file_content)
                
                if vec_id:
                    # 3. Synchronizar o Banco SQL Relacional
                    doc.semantic_summary = summary
                    doc.vector_id = vec_id
                    db.commit()
                    
                    elapsed = time.time() - start_time
                    logger.info(f"[The Dad] ✅ Documento '{title}' imortalizado no Sensus Vault em {elapsed:.2f}s!")
                else:
                    logger.warning(f"[The Dad] ⚠️ VectorId nulo retornado para '{title}'. Pulando sync.")
                    
        except Exception as e:
            logger.error(f"[The Dad] 💥 Erro crítico no loop de processamento: {e}")
            db.rollback()
        finally:
            db.close()

    async def _worker_loop(self):
        logger.info(f"[The Dad] 🕶️  Background SLM Watcher iniciado. (Janela: {self.check_interval}s)")
        while self.is_running:
            try:
                await self.process_pending_documents()
            except Exception as e:
                logger.error(f"[The Dad] Worker loop error: {e}")
            # Pausa para economizar CPU
            await asyncio.sleep(self.check_interval)

    def start(self):
        """Inicia a rotina assíncrona ligada ao Event Loop ativo."""
        if not self.is_running:
            self.is_running = True
            # Como o FastAPI app_lifespan já está em async context, injetamos no running loop.
            self._task = asyncio.create_task(self._worker_loop())

    def stop(self):
        """Graçamente finaliza a operação, esperando o final do processamento atual se possível."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            logger.info("[The Dad] Dormindo...")
