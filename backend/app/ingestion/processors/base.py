from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel

class ProcessedDocument(BaseModel):
    text_content: str
    sections: list[dict] = []  # Structured sections
    tables: list[dict] = []     # Extracted tables
    images: list[dict] = []     # Image references/captions
    metadata: dict = {}

class BaseProcessor(ABC):
    supported_types: list[str] = []
    
    @abstractmethod
    async def process(self, file_path: str, metadata: dict = None) -> ProcessedDocument:
        pass
