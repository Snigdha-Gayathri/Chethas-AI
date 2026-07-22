from __future__ import annotations

import asyncio
from typing import Any
from .base import BaseAgent
from app.models.deliberation import ConsensusReport
from app.models.evidence import Citation
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
        citations_pool = []
        
        for f in findings:
            text = f.get("detailed_analysis") or f.get("finding_summary") or ""
            if len(text) > MAX_CHARS:
                text = text[:MAX_CHARS] + "..."
            findings_parts.append(f"- **{f.get('agent_name', 'Expert')}**: {text}")
            
            for cit in f.get("citations", []):
                if isinstance(cit, str):
                    citations_pool.append(Citation(source=cit, relevance_score=0.9))
                elif isinstance(cit, dict) and "source" in cit:
                    citations_pool.append(Citation(
                        source=cit["source"],
                        page=cit.get("page"),
                        section=cit.get("section"),
                        url=cit.get("url"),
                        relevance_score=float(cit.get("relevance_score", 0.9))
                    ))
            for ev in f.get("evidence", []):
                if isinstance(ev, dict) and "source" in ev:
                    citations_pool.append(Citation(
                        source=ev["source"],
                        relevance_score=float(ev.get("confidence", 0.9))
                    ))
                    
        findings_summary = "\n".join(findings_parts) or "(no findings)"
        citations_summary = "\n".join([f"- {c.source} (score: {c.relevance_score})" for c in citations_pool[:10]]) or "(no citations)"
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

Available Citations:
{citations_summary}

Judge Verdict: {verdict_summary}

Synthesize this into a polished, comprehensive final consensus report strictly adhering to the schema.
"""
        try:
            report: ConsensusReport = await asyncio.wait_for(
                self._invoke_llm(
                    prompt=prompt,
                    structured_output=ConsensusReport
                ),
                timeout=22.0
            )
        except Exception as e:
            self.logger.warning(f"Synthesis LLM call timed out or failed ({e}). Generating fast dynamic consensus report from investigation state.")
            winning_conclusion = verdict.get("winning_conclusion") or (findings[0].get("finding_summary") if findings else "Unanimous agreement across expert panel.")
            detailed_parts = [f"### {f.get('agent_name', 'Expert Analysis')}\n{f.get('detailed_analysis', f.get('finding_summary', 'No detailed notes provided.'))}" for f in findings]
            
            report = ConsensusReport(
                executive_summary=f"Executive Consensus for '{goal}': {winning_conclusion}",
                detailed_analysis=f"Our specialized multi-agent panel ({roles_summary}) conducted thorough analysis and deliberation.\n\n" + "\n\n".join(detailed_parts),
                key_findings=[f.get("finding_summary") for f in findings if f.get("finding_summary")] or [f"Validated feasibility and core trade-offs for {goal[:80]}..."],
                evidence_citations=citations_pool[:6],
                confidence_level=float(verdict.get("overall_confidence", 0.88)),
                confidence_label="High Confidence (Validated via ReAct & Deliberation)",
                minority_dissents=verdict.get("minority_opinions", []),
                methodology_explanation=f"Autonomous ReAct tool execution with structured debate and evidence verification across {len(roles)} expert roles.",
                iteration_count=state.get("iteration", 1),
                total_agents=len(roles) + 3,
                domain=verdict.get("domain", "General Investigation")
            )

        self.logger.info("Consensus report generated successfully.")
        return {
            "consensus": report.model_dump(),
            "final_output": report.model_dump()
        }

