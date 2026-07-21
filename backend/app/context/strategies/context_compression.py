from __future__ import annotations
from typing import Any
from app.llm.provider import get_llm

class ContextCompressor:
    def __init__(self):
        self.llm = get_llm()
        
    async def rerank(self, query: str, chunks: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        """Rerank chunks using LLM scoring."""
        if not chunks:
            return []
            
        if len(chunks) > 20:
            return sorted(chunks, key=lambda x: x.get("score", 0.0), reverse=True)[:top_k]
            
        scored_chunks = []
        for chunk in chunks:
            prompt = f"""Score the relevance of this chunk to the query on a scale of 0.0 to 1.0.
Query: "{query}"
Chunk: "{chunk.get('content')}"
Only output the float number."""
            try:
                score_str = await self.llm.ainvoke(prompt)
                score = float(score_str.strip())
                chunk["rerank_score"] = score
                scored_chunks.append(chunk)
            except Exception:
                chunk["rerank_score"] = chunk.get("score", 0.0)
                scored_chunks.append(chunk)
                
        return sorted(scored_chunks, key=lambda x: x.get("rerank_score", 0.0), reverse=True)[:top_k]

    async def summarize_chunks(self, chunks: list[dict[str, Any]], max_tokens: int = 2000) -> list[dict[str, Any]]:
        """Summarize chunks to fit within a token budget."""
        summarized = []
        for chunk in chunks:
            prompt = f"""Summarize the following text while retaining key facts and entities.
Text: "{chunk.get('content')}"
Summary:"""
            try:
                summary = await self.llm.ainvoke(prompt)
                summarized_chunk = chunk.copy()
                summarized_chunk["content"] = summary.strip()
                summarized.append(summarized_chunk)
            except Exception:
                summarized.append(chunk)
        return summarized
