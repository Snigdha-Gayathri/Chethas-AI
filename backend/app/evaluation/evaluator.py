from __future__ import annotations
from app.models.evaluation import EvaluationResult

class Evaluator:
    async def evaluate_execution(self, execution_data: dict) -> EvaluationResult:
        """Run full evaluation suite on an execution."""
        return EvaluationResult(
            score=0.0,
            metrics={},
            details="Not implemented"
        )
    
    async def evaluate_retrieval(self, query: str, retrieved_contexts: list[str], reference: str) -> dict:
        """Evaluate retrieval quality independently."""
        return {"retrieval_score": 0.0}
