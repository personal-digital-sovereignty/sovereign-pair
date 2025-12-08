
from typing import List, Optional
from llama_index.core.retrievers import BaseRetriever
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore, BaseNode
from rank_bm25 import BM25Okapi
import logging

logger = logging.getLogger(__name__)

class CustomBM25Retriever(BaseRetriever):
    """
    Desempenha busca baseada em palavras-chave usando BM25 (Okapi).
    Útil para encontrar termos exatos, datas e identificadores que a busca vetorial perde.
    """
    def __init__(
        self,
        nodes: List[BaseNode],
        tokenizer: Optional[callable] = None,
        similarity_top_k: int = 5,
    ) -> None:
        self._nodes = nodes
        self._similarity_top_k = similarity_top_k
        
        # Tokenizador simples se não fornecido
        if tokenizer is None:
            import re
            def default_tokenizer(text: str):
                # Split por qualquer caractere não-alfanumérico (remove pontuação)
                return [t.lower() for t in re.split(r'\W+', text) if t]
            self._tokenizer = default_tokenizer
        else:
            self._tokenizer = tokenizer
            
        # Construir índice BM25
        logger.info(f"🏗️  Construindo índice BM25 para {len(nodes)} nós...")
        corpus = [self._tokenizer(node.get_content()) for node in nodes]
        self._bm25 = BM25Okapi(corpus)
        logger.info("   ✓ Índice BM25 pronto.")
        
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        query = query_bundle.query_str
        tokenized_query = self._tokenizer(query)
        print(f"[DEBUG] BM25 Query: {query}")
        print(f"[DEBUG] Tokens: {tokenized_query}")
        
        # Obter scores
        scores = self._bm25.get_scores(tokenized_query)
        
        # Obter top-k índices
        # Ordenar decrescente e pegar os top_k indices
        top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self._similarity_top_k]
        
        nodes_with_scores = []
        for idx in top_n:
            score = scores[idx]
            if score > 0: # Filtrar resultados irrelevantes
                node = self._nodes[idx]
                print(f"[DEBUG] BM25 Hit: {node.metadata.get('file_path', 'unknown')} (Score: {score})")
                nodes_with_scores.append(NodeWithScore(node=node, score=score))
        
        print(f"[DEBUG] BM25 Total Hits: {len(nodes_with_scores)}")
        return nodes_with_scores
