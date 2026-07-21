from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import uuid

class GoalCreate(BaseModel):
    """User-submitted goal input."""
    user_input: str = Field(..., min_length=10, description="The user's goal or objective")
    domain_hint: Optional[str] = Field(None, description="Optional domain hint (e.g., 'software engineering', 'finance')")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Optional constraints for the goal")
    document_ids: Optional[List[str]] = Field(default_factory=list, description="IDs of uploaded documents to use")

class Goal(BaseModel):
    """A stored goal with metadata."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_input: str
    domain_hint: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    document_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"  # pending, executing, completed, failed
