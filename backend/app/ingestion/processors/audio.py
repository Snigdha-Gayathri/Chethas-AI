from __future__ import annotations
from .base import BaseProcessor, ProcessedDocument
import os

class AudioProcessor(BaseProcessor):
    supported_types = ["audio/mpeg", "audio/wav"]
    
    async def process(self, file_path: str, metadata: dict = None) -> ProcessedDocument:
        metadata = metadata or {}
        # Placeholder for Whisper API integration
        text_content = "[Audio transcription not implemented. Need Whisper API]"
        return ProcessedDocument(text_content=text_content, metadata=metadata)
