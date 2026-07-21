from __future__ import annotations
import time
from typing import Any
from .base import BaseStrategy
from ..models import RetrievalConfig, RetrievalResult
from app.storage.vector_store import VectorStore

class LongContextStrategy(BaseStrategy):
    name = "long_context"
    description = "Full document retrieval for contextually small corpora."
    
    def __init__(self):
        self.vector_store = VectorStore()
        
    async def retrieve(self, config: RetrievalConfig) -> RetrievalResult:
        start_time = time.time()
        
        docs = await self.vector_store.search_semantic(
            query=config.query,
            top_k=50, 
            document_ids=config.document_ids
        )
        
        doc_contents = {}
        for doc in docs:
            doc_id = doc.get("metadata", {}).get("document_id", "unknown")
            if doc_id not in doc_contents:
                doc_contents[doc_id] = []
            doc_contents[doc_id].append(doc.get("content", ""))
            
        chunks = []
        for doc_id, text_list in doc_contents.items():
            full_text = "\n".join(text_list)
            chunks.append({
                "content": full_text,
                "metadata": {"document_id": doc_id, "long_context": True},
                "score": 1.0
            })
            
        retrieval_time_ms = int((time.time() - start_time) * 1000)
        
        return RetrievalResult(
            query=config.query,
            strategy_used=self.name,
            strategy_reasoning="",
            chunks=chunks,
            total_candidates=len(chunks),
            retrieval_time_ms=retrieval_time_ms,
            confidence=1.0
        )
