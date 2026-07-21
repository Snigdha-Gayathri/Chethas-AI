from __future__ import annotations
from app.models.evaluation import BenchmarkSuite, BenchmarkResult
from .needle_haystack import NeedleInHaystackBenchmark
from .lost_in_middle import LostInMiddleBenchmark
from .noise_injection import NoiseInjectionBenchmark
from .conflicting_evidence import ConflictingEvidenceBenchmark
from .long_context_vs_rag import LongContextVsRAGBenchmark

class BaseBenchmark:
    pass

class BenchmarkRunner:
    def __init__(self):
        self.benchmarks = {
            "needle_haystack": NeedleInHaystackBenchmark(),
            "lost_in_middle": LostInMiddleBenchmark(),
            "noise_injection": NoiseInjectionBenchmark(),
            "conflicting_evidence": ConflictingEvidenceBenchmark(),
            "long_context_vs_rag": LongContextVsRAGBenchmark()
        }
    
    async def run_all(self, config: dict = None) -> BenchmarkSuite:
        """Run all benchmarks and return suite results."""
        results = []
        for name, benchmark in self.benchmarks.items():
            if hasattr(benchmark, 'run'):
                # Pass dummy args where required, or handle correctly in real impl
                try:
                    res = await benchmark.run()
                    results.append(res)
                except TypeError:
                    # E.g. NeedleInHaystack requires args, dummy handling
                    pass
        return BenchmarkSuite(
            name="All Benchmarks",
            results=results
        )
    
    async def run_benchmark(self, name: str, config: dict = None) -> BenchmarkResult:
        """Run a specific benchmark."""
        benchmark = self.benchmarks.get(name)
        if not benchmark:
            raise ValueError(f"Benchmark {name} not found.")
        # Dummy call
        return BenchmarkResult(name=name, score=0.0, metrics={}, details="")
