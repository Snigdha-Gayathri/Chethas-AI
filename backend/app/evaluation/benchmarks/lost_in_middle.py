from __future__ import annotations
from app.models.evaluation import BenchmarkResult

class LostInMiddleBenchmark:
    async def run(self) -> BenchmarkResult:
        return BenchmarkResult(
            name="LostInMiddle",
            score=0.0,
            metrics={},
            details="Not implemented"
        )
