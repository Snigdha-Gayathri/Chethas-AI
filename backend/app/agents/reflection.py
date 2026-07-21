from __future__ import annotations

from typing import Any
from .base import BaseAgent
from app.models.deliberation import ReflectionReport
from .prompts.reflection import get_reflection_prompt

class ReflectionAgent(BaseAgent):
    """Reflection Agent - analyzes outcomes, spots gaps, and determines if iteration is needed."""
    
    def __init__(self):
        super().__init__(
            name="Reflection",
            role="Critical Reflector",
            expertise="Meta-analysis, logic gap detection, contradiction resolution, and iterative improvement planning.",
            tools=["evidence_search", "shared_blackboard_read"]
        )
    
    def get_system_prompt(self) -> str:
        return get_reflection_prompt()
    
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("Executing Reflection Agent")
        
        goal = state.get("goal", "")
        findings = state.get("expert_findings", [])
        verification_report = state.get("verification_report")

        findings_summary = "\n".join([str(f) for f in findings]) or "No findings available."
        verification_summary = str(verification_report) if verification_report else "No verification data."
        
        prompt = f"""
Original Goal: {goal}

Expert Findings:
{findings_summary}

Evidence Verification Report:
{verification_summary}

Please reflect on these inputs, identify any gaps or contradictions, and determine if another iteration is required.
"""
        report: ReflectionReport = await self._invoke_llm(
            prompt=prompt,
            structured_output=ReflectionReport
        )
        
        self.logger.info(f"Reflection completed. Needs iteration: {report.needs_another_iteration}")
        return {"reflection_report": report.model_dump()}
