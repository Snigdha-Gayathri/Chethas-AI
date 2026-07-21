from __future__ import annotations
import time
from typing import Any
from .base import BaseStrategy
from ..models import RetrievalConfig, RetrievalResult
from app.storage.vector_store import VectorStore

class HybridRetrievalStrategy(BaseStrategy):
    name = "hybrid_retrieval"
    description = "Dense + Sparse search with Reciprocal Rank Fusion."
    
    def __init__(self):
        self.vector_store = VectorStore()
        
    async def retrieve(self, config: RetrievalConfig) -> RetrievalResult:
        start_time = time.time()
        
        docs = await self.vector_store.search_hybrid(
            query=config.query,
            top_k=config.top_k,
            document_ids=config.document_ids
        )
        
        chunks = []
        for doc in docs:
            chunks.append({
                "content": doc.get("content", ""),
                "metadata": doc.get("metadata", {}),
                "score": doc.get("score", 0.0)
            })
            
        retrieval_time_ms = int((time.time() - start_time) * 1000)
        confidence = chunks[0]["score"] if chunks else 0.0
        
        return RetrievalResult(
            query=config.query,
            strategy_used=self.name,
            strategy_reasoning="", 
            chunks=chunks,
            total_candidates=len(chunks),
            retrieval_time_ms=retrieval_time_ms,
            confidence=confidence
        )
