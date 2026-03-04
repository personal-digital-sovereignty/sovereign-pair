import os
import json
import logging
import threading
import select
import time
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)

class SovereignMessageBroker(threading.Thread):
    """
    [Aresta CISO - Paradoxo do Redis]: Usa o Pub/Sub nativo do PostgreSQL (LISTEN/NOTIFY)
    como Message Broker leve para Orquestração Event-Driven de Agentes.
    Evita o uso e a manutenção de containers Redis e do LangGraph.
    
    Fallback Arquitetural: Se rodar sob SQLite (Sovereign Node Edition),
    degrada graciosamente para chamadas diretas in-memory.
    """
    def __init__(self, db_url: str):
        super().__init__(daemon=True)
        self.db_url = db_url or ""
        self.running = False
        self.channels: Dict[str, Callable] = {}
        self._conn = None
        
    def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """Registra um worker para escutar eventos na fila."""
        self.channels[channel] = callback
        
    def _connect(self):
        if not self.db_url.startswith("postgres"):
            return
            
        import psycopg2
        import psycopg2.extensions
        if not self._conn or self._conn.closed:
            self._conn = psycopg2.connect(self.db_url)
            self._conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            
    def run(self):
        if not self.db_url.startswith("postgres"):
            logger.warning("[Bare-Metal IPC] ⚠️ Banco não é PostgreSQL (SQLite detectado). A Orquestração de Agentes usará roteamento In-Memory nativo (Node Edition).")
            return

        self.running = True
        self._connect()
        curs = self._conn.cursor()
        
        for ch in self.channels.keys():
            logger.info(f"[Bare-Metal IPC] 🎧 Escutando Canal Postgres: {ch}")
            curs.execute(f"LISTEN {ch};")
            
        logger.info("[Bare-Metal IPC] 🟢 Orquestrador Event-Driven PostgreSQL Iniciado.")
        
        while self.running:
            try:
                if select.select([self._conn], [], [], 3.0) == ([], [], []):
                    continue
                self._conn.poll()
                while self._conn.notifies:
                    notify = self._conn.notifies.pop(0)
                    if notify.channel in self.channels:
                        try:
                            payload = json.loads(notify.payload)
                            self.channels[notify.channel](payload)
                        except Exception as e:
                            logger.error(f"[Bare-Metal IPC] Erro no callback {notify.channel}: {e}")
            except Exception as e:
                logger.error(f"[Bare-Metal IPC] Desconexão do Broker: {e}")
                time.sleep(5)
                self._connect()

    def publish(self, channel: str, payload_dict: Dict[str, Any]):
        """Publica mensagem (intent) na nuvem."""
        if not self.db_url.startswith("postgres"):
            # Roteamento in-memory síncrono para Desktop SQLite
            if channel in self.channels:
                self.channels[channel](payload_dict)
            return

        self._connect()
        curs = self._conn.cursor()
        payload_str = json.dumps(payload_dict).replace("'", "''")
        curs.execute(f"NOTIFY {channel}, '{payload_str}';")
