from __future__ import annotations
import logging

from app.orchestrator.state import ChethasState
from app.config import get_settings

logger = logging.getLogger(__name__)

def should_iterate(state: ChethasState) -> str:
    """Decide whether to iterate or finalize."""
    try:
        settings = get_settings()
        confidence = state.get("confidence_score", 0.0)
        iteration = state.get("iteration", 0)
        max_iter = state.get("max_iterations", settings.max_iterations)
        
        judge_verdict = state.get("judge_verdict", {})
        needs_iteration = judge_verdict.get("needs_iteration", False)
        
        if needs_iteration and iteration < max_iter and confidence < settings.confidence_threshold:
            return "iterate"
        return "finalize"
    except Exception as e:
        logger.error(f"Error determining edge iteration: {e}")
        return "finalize"
