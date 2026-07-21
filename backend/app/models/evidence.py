from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid

class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    source: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    citation: str
    modality: str # text/image/table/chart/code/audio/video
    retrieval_strategy: str
    chunk_id: Optional[str] = None
    document_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Citation(BaseModel):
    source: str
    page: Optional[int] = None
    section: Optional[str] = None
    url: Optional[str] = None
    relevance_score: float

class RetrievalResult(BaseModel):
    query: str
    strategy_used: str
    strategy_reasoning: str
    evidence_items: List[Evidence] = Field(default_factory=list)
    total_candidates: int
    retrieval_time_ms: int
