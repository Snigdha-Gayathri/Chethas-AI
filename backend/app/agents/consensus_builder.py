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
            tools=[]
        )
    
    def get_system_prompt(self) -> str:
        return get_consensus_prompt()
    
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("Executing Consensus Builder Agent")

        goal = state.get("goal", "")
        findings = state.get("expert_findings", [])
        verdict = state.get("judge_verdict") or {}
        roles = state.get("generated_roles", [])

        MAX_CHARS = 1200
        findings_parts = []
        for f in findings:
            text = f.get("detailed_analysis") or f.get("finding_summary") or ""
            if len(text) > MAX_CHARS:
                text = text[:MAX_CHARS] + "..."
            findings_parts.append(f"- {text}")
        findings_summary = "\n".join(findings_parts) or "(no findings)"

        roles_summary = ", ".join([r.get("name", "") for r in roles]) or "(no roles)"

        verdict_summary = ""
        if verdict:
            verdict_summary = (
                f"Confidence: {verdict.get('overall_confidence', 'n/a')}. "
                f"Conclusion: {verdict.get('winning_conclusion', '')}"
            )
        else:
            verdict_summary = "No verdict available."

        prompt = f"""Original Goal: {goal}

Participating Roles: {roles_summary}

Expert Findings:
{findings_summary}

Judge Verdict: {verdict_summary}

Synthesize this into a polished, comprehensive final consensus report.
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
