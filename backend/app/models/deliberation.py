from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from .evidence import Citation

class DebateArgument(BaseModel):
    agent_name: str
    position: str
    evidence_refs: List[str] = Field(default_factory=list) # evidence ids
    confidence: float = Field(..., ge=0.0, le=1.0)
    round_number: int

class DebateChallenge(BaseModel):
    challenger: str
    challenged_agent: str
    challenged_claim: str
    counter_argument: str
    supporting_evidence: List[str] = Field(default_factory=list)

class DebateDefense(BaseModel):
    defender: str
    original_claim: str
    defense_argument: str
    additional_evidence: List[str] = Field(default_factory=list)
    revised_confidence: float

class DebateRevision(BaseModel):
    agent_name: str
    original_position: str
    revised_position: str
    reason: str
    confidence_change: float

class DeliberationRound(BaseModel):
    round_number: int
    arguments: List[DebateArgument] = Field(default_factory=list)
    challenges: List[DebateChallenge] = Field(default_factory=list)
    defenses: List[DebateDefense] = Field(default_factory=list)
    revisions: List[DebateRevision] = Field(default_factory=list)
    convergence_score: float = Field(..., ge=0.0, le=1.0)

class ReflectionReport(BaseModel):
    identified_weaknesses: List[str] = Field(default_factory=list)
    hallucination_risks: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    evidence_gaps: List[str] = Field(default_factory=list)
    suggested_improvements: List[str] = Field(default_factory=list)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    needs_another_iteration: bool

class JudgeVerdict(BaseModel):
    evidence_quality_score: float
    reasoning_quality_score: float
    factual_consistency_score: float
    citation_quality_score: float
    overall_confidence: float
    inter_agent_agreement: float
    consensus_view: str
    minority_opinions: List[str] = Field(default_factory=list)
    winning_conclusion: str
    winning_explanation: str
    needs_iteration: bool

class ConsensusReport(BaseModel):
    executive_summary: str
    detailed_analysis: str
    key_findings: List[str] = Field(default_factory=list)
    evidence_citations: List[Citation] = Field(default_factory=list)
    confidence_level: float
    confidence_label: str
    minority_dissents: List[str] = Field(default_factory=list)
    methodology_explanation: str
    iteration_count: int
    total_agents: int
    domain: str
