from __future__ import annotations
from app.models.evaluation import BenchmarkResult

class ConflictingEvidenceBenchmark:
    async def run(self) -> BenchmarkResult:
        return BenchmarkResult(
            name="ConflictingEvidence",
            score=0.0,
            metrics={},
            details="Not implemented"
        )
