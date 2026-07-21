from __future__ import annotations
from functools import lru_cache
from app.config import Settings, get_settings
from app.storage.vector_store import VectorStore
from app.storage.graph_store import GraphStore
from app.storage.state_store import StateStore

@lru_cache()
def get_vector_store() -> VectorStore:
    """Returns a cached instance of the VectorStore."""
    settings = get_settings()
    return VectorStore(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

@lru_cache()
def get_graph_store() -> GraphStore:
    """Returns a cached instance of the GraphStore."""
    settings = get_settings()
    return GraphStore(uri=settings.neo4j_uri, user=settings.neo4j_user, password=settings.neo4j_password)

@lru_cache()
def get_state_store() -> StateStore:
    """Returns a cached instance of the StateStore."""
    settings = get_settings()
    return StateStore(database_url=settings.database_url)
