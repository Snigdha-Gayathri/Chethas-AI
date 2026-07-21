from __future__ import annotations
from app.models.evaluation import BenchmarkResult

class NeedleInHaystackBenchmark:
    async def run(self, needle: str, haystack_sizes: list[int], depths: list[float], llm=None) -> BenchmarkResult:
        """Run NIAH across depth x context size matrix."""
        return BenchmarkResult(
            name="NeedleInHaystack",
            score=0.0,
            metrics={"sizes": haystack_sizes, "depths": depths},
            details="Not implemented"
        )
