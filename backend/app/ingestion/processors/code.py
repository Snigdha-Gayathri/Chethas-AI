from __future__ import annotations
from .base import BaseProcessor, ProcessedDocument
import os

class CodeProcessor(BaseProcessor):
    supported_types = ["text/x-python", "text/javascript", "text/x-java"]
    
    async def process(self, file_path: str, metadata: dict = None) -> ProcessedDocument:
        metadata = metadata or {}
        text_content = ""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                text_content = f.read()
                
        metadata["language"] = os.path.splitext(file_path)[1].replace(".", "")
        return ProcessedDocument(text_content=text_content, metadata=metadata)
