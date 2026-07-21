from __future__ import annotations

import json
import logging
from typing import Optional
from langchain_core.tools import tool
from app.storage.graph_store import GraphStore

logger = logging.getLogger(__name__)

@tool
async def graph_query(cypher_or_entity: str, query_type: str = "search_entity", depth: int = 1) -> str:
    """Explore the Neo4j knowledge graph for multi-hop relationships, entity neighbors, or execute read-only Cypher queries.
    
    Args:
        cypher_or_entity: Entity name/text string to search, OR a read-only Cypher query if query_type is 'cypher'.
        query_type: One of 'search_entity', 'neighbors', or 'cypher' (default 'search_entity').
        depth: Graph depth when checking neighbors (default 1, max 3).
    Returns:
        JSON string with matched nodes, relationships, or Cypher result records.
    """
    logger.info(f"Graph query tool called: type={query_type}, query='{cypher_or_entity}'")
    store = GraphStore()
    try:
        if query_type == "cypher":
            # Ensure safe read-only Cypher
            if any(cmd in cypher_or_entity.upper() for cmd in ["CREATE", "MERGE", "DELETE", "SET", "REMOVE", "DROP"]):
                return json.dumps({"status": "error", "message": "Only read-only Cypher (MATCH/RETURN) allowed in graph_query tool."})
            records = await store.query(cypher_or_entity)
            return json.dumps({"status": "success", "query_type": "cypher", "records": records[:20]}, indent=2)
            
        elif query_type == "neighbors":
            # First find matching entity
            entities = await store.search_entities(cypher_or_entity)
            if not entities:
                return json.dumps({"status": "no_entity_found", "query": cypher_or_entity, "neighbors": []})
            entity_id = entities[0].get("id")
            if not entity_id:
                return json.dumps({"status": "error", "message": "Matched entity has no ID property."})
            neighbors_data = await store.get_neighbors(entity_id, depth=min(depth, 3))
            return json.dumps({"status": "success", "query_type": "neighbors", "data": neighbors_data}, indent=2)
            
        else:
            # Default: search_entity
            entities = await store.search_entities(cypher_or_entity)
            return json.dumps({"status": "success", "query_type": "search_entity", "entities": entities[:10]}, indent=2)
    except Exception as e:
        logger.error(f"graph_query tool error: {e}")
        return json.dumps({"status": "error", "message": str(e)})
    finally:
        await store.close()
