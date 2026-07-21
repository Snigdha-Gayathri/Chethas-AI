from __future__ import annotations
from typing import List
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from app.models.evaluation import EvaluationResult

router = APIRouter(prefix="/api/evaluations", tags=["Evaluations"])

# In-memory store
EVALUATIONS_DB: dict[str, EvaluationResult] = {}

@router.get("", response_model=List[EvaluationResult])
async def list_evaluations() -> List[EvaluationResult]:
    """List all evaluation results."""
    return list(EVALUATIONS_DB.values())

@router.get("/{execution_id}", response_model=EvaluationResult)
async def get_evaluation(execution_id: str) -> EvaluationResult:
    """Get evaluation results for an execution."""
    for eval_result in EVALUATIONS_DB.values():
        if getattr(eval_result, "execution_id", None) == execution_id:
            return eval_result
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Evaluation result for execution {execution_id} not found."
    )

@router.post("/{execution_id}/run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_evaluation(execution_id: str, background_tasks: BackgroundTasks) -> dict:
    """Trigger evaluation for an execution."""
    
    def mock_eval_task(exec_id: str):
        # Stub background task for evaluation pipeline
        pass
        
    background_tasks.add_task(mock_eval_task, execution_id)
    return {"message": "Evaluation started", "execution_id": execution_id}
