from __future__ import annotations
import time
from typing import Any
from .base import BaseStrategy
from ..models import RetrievalConfig, RetrievalResult
from app.storage.vector_store import VectorStore

class ParentChildStrategy(BaseStrategy):
    name = "parent_child"
    description = "Hierarchical retrieval: search small child chunks and retrieve full parent context."
    
    def __init__(self):
        self.vector_store = VectorStore()
        
    async def retrieve(self, config: RetrievalConfig) -> RetrievalResult:
        start_time = time.time()
        
        child_docs = await self.vector_store.search_semantic(
            query=config.query,
            top_k=config.top_k,
            document_ids=config.document_ids
        )
        
        parent_ids = list(set([
            doc.get("metadata", {}).get("parent_id") 
            for doc in child_docs 
            if doc.get("metadata", {}).get("parent_id")
        ]))
        
        chunks = []
        if parent_ids:
            parent_docs = await self.vector_store.search_semantic(
                query="", 
                top_k=len(parent_ids),
                document_ids=parent_ids
            )
            for doc in parent_docs:
                chunks.append({
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {}),
                    "score": doc.get("score", 0.0)
                })
        else:
            for doc in child_docs:
                chunks.append({
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {}),
                    "score": doc.get("score", 0.0)
                })
            
        retrieval_time_ms = int((time.time() - start_time) * 1000)
        confidence = child_docs[0].get("score", 0.0) if child_docs else 0.0
        
        return RetrievalResult(
            query=config.query,
            strategy_used=self.name,
            strategy_reasoning="",
            chunks=chunks,
            total_candidates=len(chunks),
            retrieval_time_ms=retrieval_time_ms,
            confidence=confidence
        )
