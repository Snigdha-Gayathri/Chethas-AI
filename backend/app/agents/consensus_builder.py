from __future__ import annotations

from typing import Any
from .base import BaseAgent
from app.models.deliberation import ConsensusReport
from .prompts.consensus import get_consensus_prompt

class ConsensusBuilderAgent(BaseAgent):
    """Consensus Builder Agent - synthesizes final output for the user."""
    
    def __init__(self):
        super().__init__(
            name="ConsensusBuilder",
            role="Synthesis Expert",
            expertise="Report writing, information synthesis, executive summarization, and consensus articulation.",
            tools=["shared_blackboard_read"]
        )
    
    def get_system_prompt(self) -> str:
        return get_consensus_prompt()
    
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("Executing Consensus Builder Agent")
        
        goal = state.get("goal", "")
        findings = state.get("expert_findings", [])
        verdict = state.get("judge_verdict") or {}
        roles = state.get("generated_roles", [])

        findings_summary = "\n".join([
            f"Finding: {f.get('detailed_analysis', f.get('finding_summary', ''))}"
            for f in findings
        ])
        roles_summary = ", ".join([r.get("name", "") for r in roles])
        verdict_summary = str(verdict) if verdict else "No verdict available."
        
        prompt = f"""
Original Goal: {goal}

Participating Roles: {roles_summary}

Expert Findings:
{findings_summary}

Judge Verdict:
{verdict_summary}

Please synthesize all of this information into a polished, comprehensive final consensus report.
"""
        report: ConsensusReport = await self._invoke_llm(
            prompt=prompt,
            structured_output=ConsensusReport
        )
        
        self.logger.info("Consensus report generated successfully.")
        return {
            "consensus": report.model_dump(),
            "final_output": report.model_dump()
        }
