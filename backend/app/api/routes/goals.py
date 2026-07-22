from __future__ import annotations
from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status
from app.models.goal import GoalCreate, Goal
from app.storage import persistent_store

router = APIRouter(prefix="/api/goals", tags=["Goals"])

# In-memory cache backed by SQLite persistent store
GOALS_DB: dict[str, Goal] = {}

@router.post("", response_model=Goal, status_code=status.HTTP_201_CREATED)
async def create_goal(goal_in: GoalCreate) -> Goal:
    """Create a new goal."""
    goal_id = str(uuid.uuid4())
    goal_dict = goal_in.model_dump() if hasattr(goal_in, "model_dump") else goal_in.dict()
    goal_dict["id"] = goal_id
    
    goal = Goal(**goal_dict)
    GOALS_DB[goal_id] = goal
    persistent_store.save_goal(goal)
    return goal

@router.get("", response_model=List[Goal])
async def list_goals() -> List[Goal]:
    """List all goals."""
    db_goals = persistent_store.list_goals()
    for g in db_goals:
        GOALS_DB[g.id] = g
    return list(GOALS_DB.values())

@router.get("/{goal_id}", response_model=Goal)
async def get_goal(goal_id: str) -> Goal:
    """Get a specific goal."""
    goal = GOALS_DB.get(goal_id)
    if not goal:
        goal = persistent_store.get_goal(goal_id)
        if goal:
            GOALS_DB[goal_id] = goal
            
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found."
        )
    return goal

