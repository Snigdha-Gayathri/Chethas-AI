from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

class RagasEvaluator:
    async def evaluate(self, questions: list[str], answers: list[str], contexts: list[list[str]], ground_truths: list[str] = None) -> dict:
        """Run RAGAS evaluation."""
        try:
            import ragas
            from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
            from datasets import Dataset
            
            data = {
                "question": questions,
                "answer": answers,
                "contexts": contexts,
                "ground_truth": ground_truths or [""] * len(questions)
            }
            dataset = Dataset.from_dict(data)
            
            result = ragas.evaluate(
                dataset,
                metrics=[faithfulness, answer_relevancy, context_precision, context_recall]
            )
            return result
        except ImportError:
            logger.warning("ragas not installed.")
            return {}
