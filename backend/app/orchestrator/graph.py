from __future__ import annotations
import uuid
import logging
from langgraph.graph import StateGraph, START, END

from app.orchestrator.state import ChethasState
from app.orchestrator.nodes import (
    planner_node, task_decomposition_node, role_generator_node,
    expert_execution_node, evidence_verification_node,
    deliberation_node, reflection_node, judge_node, consensus_node
)
from app.orchestrator.edges import should_iterate

logger = logging.getLogger(__name__)

def build_chethas_graph(checkpointer=None) -> StateGraph:
    """Build the main Chethas orchestration graph."""
    builder = StateGraph(ChethasState)
    
    # Add nodes
    builder.add_node("planner", planner_node)
    builder.add_node("task_decomposition", task_decomposition_node)
    builder.add_node("role_generator", role_generator_node)
    builder.add_node("expert_execution", expert_execution_node)
    builder.add_node("evidence_verification", evidence_verification_node)
    builder.add_node("deliberation", deliberation_node)
    builder.add_node("reflection", reflection_node)
    builder.add_node("judge", judge_node)
    builder.add_node("consensus", consensus_node)
    
    # Linear flow
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "task_decomposition")
    builder.add_edge("task_decomposition", "role_generator")
    builder.add_edge("role_generator", "expert_execution")
    builder.add_edge("expert_execution", "evidence_verification")
    builder.add_edge("evidence_verification", "deliberation")
    builder.add_edge("deliberation", "reflection")
    builder.add_edge("reflection", "judge")
    
    # Conditional edge
    builder.add_conditional_edges(
        "judge",
        should_iterate,
        {
            "iterate": "planner",
            "finalize": "consensus"
        }
    )
    
    builder.add_edge("consensus", END)
    
    return builder.compile(checkpointer=checkpointer)

async def run_goal(goal: str, constraints: dict = None, document_ids: list = None, checkpointer=None, execution_id: str = None) -> dict:
    """Execute a complete goal investigation."""
    graph = build_chethas_graph(checkpointer=checkpointer)
    
    initial_state = {
        "goal": goal,
        "execution_id": execution_id,
        "constraints": constraints or {},
        "document_ids": document_ids or [],
        "planner_decision": {},
        "task_decomposition": {},
        "subtasks": [],
        "generated_roles": [],
        "expert_findings": [],
        "evidence_pool": [],
        "debate_rounds": [],
        "current_debate_round": 0,
        "reflection_report": {},
        "judge_verdict": {},
        "consensus": {},
        "iteration": 0,
        "confidence_score": 0.0,
        "max_iterations": 3,
        "status": "initializing",
        "timeline_events": [],
        "context_strategy_decisions": [],
        "evaluation_metrics": {},
        "final_output": {},
    }
    
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    try:
        final_state = await graph.ainvoke(initial_state, config=config)
        return final_state
    except Exception as e:
        logger.error(f"Error running goal graph: {e}")
        return {"status": "error_orchestrator"}
