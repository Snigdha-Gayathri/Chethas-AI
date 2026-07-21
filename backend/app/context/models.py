from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any

class RetrievalConfig(BaseModel):
    query: str
    document_ids: list[str] = Field(default_factory=list)
    top_k: int = 5
    token_budget: int = 4000
    min_confidence: float = 0.5
    strategy_override: str | None = None

class StrategyDecision(BaseModel):
    selected_strategy: str
    reasoning: str
    alternatives_considered: list[str] = Field(default_factory=list)
    confidence: float
    decision_factors: dict[str, Any] = Field(default_factory=dict)

class RetrievalResult(BaseModel):
    query: str
    strategy_used: str
    strategy_reasoning: str
    chunks: list[dict[str, Any]]
    total_candidates: int
    retrieval_time_ms: int
    confidence: float
