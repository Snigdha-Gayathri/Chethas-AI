from __future__ import annotations
from .base import BaseProcessor, ProcessedDocument
import logging

logger = logging.getLogger(__name__)

class WebProcessor(BaseProcessor):
    supported_types = ["text/html"]
    
    async def process(self, file_path: str, metadata: dict = None) -> ProcessedDocument:
        metadata = metadata or {}
        text_content = ""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                text_content = soup.get_text(separator="\n", strip=True)
                metadata["title"] = soup.title.string if soup.title else ""
        except ImportError:
            logger.warning("beautifulsoup4 not installed.")
        except Exception as e:
            logger.error(f"Error processing Web/HTML: {e}")
            
        return ProcessedDocument(text_content=text_content, metadata=metadata)
