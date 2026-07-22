from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import uuid
from .goal import Goal

class ExecutionPhase(BaseModel):
    name: str
    status: str = "pending" # pending/running/completed/failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    output: Optional[Dict[str, Any]] = None

class TimelineEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    phase: str
    agent_name: Optional[str] = None
    event_type: str # info/decision/evidence/debate/reflection/judgment/error
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ContextStrategyDecision(BaseModel):
    query: str
    selected_strategy: str
    reasoning: str
    alternatives_considered: List[str] = Field(default_factory=list)
    confidence: float

class ExecutionCreate(BaseModel):
    goal_id: str

class ExecutionSummary(BaseModel):
    id: str
    goal_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

class Execution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: Goal
    status: str = "pending"
    phases: List[ExecutionPhase] = Field(default_factory=list)
    timeline_events: List[TimelineEvent] = Field(default_factory=list)
    agents: List[Dict[str, Any]] = Field(default_factory=list) # References to AgentRoles
    context_strategy_decisions: List[ContextStrategyDecision] = Field(default_factory=list)
    final_output: Optional[Dict[str, Any]] = None
    evaluation_metrics: Optional[Dict[str, Any]] = None
    iteration: int = 0
    confidence_score: float = 0.0
    max_iterations: int = 3
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
