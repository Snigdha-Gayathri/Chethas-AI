from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

class DeepEvalEvaluator:
    async def evaluate(self, input_text: str, actual_output: str, retrieval_context: list[str], expected_output: str = None) -> dict:
        """Run DeepEval metrics."""
        try:
            from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
            from deepeval.test_case import LLMTestCase
            
            test_case = LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                retrieval_context=retrieval_context,
                expected_output=expected_output
            )
            
            faithfulness = FaithfulnessMetric(threshold=0.5)
            faithfulness.measure(test_case)
            
            answer_relevancy = AnswerRelevancyMetric(threshold=0.5)
            answer_relevancy.measure(test_case)
            
            return {
                "faithfulness": faithfulness.score,
                "faithfulness_reason": faithfulness.reason,
                "answer_relevancy": answer_relevancy.score,
                "answer_relevancy_reason": answer_relevancy.reason
            }
        except ImportError:
            logger.warning("deepeval not installed.")
            return {}
