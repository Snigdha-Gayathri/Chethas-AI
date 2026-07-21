from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import hashlib
from app.config import get_settings

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, provider: str | None = None, model: str | None = None):
        settings = get_settings()
        self.provider = provider or settings.embedding_provider or "fastembed"
        self.model = model or settings.embedding_model or "BAAI/bge-small-en-v1.5"
        self._model_instance = None
        self._executor = ThreadPoolExecutor()
        
        if self.provider == "fastembed":
            try:
                from fastembed import TextEmbedding
                self._model_instance = TextEmbedding(model_name=self.model)
            except Exception as e:
                logger.warning(f"fastembed not available ({e}). Using deterministic fallback embeddings.")
        elif self.provider == "google":
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                self._model_instance = GoogleGenerativeAIEmbeddings(model=self.model)
            except Exception as e:
                logger.warning(f"langchain-google-genai not available ({e}). Using deterministic fallback embeddings.")
                
    def _fallback_embedding(self, text: str) -> list[float]:
        """Generate a deterministic fallback vector based on text hash when external models are unavailable."""
        dim = self.dimension
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vector = []
        for i in range(dim):
            val = (h[i % len(h)] - 128) / 128.0
            vector.append(val)
        # Normalize to unit vector
        norm = sum(v * v for v in vector) ** 0.5
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return []
        if not self._model_instance:
            return [self._fallback_embedding(t) for t in texts]
            
        loop = asyncio.get_running_loop()
        try:
            if self.provider == "fastembed":
                embeddings_generator = await loop.run_in_executor(
                    self._executor, 
                    lambda: list(self._model_instance.embed(texts))
                )
                return [emb.tolist() for emb in embeddings_generator]
            elif self.provider == "google":
                return await loop.run_in_executor(
                    self._executor,
                    self._model_instance.embed_documents,
                    texts
                )
        except Exception as e:
            logger.error(f"Embedding batch generation failed ({e}). Using fallback.")
        return [self._fallback_embedding(t) for t in texts]

    async def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single query."""
        if not query:
            return [0.0] * self.dimension
        if not self._model_instance:
            return self._fallback_embedding(query)
            
        loop = asyncio.get_running_loop()
        try:
            if self.provider == "fastembed":
                embeddings_generator = await loop.run_in_executor(
                    self._executor, 
                    lambda: list(self._model_instance.embed([query]))
                )
                return [emb.tolist() for emb in embeddings_generator][0]
            elif self.provider == "google":
                return await loop.run_in_executor(
                    self._executor,
                    self._model_instance.embed_query,
                    query
                )
        except Exception as e:
            logger.error(f"Embedding query generation failed ({e}). Using fallback.")
        return self._fallback_embedding(query)

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        if self.provider == "fastembed" and "small" in self.model:
            return 384
        return 768

