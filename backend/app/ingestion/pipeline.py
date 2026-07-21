from __future__ import annotations
import mimetypes
from typing import Any
from app.storage.vector_store import VectorStore
from app.storage.graph_store import GraphStore
from .chunking import AdaptiveChunker
from .embeddings import EmbeddingGenerator
from .processors.base import BaseProcessor
from .processors.pdf import PDFProcessor
from .processors.markdown_proc import MarkdownProcessor
from .processors.web import WebProcessor
from .processors.code import CodeProcessor
from .processors.presentation import PresentationProcessor
from .processors.audio import AudioProcessor
from .processors.image import ImageProcessor

class IngestionPipeline:
    def __init__(self, vector_store: VectorStore, graph_store: GraphStore):
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.chunker = AdaptiveChunker()
        self.embedder = EmbeddingGenerator()
        
        self.processors: dict[str, BaseProcessor] = {
            "application/pdf": PDFProcessor(),
            "text/markdown": MarkdownProcessor(),
            "text/html": WebProcessor(),
            "text/x-python": CodeProcessor(),
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": PresentationProcessor(),
            "audio/mpeg": AudioProcessor(),
            "image/jpeg": ImageProcessor(),
            "image/png": ImageProcessor(),
        }
    
    async def ingest_document(self, file_path: str, filename: str, content_type: str, metadata: dict = None) -> dict:
        """Process a single document through the full pipeline."""
        metadata = metadata or {}
        metadata["filename"] = filename
        metadata["content_type"] = content_type
        
        processor = self._detect_processor(content_type)
        if not processor:
            return {"status": "error", "message": f"No processor for {content_type}"}
            
        processed_doc = await processor.process(file_path, metadata)
        
        chunks = self.chunker.chunk_text(processed_doc.text_content, metadata=processed_doc.metadata)
        
        if not chunks:
            return {"status": "success", "chunk_count": 0}
            
        texts = [c["content"] for c in chunks]
        embeddings = await self.embedder.embed_texts(texts)
        
        documents_to_upsert = []
        import uuid
        document_id = str(uuid.uuid4())
        
        for i, chunk in enumerate(chunks):
            doc = {
                "id": chunk.get("metadata", {}).get("chunk_id", str(uuid.uuid4())),
                "document_id": document_id,
                "content": chunk["content"],
                "metadata": chunk["metadata"],
                "embedding": embeddings[i] if i < len(embeddings) else None
            }
            documents_to_upsert.append(doc)
            
        await self.vector_store.upsert_documents("default", documents_to_upsert)
        
        return {"document_id": document_id, "chunk_count": len(chunks), "status": "success"}
    
    async def ingest_batch(self, documents: list[dict]) -> list[dict]:
        """Process multiple documents."""
        results = []
        for doc in documents:
            res = await self.ingest_document(
                file_path=doc.get("file_path"),
                filename=doc.get("filename"),
                content_type=doc.get("content_type"),
                metadata=doc.get("metadata")
            )
            results.append(res)
        return results
    
    def _detect_processor(self, content_type: str) -> BaseProcessor:
        """Map MIME type to processor."""
        return self.processors.get(content_type)
