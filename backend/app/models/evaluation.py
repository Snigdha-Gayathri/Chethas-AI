from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

class EvaluationMetric(BaseModel):
    name: str
    score: float
    details: Optional[str] = None

class EvaluationResult(BaseModel):
    execution_id: str
    faithfulness: Optional[float] = None
    answer_relevancy: Optional[float] = None
    context_precision: Optional[float] = None
    context_recall: Optional[float] = None
    hallucination_rate: Optional[float] = None
    latency_ms: Optional[int] = None
    token_cost: Optional[float] = None
    retrieval_quality: Optional[float] = None
    provider: str # ragas/deepeval
    metrics: List[EvaluationMetric] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BenchmarkResult(BaseModel):
    benchmark_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    scores: Dict[str, float] = Field(default_factory=dict)
    raw_results: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BenchmarkSuite(BaseModel):
    name: str
    description: str
    benchmarks: List[BenchmarkResult] = Field(default_factory=list)
    overall_score: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
