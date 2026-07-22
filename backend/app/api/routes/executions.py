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

def update_execution_phase_status(execution_id: str, phase_key: str, event_type: str):
    """Update phase status in execution object based on workflow progression."""
    execution = EXECUTIONS_DB.get(execution_id) or persistent_store.get_execution(execution_id)
    if not execution:
        return
        
    phase_map = {
        "planning": "p1",
        "task_decomposition": "p2",
        "role_generation": "p3",
        "expert_analysis": "p4",
        "deliberation": "p5",
        "evidence_verification": "p5",
        "reflection": "p6",
        "judging": "p7",
        "consensus": "p8"
    }
    target_id = phase_map.get(phase_key)
    if not target_id:
        return
        
    changed = False
    now = datetime.now(timezone.utc)
    
    for p in execution.phases:
        if p.id == target_id:
            if event_type in ("status_update", "info") and p.status == "pending":
                p.status = "running"
                p.started_at = p.started_at or now
                changed = True
            elif event_type in ("decision", "finding", "verification", "debate", "reflection", "verdict", "consensus", "completed"):
                p.status = "completed"
                p.started_at = p.started_at or now
                p.completed_at = now
                if p.started_at:
                    p.duration_ms = int((now - p.started_at).total_seconds() * 1000)
                changed = True
            elif event_type == "error":
                p.status = "failed"
                p.completed_at = now
                changed = True
        else:
            try:
                p_idx = int(p.id[1:])
                t_idx = int(target_id[1:])
                if p_idx < t_idx and p.status in ("pending", "running"):
                    p.status = "completed"
                    p.completed_at = p.completed_at or now
                    changed = True
            except (ValueError, IndexError):
                pass
                
    if changed:
        EXECUTIONS_DB[execution_id] = execution
        persistent_store.save_execution(execution)

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
    if execution.phases and len(execution.phases) > 0:
        execution.phases[0].status = "running"
        execution.phases[0].started_at = datetime.now(timezone.utc)
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
        for p in execution.phases:
            if p.status in ("pending", "running"):
                p.status = "completed"
                p.completed_at = p.completed_at or datetime.now(timezone.utc)
        
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
        for p in execution.phases:
            if p.status == "running":
                p.status = "failed"
                p.completed_at = datetime.now(timezone.utc)
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
            ExecutionPhase(id="p1", name="Planning"),
            ExecutionPhase(id="p2", name="Task Decomposition"),
            ExecutionPhase(id="p3", name="Role Generation"),
            ExecutionPhase(id="p4", name="Expert Analysis"),
            ExecutionPhase(id="p5", name="Deliberation"),
            ExecutionPhase(id="p6", name="Reflection"),
            ExecutionPhase(id="p7", name="Judgment"),
            ExecutionPhase(id="p8", name="Consensus"),
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
                    ExecutionPhase(id="p1", name="Planning", status="completed" if any(e.get("phase")=="planning" for e in events) else "pending"),
                    ExecutionPhase(id="p2", name="Task Decomposition", status="completed" if any(e.get("phase")=="task_decomposition" for e in events) else "pending"),
                    ExecutionPhase(id="p3", name="Role Generation", status="completed" if any(e.get("phase")=="role_generation" for e in events) else "pending"),
                    ExecutionPhase(id="p4", name="Expert Analysis", status="completed" if any(e.get("phase")=="expert_analysis" for e in events) else "pending"),
                    ExecutionPhase(id="p5", name="Deliberation", status="completed" if any(e.get("phase") in ("deliberation", "evidence_verification") for e in events) else "pending"),
                    ExecutionPhase(id="p6", name="Reflection", status="completed" if any(e.get("phase")=="reflection" for e in events) else "pending"),
                    ExecutionPhase(id="p7", name="Judgment", status="completed" if any(e.get("phase")=="judging" for e in events) else "pending"),
                    ExecutionPhase(id="p8", name="Consensus", status="completed" if any(e.get("phase")=="consensus" for e in events) else "pending"),
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


