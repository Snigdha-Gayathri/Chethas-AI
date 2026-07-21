from __future__ import annotations

import json
import logging
from langchain_core.tools import tool
from app.context.strategies.query_rewriter import QueryRewriter

logger = logging.getLogger(__name__)

@tool
async def query_rewrite(query: str, mode: str = "decompose") -> str:
    """Rewrite or decompose an ambiguous or complex query before retrieving knowledge.
    
    Args:
        query: The complex or ambiguous query string to optimize.
        mode: One of 'decompose' (break into sub-queries), 'hyde' (generate hypothetical answer passage to search by), or 'standalone'.
    Returns:
        JSON string with rewritten query strings.
    """
    logger.info(f"query_rewrite tool called: mode={mode}, query='{query}'")
    rewriter = QueryRewriter()
    try:
        if mode == "hyde":
            hyde_ans = await rewriter.hyde(query)
            return json.dumps({"status": "success", "mode": "hyde", "original": query, "hyde_passage": hyde_ans}, indent=2)
        elif mode == "standalone":
            # For standalone without full history provided, rephrase for clarity
            st = await rewriter.standalone(query, history=[])
            return json.dumps({"status": "success", "mode": "standalone", "original": query, "rewritten": st}, indent=2)
        else:
            # Default: decompose
            sub_queries = await rewriter.decompose(query)
            return json.dumps({"status": "success", "mode": "decompose", "original": query, "sub_queries": sub_queries}, indent=2)
    except Exception as e:
        logger.error(f"query_rewrite tool error: {e}")
        return json.dumps({"status": "error", "message": str(e)})
