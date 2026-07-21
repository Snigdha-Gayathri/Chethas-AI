from __future__ import annotations
from .base import BaseProcessor, ProcessedDocument
from .pdf import PDFProcessor
from .markdown_proc import MarkdownProcessor
from .web import WebProcessor
from .code import CodeProcessor
from .presentation import PresentationProcessor
from .audio import AudioProcessor
from .image import ImageProcessor

__all__ = [
    "BaseProcessor", "ProcessedDocument", "PDFProcessor", "MarkdownProcessor",
    "WebProcessor", "CodeProcessor", "PresentationProcessor", "AudioProcessor", "ImageProcessor"
]
