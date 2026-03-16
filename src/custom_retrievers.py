
from typing import List, Optional, Callable, Any
from pathlib import Path
from llama_index.core.retrievers import BaseRetriever
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore, BaseNode
from rank_bm25 import BM25Okapi
import re
import logging

logger = logging.getLogger(__name__)

class CustomBM25Retriever(BaseRetriever):
    """
    Desempenha busca baseada em palavras-chave usando BM25 (Okapi).
    Útil para encontrar termos exatos, datas e identificadores que a busca vetorial perde.
    
    O corpus é enriquecido com metadados (nome do arquivo) para melhorar
    a precisão da busca por títulos e termos presentes no path do documento.
    """
    
    _nodes: Any = None
    _similarity_top_k: int = 5
    _tokenizer: Any = None
    _bm25: Any = None

    def __init__(
        self,
        nodes: List[BaseNode],
        tokenizer: Optional[Callable] = None,
        similarity_top_k: int = 5,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        
        self._nodes = nodes
        self._similarity_top_k = similarity_top_k
        
        # Tokenizador regex: split por qualquer caractere não-alfanumérico
        if tokenizer is None:
            def default_tokenizer(text: str) -> List[str]:
                return [t.lower() for t in re.split(r'\W+', text) if t]
            self._tokenizer = default_tokenizer
        else:
            self._tokenizer = tokenizer
            
        # Construir índice BM25 com corpus enriquecido
        if not nodes:
            logger.warning("🏗️  Passando BM25: Banco de dados parece estar vazio.")
            self._bm25 = None
        else:
            logger.info(f"🏗️  Construindo índice BM25 para {len(nodes)} nós...")
            corpus = [self._tokenizer(self._enrich_with_metadata(node)) for node in nodes]
            self._bm25 = BM25Okapi(corpus)
            logger.info("   ✓ Índice BM25 pronto.")

    @staticmethod
    def _enrich_with_metadata(node: BaseNode) -> str:
        """
        Combina conteúdo + metadados relevantes para indexação BM25.
        Inclui o nome do arquivo no texto para que títulos como 
        'Sensus - Livre-arbítrio' sejam encontráveis por BM25.
        """
        content = node.get_content()
        file_path = node.metadata.get('file_path', '')
        if file_path:
            # Extrair nome do arquivo sem extensão
            # Ex: "2007-12-18 - Sensus - Livre-arbítrio" → tokens: ['2007', '12', '18', 'sensus', 'livre', 'arbítrio']
            file_name = Path(file_path).stem
            content = f"{file_name}\n{content}"
        return content

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        if not self._bm25:
            logger.debug("BM25 Retorno Vazio: Índice BM25 não foi instanciado.")
            return []

        query = query_bundle.query_str
        tokenized_query = self._tokenizer(query)
        logger.debug(f"BM25 Query: {query}")
        logger.debug(f"BM25 Tokens: {tokenized_query}")
        
        # Obter scores
        scores = self._bm25.get_scores(tokenized_query)
        
        # Obter top-k índices (ordenar decrescente)
        top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self._similarity_top_k]
        
        nodes_with_scores = []
        for idx in top_n:
            score = scores[idx]
            if score != 0.0:  # Filtrar documentos estritamente sem nenhum match
                node = self._nodes[idx]
                logger.debug(f"BM25 Hit: {node.metadata.get('file_path', 'unknown')} (Score: {score:.2f})")
                nodes_with_scores.append(NodeWithScore(node=node, score=score))
        
        logger.debug(f"BM25 Total Hits: {len(nodes_with_scores)}")
        return nodes_with_scores

class CustomSqliteVecRetriever(BaseRetriever):
    """
    Retriever Semântico Cíbrido nativo para o Sovereign Pair Agentic Mesh.
    Calcula Distância K-Nearest Neighbors diretamente na extensão SQLite-Vec,
    removendo a necessidade do ChromaDB ou faixas lentas na memória.
    """
    _similarity_top_k: int = 5
    _embed_model: Any = None
    _db_session: Any = None
    _tenant_id: str = "default"

    def __init__(
        self,
        embed_model: Any,
        db_session: Any,
        tenant_id: str = "default",
        similarity_top_k: int = 5,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._embed_model = embed_model
        self._db_session = db_session
        self._tenant_id = tenant_id
        self._similarity_top_k = similarity_top_k

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        from llama_index.core.schema import TextNode
        from sqlalchemy.sql import text
        import struct
        import json

        try:
            # 1. Obter o vetor F32 (Embeddings via Nomic Nomic/Ollama)
            query_embedding = self._embed_model.get_text_embedding(query_bundle.query_str)
            
            # 2. Empacotar float[] para bytes brutos que o sqlite-vec em C consegue chupar imediatamente
            # O sqlite-vec f32 usa little-endian (struct pack 'f')
            query_f32_blob = struct.pack(f"{len(query_embedding)}f", *query_embedding)
            
            # 3. Cruzar VIRTUAL TABLE (Busca Rápida L2/Cosine) com a Tabela Relacional Base
            # Sintaxe do vec0: WHERE embedding MATCH ? AND k = ?
            sql = text("""
                SELECT c.chunk_id, c.text_content, c.metadata_json, v.distance 
                FROM sovereign_vectors v
                JOIN sovereign_chunks c ON c.chunk_id = v.chunk_id
                WHERE v.embedding MATCH :embedding AND v.k = :k AND c.tenant_id = :tenant_id
                ORDER BY v.distance ASC
            """)
            
            result = self._db_session.execute(sql, {
                "embedding": query_f32_blob,
                "k": self._similarity_top_k,
                "tenant_id": self._tenant_id
            })
            
            nodes_with_scores = []
            for row in result.fetchall():
                chunk_id_val, text_content_val, metadata_json_str, distance_val = row
                
                metadata = json.loads(metadata_json_str) if metadata_json_str else {}
                
                node = TextNode(
                    id_=str(chunk_id_val),
                    text=text_content_val,
                    metadata=metadata
                )
                
                # Para distances L2 ou Cosine, converter logicamente para 0.0 ~ 1.0 Similaridade
                score = 1.0 / (1.0 + float(distance_val))
                nodes_with_scores.append(NodeWithScore(node=node, score=score))
                
            logger.info(f"   ✓ {len(nodes_with_scores)} matches Cíbridos encontrados com sucesso.")
            return nodes_with_scores
            
        except Exception as e:
            logger.error(f"🚨 [SQLite-Vec] Erro durante o K-NN Retrieval: {e}")
            return []

