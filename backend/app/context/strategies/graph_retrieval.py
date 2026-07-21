from __future__ import annotations
import time
from typing import Any
from .base import BaseStrategy
from ..models import RetrievalConfig, RetrievalResult
from app.storage.graph_store import GraphStore
from app.llm.provider import get_llm

class GraphRetrievalStrategy(BaseStrategy):
    name = "graph_retrieval"
    description = "Neo4j graph-based retrieval for multi-hop relationship-heavy data."
    
    def __init__(self):
        self.graph_store = GraphStore()
        self.llm = get_llm()
        
    async def retrieve(self, config: RetrievalConfig) -> RetrievalResult:
        start_time = time.time()
        
        prompt = f"""Convert the following question into a Cypher query for a Neo4j database.
Question: "{config.query}"
Only output the Cypher query text, without markdown blocks.
"""
        try:
            response = await self.llm.ainvoke(prompt)
            cypher_query = response.content if hasattr(response, 'content') else str(response)
            cypher_query = cypher_query.strip().replace("```cypher", "").replace("```", "").strip()
            
            graph_results = await self.graph_store.query(cypher_query)
            
            entities = await self.graph_store.search_entities(config.query)
            if not graph_results and entities:
                for entity in entities:
                    neighbors = await self.graph_store.get_neighbors(entity.get("id"))
                    graph_results.extend(neighbors)
        except Exception as e:
            graph_results = []
            
        chunks = []
        for res in graph_results[:config.top_k]:
            chunks.append({
                "content": str(res),
                "metadata": {"source": "graph"},
                "score": 0.8
            })
            
        retrieval_time_ms = int((time.time() - start_time) * 1000)
        
        return RetrievalResult(
            query=config.query,
            strategy_used=self.name,
            strategy_reasoning="",
            chunks=chunks,
            total_candidates=len(chunks),
            retrieval_time_ms=retrieval_time_ms,
            confidence=0.8 if chunks else 0.0
        )
