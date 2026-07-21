from __future__ import annotations

import logging
from typing import Any
from app.context.models import RetrievalConfig, RetrievalResult
from app.context.strategy_router import StrategyRouter
from app.models.evidence import Evidence

logger = logging.getLogger(__name__)

async def retrieve_evidence(
    query: str,
    document_ids: list[str] | None = None,
    strategy_hint: str | None = None,
    top_k: int = 5,
    token_budget: int = 4000
) -> list[dict[str, Any]]:
    """High-level evidence retrieval function used by agents and tools."""
    if not query or not query.strip():
        return []

    router = StrategyRouter()
    config = RetrievalConfig(
        query=query,
        document_ids=document_ids or [],
        top_k=top_k,
        token_budget=token_budget,
        strategy_override=strategy_hint if strategy_hint in router.STRATEGIES else None
    )

    try:
        result: RetrievalResult = await router.retrieve(config)
        evidence_items = []
        for i, chunk in enumerate(result.chunks):
            metadata = chunk.get("metadata", {})
            source_name = metadata.get("source", metadata.get("filename", f"Chunk_{i+1}"))
            
            ev = Evidence(
                content=chunk.get("content", ""),
                source=str(source_name),
                confidence=float(chunk.get("score", result.confidence or 0.8)),
                citation=f"[{i+1}] {source_name}",
                modality=metadata.get("modality", "text"),
                retrieval_strategy=result.strategy_used,
                chunk_id=metadata.get("chunk_id", str(i)),
                document_id=metadata.get("document_id", ""),
                metadata=metadata
            )
            evidence_items.append(ev.model_dump())
            
        return evidence_items
    except Exception as e:
        logger.error(f"retrieve_evidence failed for query '{query}': {e}")
        return []
