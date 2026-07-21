from __future__ import annotations
from .base import BaseProcessor, ProcessedDocument
import logging

logger = logging.getLogger(__name__)

class PDFProcessor(BaseProcessor):
    supported_types = ["application/pdf"]
    
    async def process(self, file_path: str, metadata: dict = None) -> ProcessedDocument:
        metadata = metadata or {}
        text_content = ""
        try:
            from unstructured.partition.pdf import partition_pdf
            elements = partition_pdf(filename=file_path)
            text_content = "\n\n".join([str(el) for el in elements])
        except ImportError:
            logger.warning("unstructured not installed. Fallback to basic extraction.")
            # Fallback could use PyPDF2
            pass
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            
        return ProcessedDocument(text_content=text_content, metadata=metadata)
