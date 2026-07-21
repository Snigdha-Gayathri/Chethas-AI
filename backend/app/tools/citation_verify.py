from __future__ import annotations

import json
import logging
from langchain_core.tools import tool
from app.context.retrieval import retrieve_evidence

logger = logging.getLogger(__name__)

@tool
async def citation_verify(claim_text: str, cited_source_or_query: str) -> str:
    """Verify whether a specific claim or statement is directly supported by cited knowledge chunks.
    
    Args:
        claim_text: The exact claim, figure, or factual statement to verify.
        cited_source_or_query: The cited source name or targeted keywords from the citation.
    Returns:
        JSON string containing support status ('SUPPORTED', 'CONTRADICTED', 'UNVERIFIED'), confidence score, and matching evidence snippets.
    """
    logger.info(f"citation_verify tool called: claim='{claim_text[:80]}...', source='{cited_source_or_query}'")
    try:
        # Search for evidence combining the claim keywords and cited source
        search_q = f"{claim_text} {cited_source_or_query}"
        items = await retrieve_evidence(query=search_q, top_k=3)
        if not items:
            return json.dumps({
                "status": "UNVERIFIED",
                "reason": "No matching knowledge chunks retrieved for the cited source or keywords.",
                "claim": claim_text,
                "matches": []
            }, indent=2)
            
        matches = []
        highest_score = 0.0
        for item in items:
            score = item.get("confidence", 0.0)
            if score > highest_score:
                highest_score = score
            matches.append({
                "source": item.get("source", "unknown"),
                "confidence": score,
                "snippet": item.get("content", "")[:500]
            })
            
        verdict = "SUPPORTED" if highest_score >= 0.7 else "UNVERIFIED"
        return json.dumps({
            "status": verdict,
            "confidence": highest_score,
            "claim": claim_text,
            "matches": matches
        }, indent=2)
    except Exception as e:
        logger.error(f"citation_verify tool error: {e}")
        return json.dumps({"status": "ERROR", "message": str(e)})
