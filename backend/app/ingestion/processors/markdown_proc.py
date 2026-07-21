from __future__ import annotations
from .base import BaseProcessor, ProcessedDocument
import os

class MarkdownProcessor(BaseProcessor):
    supported_types = ["text/markdown"]
    
    async def process(self, file_path: str, metadata: dict = None) -> ProcessedDocument:
        metadata = metadata or {}
        text_content = ""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
                
        return ProcessedDocument(text_content=text_content, metadata=metadata)
