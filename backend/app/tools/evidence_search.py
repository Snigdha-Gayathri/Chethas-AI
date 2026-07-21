from __future__ import annotations

import json
import logging
from typing import Optional
from langchain_core.tools import tool
from app.context.retrieval import retrieve_evidence

logger = logging.getLogger(__name__)

@tool
async def evidence_search(query: str, strategy_hint: Optional[str] = None, top_k: int = 5) -> str:
    """Search the document vector and hybrid knowledge base for evidence and facts related to a specific sub-query.
    
    Args:
        query: Specific search query string to look for evidence.
        strategy_hint: Optional strategy name ('semantic_rag', 'hybrid_retrieval', 'parent_child', 'graph_retrieval', 'long_context').
        top_k: Number of top evidence items to retrieve (1 to 10).
    Returns:
        JSON string containing retrieved evidence chunks, sources, and confidence scores.
    """
    logger.info(f"Evidence search tool called for query: '{query}' (strategy={strategy_hint})")
    try:
        items = await retrieve_evidence(
            query=query,
            strategy_hint=strategy_hint,
            top_k=top_k
        )
        if not items:
            return json.dumps({"status": "no_evidence_found", "query": query, "items": []})
            
        formatted = []
        for idx, item in enumerate(items):
            formatted.append({
                "citation": item.get("citation", f"[{idx+1}]"),
                "source": item.get("source", "unknown"),
                "confidence": item.get("confidence", 0.0),
                "strategy": item.get("retrieval_strategy", "unknown"),
                "content": item.get("content", "")[:1000] # Cap long chunks for tool context
            })
        return json.dumps({"status": "success", "query": query, "items": formatted}, indent=2)
    except Exception as e:
        logger.error(f"evidence_search tool error: {e}")
        return json.dumps({"status": "error", "message": str(e)})
