
from typing import List, Optional
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
    def __init__(
        self,
        nodes: List[BaseNode],
        tokenizer: Optional[callable] = None,
        similarity_top_k: int = 5,
    ) -> None:
        self._nodes = nodes
        self._similarity_top_k = similarity_top_k
        
        # Tokenizador regex: split por qualquer caractere não-alfanumérico
        if tokenizer is None:
            def default_tokenizer(text: str):
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
        
        super().__init__()

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
            if score > 0:  # Filtrar resultados irrelevantes
                node = self._nodes[idx]
                logger.debug(f"BM25 Hit: {node.metadata.get('file_path', 'unknown')} (Score: {score:.2f})")
                nodes_with_scores.append(NodeWithScore(node=node, score=score))
        
        logger.debug(f"BM25 Total Hits: {len(nodes_with_scores)}")
        return nodes_with_scores
