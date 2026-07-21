from __future__ import annotations
from typing import TypedDict, Annotated, Any, Optional
import operator
from datetime import datetime, timezone

def merge_lists(left: list, right: list) -> list:
    """Reducer that merges two lists."""
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right

class ChethasState(TypedDict):
    # Input
    goal: str
    constraints: dict
    document_ids: list[str]
    
    # Planning Phase
    planner_decision: dict
    task_decomposition: dict
    subtasks: list[dict]
    generated_roles: list[dict]
    
    # Expert Work
    expert_findings: Annotated[list[dict], merge_lists]
    evidence_pool: Annotated[list[dict], merge_lists]
    verification_report: dict
    
    # Deliberation
    debate_rounds: Annotated[list[dict], merge_lists]
    current_debate_round: int
    
    # Reflection & Judgment
    reflection_report: dict
    judge_verdict: dict
    consensus: dict
    
    # Control Flow
    iteration: Annotated[int, operator.add]
    confidence_score: float
    max_iterations: int
    status: str
    
    # Transparency
    timeline_events: Annotated[list[dict], merge_lists]
    context_strategy_decisions: Annotated[list[dict], merge_lists]
    
    # Evaluation
    evaluation_metrics: dict
    
    # Final output
    final_output: dict
