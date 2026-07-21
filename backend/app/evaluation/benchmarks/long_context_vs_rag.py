from __future__ import annotations
from app.models.evaluation import BenchmarkResult

class LongContextVsRAGBenchmark:
    async def run(self) -> BenchmarkResult:
        return BenchmarkResult(
            name="LongContextVsRAG",
            score=0.0,
            metrics={},
            details="Not implemented"
        )
