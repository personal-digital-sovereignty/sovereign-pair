import logging
from typing import List, Optional
from pydantic import Field, PrivateAttr
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle
from flashrank import Ranker, RerankRequest

logger = logging.getLogger(__name__)

class FlashrankReranker(BaseNodePostprocessor):
    """
    Reranker nativo super-rápido baseado em FlashRank, executando modelos cross-encoder na CPU
    sem necessidade de Torch/GPU pesados para o ranqueamento.
    A "Pílula RAG" oficial do Sovereign Pair.
    """
    model_name: str = Field(default="ms-marco-MiniLM-L-12-v2")
    top_n: int = Field(default=3)
    
    _ranker: Optional[Ranker] = PrivateAttr(default=None)
    
    def __init__(self, top_n: int = 3, model_name: str = "ms-marco-MiniLM-L-12-v2", **kwargs):
        super().__init__(top_n=top_n, model_name=model_name, **kwargs)
        self._ranker = Ranker(model_name=self.model_name, cache_dir="/tmp/flashrank_cache")
        logger.info(f"⚡ FlashRank Inicializado ({self.model_name}) - Destilando Top {self.top_n} Chunks.")

    def _postprocess_nodes(
        self, nodes: List[NodeWithScore], query_bundle: Optional[QueryBundle] = None
    ) -> List[NodeWithScore]:
        if query_bundle is None or not nodes:
            return nodes

        query = query_bundle.query_str
        
        # Extract text context
        passages = [
            {
                "id": str(idx),
                "text": node.node.get_content()
            }
            for idx, node in enumerate(nodes)
        ]
        
        try:
            request = RerankRequest(query=query, passages=passages)
            results = self._ranker.rerank(request)
            
            # Reconstruct Nodes
            reranked_nodes = []
            for res in results[:self.top_n]:
                idx = int(res["id"])
                original_node = nodes[idx]
                original_node.score = res.get("score", 0.0)
                reranked_nodes.append(original_node)
                
            logger.info(f"⚡ [FlashRank RAG] {len(nodes)} Chunks Originais esmagados para os top {len(reranked_nodes)} (Evitando Context Spam).")
            return reranked_nodes
            
        except Exception as e:
            logger.error(f"⚠️ Erro ao aplicar FlashrankReranker: {e}")
            return nodes[:self.top_n] # Fallback silencioso
