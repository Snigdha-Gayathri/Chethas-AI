from __future__ import annotations
from .base import BaseProcessor, ProcessedDocument

class ImageProcessor(BaseProcessor):
    supported_types = ["image/jpeg", "image/png"]
    
    async def process(self, file_path: str, metadata: dict = None) -> ProcessedDocument:
        metadata = metadata or {}
        # Placeholder for Gemini Vision or similar
        text_content = f"[Image description placeholder for {file_path}]"
        return ProcessedDocument(text_content=text_content, metadata=metadata)
