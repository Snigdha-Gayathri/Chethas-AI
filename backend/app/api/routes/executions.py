from __future__ import annotations
from typing import List
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from app.models.execution import Execution, ExecutionCreate, ExecutionSummary, ExecutionPhase
from app.api.routes.goals import GOALS_DB
from app.api.routes.stream import broadcast_event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/executions", tags=["Executions"])

# In-memory store
EXECUTIONS_DB: dict[str, Execution] = {}

async def run_execution_workflow(goal_id: str, execution_id: str):
    """Background workflow running the full multi-agent investigation and broadcasting live updates."""
    from app.orchestrator.graph import run_goal
    
    execution = EXECUTIONS_DB.get(execution_id)
    if not execution:
        return
        
    goal_obj = GOALS_DB.get(goal_id)
    goal_text = goal_obj.user_input if goal_obj else "General investigation task"
    
    execution.status = "running"
    execution.updated_at = datetime.now(timezone.utc)
    
    await broadcast_event(
        execution_id=execution_id,
        event_type="status_update",
        phase="planning",
        agent_name="System",
        content=f"Starting multi-agent investigation for goal: '{goal_text[:60]}...'",
        metadata={"goal_id": goal_id}
    )
    
    try:
        # Run the full LangGraph orchestration
        result_state = await run_goal(goal=goal_text, execution_id=execution_id)
        
        if result_state.get("status") == "error_orchestrator":
            raise RuntimeError("Orchestration graph encountered an error during execution.")
            
        execution.status = "completed"
        execution.updated_at = datetime.now(timezone.utc)
        
        # Populate execution timeline and results
        timeline = result_state.get("timeline_events", [])
        if hasattr(execution, "timeline"):
            execution.timeline = timeline
            
        await broadcast_event(
            execution_id=execution_id,
            event_type="completed",
            phase="consensus",
            agent_name="ConsensusBuilder",
            content="Investigation completed successfully. Consensus reached.",
            metadata={"timeline_count": len(timeline)}
        )
    except Exception as e:
        logger.error(f"Execution workflow failed for {execution_id}: {e}", exc_info=True)
        execution.status = "failed"
        execution.updated_at = datetime.now(timezone.utc)
        await broadcast_event(
            execution_id=execution_id,
            event_type="error",
            phase="system",
            agent_name="System",
            content=f"Execution error: {str(e)}. If this is an API key error, check GEMINI_API_KEY in .env.",
            metadata={"error": str(e)}
        )

@router.post("", response_model=Execution, status_code=status.HTTP_201_CREATED)
async def create_execution(execution_in: ExecutionCreate, background_tasks: BackgroundTasks) -> Execution:
    """Start a new execution for a goal."""
    goal_obj = GOALS_DB.get(execution_in.goal_id)
    if not goal_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {execution_in.goal_id} not found."
        )

    exec_id = str(uuid.uuid4())
    execution = Execution(
        id=exec_id,
        goal=goal_obj,
        status="pending",
        phases=[
            ExecutionPhase(name="Planning"),
            ExecutionPhase(name="Task Decomposition"),
            ExecutionPhase(name="Role Generation"),
            ExecutionPhase(name="Expert Analysis"),
            ExecutionPhase(name="Deliberation"),
            ExecutionPhase(name="Reflection"),
            ExecutionPhase(name="Judgment"),
            ExecutionPhase(name="Consensus"),
        ],
    )
    EXECUTIONS_DB[exec_id] = execution

    # Trigger background execution workflow
    background_tasks.add_task(run_execution_workflow, execution_in.goal_id, exec_id)

    return execution

@router.get("", response_model=List[ExecutionSummary])
async def list_executions() -> List[ExecutionSummary]:
    """List all executions."""
    summaries = []
    for exec_obj in EXECUTIONS_DB.values():
        summaries.append(ExecutionSummary(
            id=exec_obj.id,
            goal_id=exec_obj.goal.id,
            status=exec_obj.status,
            created_at=exec_obj.created_at,
            completed_at=exec_obj.completed_at,
        ))
    return summaries

@router.get("/{execution_id}", response_model=Execution)
async def get_execution(execution_id: str) -> Execution:
    """Get execution details including all phases, timeline events, agents, etc."""
    execution = EXECUTIONS_DB.get(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with id {execution_id} not found."
        )
    return execution

@router.post("/{execution_id}/cancel", response_model=Execution)
async def cancel_execution(execution_id: str) -> Execution:
    """Cancel a running execution."""
    execution = EXECUTIONS_DB.get(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with id {execution_id} not found."
        )
    execution.status = "cancelled"
    execution.updated_at = datetime.now(timezone.utc)
    return execution

