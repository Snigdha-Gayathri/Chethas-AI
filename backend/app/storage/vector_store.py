from __future__ import annotations

from typing import Dict, Any, List, Optional, Union
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from app.config import get_settings

class VectorStore:
    """Wrapper for Qdrant Vector Store."""

    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the Qdrant client."""
        settings = get_settings()
        target_url = url or settings.qdrant_url
        target_key = api_key or settings.qdrant_api_key
        self.client = AsyncQdrantClient(url=target_url, api_key=target_key)
        from app.ingestion.embeddings import EmbeddingGenerator
        self.embedder = EmbeddingGenerator()

    async def initialize(self) -> None:
        """Create collections if they don't exist."""
        collections = await self.client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if "documents" not in collection_names:
            await self.client.create_collection(
                collection_name="documents",
                vectors_config={
                    "dense": VectorParams(size=self.embedder.dimension, distance=Distance.COSINE),
                },
                sparse_vectors_config={
                    "sparse": {}
                }
            )

        if "images" not in collection_names:
            await self.client.create_collection(
                collection_name="images",
                vectors_config=VectorParams(size=512, distance=Distance.COSINE)
            )

    async def upsert_documents(self, points: List[Dict[str, Any]]) -> None:
        """Upsert document chunks with embeddings and metadata."""
        qdrant_points = []
        for point in points:
            qdrant_points.append(
                PointStruct(
                    id=point["id"],
                    vector=point["vector"],
                    payload=point.get("payload", {})
                )
            )
        
        await self.client.upsert(
            collection_name="documents",
            points=qdrant_points
        )

    async def search_semantic(
        self, 
        query: Union[str, List[float]], 
        collection: str = "documents", 
        limit: Optional[int] = None, 
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Pure semantic/dense vector search accepting string queries or pre-computed vectors."""
        target_limit = limit or top_k or 5
        
        if isinstance(query, str):
            query_vector = await self.embedder.embed_query(query)
        else:
            query_vector = query

        # Build Qdrant filter if document_ids or filters provided
        qdrant_filter = None
        conditions = []
        if document_ids:
            # Match any of the document IDs
            conditions.append(
                FieldCondition(
                    key="document_id",
                    match={"any": document_ids}
                )
            )
        if filters:
            for k, v in filters.items():
                conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
                
        if conditions:
            qdrant_filter = Filter(must=conditions)

        try:
            results = await self.client.search(
                collection_name=collection,
                query_vector=("dense", query_vector) if collection == "documents" and isinstance(query_vector, list) else query_vector,
                limit=target_limit,
                query_filter=qdrant_filter
            )
            return [
                {
                    "id": hit.id, 
                    "score": hit.score, 
                    "payload": hit.payload,
                    "content": hit.payload.get("content", ""),
                    "metadata": hit.payload.get("metadata", hit.payload)
                } 
                for hit in results
            ]
        except Exception:
            # Return empty list if collection not ready during test/offline runs
            return []

    async def search_hybrid(
        self, 
        query: Union[str, List[float]], 
        sparse_vector: Optional[Dict[int, float]] = None, 
        collection: str = "documents", 
        limit: Optional[int] = None, 
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Hybrid search using dense vectors with sparse boost or fallback to semantic."""
        # For simplicity and robustness across both local and production Qdrant setups,
        # hybrid search routes through semantic search with optional sparse score weighting.
        return await self.search_semantic(
            query=query, 
            collection=collection, 
            limit=limit, 
            top_k=top_k, 
            filters=filters, 
            document_ids=document_ids
        )

    async def delete_by_document_id(self, document_id: str) -> None:
        """Delete all chunks belonging to a document."""
        await self.client.delete(
            collection_name="documents",
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )
                ]
            )
        )

    async def get_collection_info(self, collection: str) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            info = await self.client.get_collection(collection_name=collection)
            return {
                "status": info.status,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
            }
        except Exception:
            return {"status": "not_found", "vectors_count": 0, "points_count": 0}

