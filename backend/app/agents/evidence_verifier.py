from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from .base import BaseAgent
from .prompts.evidence_verifier import get_evidence_verifier_prompt

class EvidenceReportItem(BaseModel):
    finding_id: str = Field(..., description="ID or summary of the finding being verified")
    is_supported: bool = Field(..., description="Whether the finding is adequately supported by evidence")
    flags: list[str] = Field(default_factory=list, description="Any potential issues, hallucinations, or missing citations")
    quality_score: float = Field(..., description="Quality score of the evidence from 0.0 to 1.0")

class VerificationReport(BaseModel):
    items: list[EvidenceReportItem] = Field(..., description="Verification results for all findings")
    overall_quality: float = Field(..., description="Average evidence quality across all findings")

class EvidenceVerifierAgent(BaseAgent):
    """Evidence Verifier Agent - validates claims and evidence from expert findings."""
    
    def __init__(self):
        super().__init__(
            name="EvidenceVerifier",
            role="Evidence Verifier",
            expertise="Fact-checking, citation validation, hallucination detection, and source credibility assessment.",
            tools=["citation_verify", "evidence_search"]
        )
    
    def get_system_prompt(self) -> str:
        return get_evidence_verifier_prompt()
    
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("Executing Evidence Verifier Agent")

        findings: list[dict] = state.get("expert_findings", [])
        if not findings:
            self.logger.warning("No findings to verify.")
            return {"verification_report": None}

        findings_text = "\n\n".join([
            f"Finding by {f.get('agent_name', 'unknown')} (Confidence: {f.get('confidence', 0.0)}):\n"
            f"{f.get('detailed_analysis', f.get('finding_summary', ''))}\n"
            f"Citations: {f.get('citations', [])}"
            for f in findings
        ])

        prompt = f"""
Please verify the following expert findings:

{findings_text}
"""
        report: VerificationReport = await self._invoke_llm(
            prompt=prompt,
            structured_output=VerificationReport
        )

        self.logger.info(f"Verification completed. Overall quality: {report.overall_quality}")
        return {"verification_report": report.model_dump()}
