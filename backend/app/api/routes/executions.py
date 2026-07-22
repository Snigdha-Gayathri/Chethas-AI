from __future__ import annotations
from typing import List
import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from app.models.execution import Execution, ExecutionCreate, ExecutionSummary, ExecutionPhase
from app.api.routes.goals import GOALS_DB, get_goal
from app.api.routes.stream import broadcast_event
from app.storage import persistent_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/executions", tags=["Executions"])

# In-memory cache backed by SQLite persistent store
EXECUTIONS_DB: dict[str, Execution] = {}

async def run_execution_workflow(goal_id: str, execution_id: str):
    """Background workflow running the full multi-agent investigation and broadcasting live updates."""
    from app.orchestrator.graph import run_goal
    
    execution = EXECUTIONS_DB.get(execution_id) or persistent_store.get_execution(execution_id)
    if not execution:
        return
        
    goal_obj = GOALS_DB.get(goal_id) or persistent_store.get_goal(goal_id)
    goal_text = goal_obj.user_input if goal_obj else "General investigation task"
    
    execution.status = "running"
    execution.updated_at = datetime.now(timezone.utc)
    EXECUTIONS_DB[execution_id] = execution
    persistent_store.save_execution(execution)
    
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
        execution.completed_at = datetime.now(timezone.utc)
        
        # Populate execution timeline and results
        timeline = result_state.get("timeline_events", [])
        if hasattr(execution, "timeline"):
            execution.timeline = timeline
            
        EXECUTIONS_DB[execution_id] = execution
        persistent_store.save_execution(execution)
            
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
        EXECUTIONS_DB[execution_id] = execution
        persistent_store.save_execution(execution)
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
    goal_obj = GOALS_DB.get(execution_in.goal_id) or persistent_store.get_goal(execution_in.goal_id)
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
    persistent_store.save_execution(execution)

    # Trigger background execution workflow
    background_tasks.add_task(run_execution_workflow, execution_in.goal_id, exec_id)

    return execution

@router.get("", response_model=List[ExecutionSummary])
async def list_executions() -> List[ExecutionSummary]:
    """List all executions."""
    db_execs = persistent_store.list_executions()
    for ex in db_execs:
        EXECUTIONS_DB[ex.id] = ex
        
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
        execution = persistent_store.get_execution(execution_id)
        if execution:
            EXECUTIONS_DB[execution_id] = execution
            
    if not execution:
        # Check if we have event history for this execution ID to reconstruct a fallback execution
        events = persistent_store.get_event_history(execution_id)
        if events:
            from app.models.goal import Goal
            goal_id = "reconstructed"
            goal_text = "Reconstructed investigation session"
            for ev in events:
                if ev.get("metadata") and ev["metadata"].get("goal_id"):
                    goal_id = ev["metadata"]["goal_id"]
                if ev.get("content") and "Starting multi-agent investigation for goal:" in ev.get("content", ""):
                    goal_text = ev["content"].split("goal: '")[-1].rstrip("...'")
            
            goal_obj = GOALS_DB.get(goal_id) or persistent_store.get_goal(goal_id) or Goal(id=goal_id, user_input=goal_text)
            execution = Execution(
                id=execution_id,
                goal=goal_obj,
                status="completed" if any(e.get("event_type") == "completed" for e in events) else ("failed" if any(e.get("event_type") == "error" for e in events) else "running"),
                phases=[
                    ExecutionPhase(name="Planning"),
                    ExecutionPhase(name="Task Decomposition"),
                    ExecutionPhase(name="Role Generation"),
                    ExecutionPhase(name="Expert Analysis"),
                    ExecutionPhase(name="Deliberation"),
                    ExecutionPhase(name="Reflection"),
                    ExecutionPhase(name="Judgment"),
                    ExecutionPhase(name="Consensus"),
                ]
            )
            EXECUTIONS_DB[execution_id] = execution
            persistent_store.save_execution(execution)
            return execution

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with id {execution_id} not found."
        )
    return execution

@router.post("/{execution_id}/cancel", response_model=Execution)
async def cancel_execution(execution_id: str) -> Execution:
    """Cancel a running execution."""
    execution = EXECUTIONS_DB.get(execution_id) or persistent_store.get_execution(execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution with id {execution_id} not found."
        )
    execution.status = "cancelled"
    execution.updated_at = datetime.now(timezone.utc)
    EXECUTIONS_DB[execution_id] = execution
    persistent_store.save_execution(execution)
    return execution


