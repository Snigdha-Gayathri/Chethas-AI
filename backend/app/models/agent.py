from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid

class AgentRole(BaseModel):
    name: str
    expertise: str
    description: str
    assigned_subtasks: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    system_prompt: Optional[str] = None

class SubTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    required_expertise: str
    dependencies: List[str] = Field(default_factory=list) # List of SubTask ids
    priority: int = Field(1, ge=1, le=5)
    status: str = "pending"

class TaskDecomposition(BaseModel):
    goal_summary: str
    subtasks: List[SubTask] = Field(default_factory=list)
    execution_order: List[List[str]] = Field(default_factory=list) # Groups of parallel subtask ids

class AgentFinding(BaseModel):
    agent_name: str
    role: str
    finding_summary: str
    detailed_analysis: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    reasoning: str
    tools_used: List[str] = Field(default_factory=list)
    token_usage: Optional[Dict[str, int]] = None # prompt_tokens, completion_tokens, total_tokens

class PlannerDecision(BaseModel):
    identified_domain: str
    approach_strategy: str
    complexity_estimate: str # low/medium/high/critical
    required_capabilities: List[str] = Field(default_factory=list)
    needs_retrieval: bool
    retrieval_type_hint: Optional[str] = None
    reasoning: str
