from __future__ import annotations

import json
import logging
from typing import Dict, Any, List
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Global shared blackboard across agents during a graph run
_BLACKBOARD_STORAGE: List[Dict[str, Any]] = []

def get_blackboard_entries() -> List[Dict[str, Any]]:
    """Return current entries on the shared memory blackboard."""
    return list(_BLACKBOARD_STORAGE)

def clear_blackboard() -> None:
    """Clear blackboard storage between distinct graph runs."""
    _BLACKBOARD_STORAGE.clear()

@tool
def shared_blackboard_post(agent_name: str, topic: str, content: str, entry_type: str = "insight") -> str:
    """Post an intermediate finding, hypothesis, or question to the shared agent blackboard so other concurrent agents can see it.
    
    Args:
        agent_name: Name or role of the agent posting to the blackboard.
        topic: Short topic or category tag (e.g., 'data_anomaly', 'contradiction_question').
        content: Detailed explanation or finding being shared.
        entry_type: One of 'insight', 'hypothesis', 'question', or 'warning' (default 'insight').
    Returns:
        Confirmation status of the post.
    """
    logger.info(f"Blackboard post by '{agent_name}': [{topic}] ({entry_type})")
    entry = {
        "agent": agent_name,
        "topic": topic,
        "content": content,
        "entry_type": entry_type
    }
    _BLACKBOARD_STORAGE.append(entry)
    return json.dumps({"status": "posted", "entry_index": len(_BLACKBOARD_STORAGE) - 1, "entry": entry})

@tool
def shared_blackboard_read(topic_filter: str = "") -> str:
    """Read insights, hypotheses, and questions currently posted to the shared blackboard by peer agents.
    
    Args:
        topic_filter: Optional keyword or topic string to filter entries. Leave blank "" to read all entries.
    Returns:
        JSON string listing blackboard entries posted so far.
    """
    if not topic_filter:
        entries = _BLACKBOARD_STORAGE
    else:
        entries = [
            e for e in _BLACKBOARD_STORAGE 
            if topic_filter.lower() in e.get("topic", "").lower() or topic_filter.lower() in e.get("content", "").lower()
        ]
    return json.dumps({"status": "success", "total_entries": len(entries), "entries": entries}, indent=2)
