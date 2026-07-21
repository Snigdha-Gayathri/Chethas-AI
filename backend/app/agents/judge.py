from __future__ import annotations

from typing import Any
from .base import BaseAgent
from app.models.deliberation import JudgeVerdict
from app.llm.provider import get_evaluation_llm
from .prompts.judge import get_judge_prompt

class JudgeAgent(BaseAgent):
    """Judge Agent - scores the investigation and decides if confidence is sufficient."""
    
    def __init__(self):
        super().__init__(
            name="Judge",
            role="Impartial Evaluator",
            expertise="Objective quality assessment, confidence scoring, consensus evaluation, and threshold determination.",
            tools=["citation_verify", "evidence_search"]
        )
    
    def get_system_prompt(self) -> str:
        return get_judge_prompt()
        
    async def _invoke_eval_llm(self, prompt: str, structured_output=None):
        llm = get_evaluation_llm()
        if structured_output:
            llm = llm.with_structured_output(structured_output)
        messages = [
            ("system", self.get_system_prompt()),
            ("human", prompt),
        ]
        return await llm.ainvoke(messages)
    
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("Executing Judge Agent")

        goal = state.get("goal", "")
        findings = state.get("expert_findings", [])
        reflection = state.get("reflection_report") or {}
        verification = state.get("verification_report") or {}
        debate_rounds = state.get("debate_rounds", [])

        state_summary = f"""
Original Goal: {goal}
Number of Findings: {len(findings)}
Debate Rounds Held: {len(debate_rounds)}
Reflection Needs Iteration: {reflection.get('needs_another_iteration', 'Unknown')}
Reflection Quality Score: {reflection.get('quality_score', 'Unknown')}
Evidence Quality: {verification.get('overall_quality', 'Unknown')}
"""

        prompt = f"""
Evaluate the overall quality of the investigation based on the following summary and state context.
{state_summary}

Determine the final verdict, confidence score, and whether another iteration is strictly required.
"""
        verdict: JudgeVerdict = await self._invoke_eval_llm(
            prompt=prompt,
            structured_output=JudgeVerdict
        )

        self.logger.info(
            f"Judge verdict reached. Confidence: {verdict.overall_confidence}, "
            f"Needs iteration: {verdict.needs_iteration}"
        )
        return {
            "judge_verdict": verdict.model_dump(),
            "confidence_score": verdict.overall_confidence
        }
