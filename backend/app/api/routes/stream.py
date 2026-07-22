from __future__ import annotations
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.storage import persistent_store

router = APIRouter(prefix="/api/executions", tags=["Streaming"])

# Shared live event queues keyed by execution_id
STREAM_QUEUES: Dict[str, asyncio.Queue] = {}
EVENT_HISTORY: Dict[str, List[dict]] = {}

async def broadcast_event(execution_id: str, event_type: str, phase: str, agent_name: str, content: str, metadata: dict = None):
    """Broadcast an update event to any active SSE subscribers and store in history."""
    event_data = {
        "event_type": event_type,
        "phase": phase,
        "agent_name": agent_name,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {}
    }
    if execution_id not in EVENT_HISTORY:
        EVENT_HISTORY[execution_id] = []
    EVENT_HISTORY[execution_id].append(event_data)
    persistent_store.save_event(execution_id, event_data)
    
    if execution_id in STREAM_QUEUES:
        await STREAM_QUEUES[execution_id].put(event_data)

async def real_event_generator(execution_id: str):
    """Yield SSE execution updates from real workflow events or history."""
    if execution_id not in STREAM_QUEUES:
        STREAM_QUEUES[execution_id] = asyncio.Queue()
        
    # First replay past events if any occurred before connecting
    history = EVENT_HISTORY.get(execution_id)
    if not history:
        history = persistent_store.get_event_history(execution_id)
        if history:
            EVENT_HISTORY[execution_id] = history
    if not history:
        history = []
        
    for ev in history:
        yield {
            "event": "update",
            "data": json.dumps(ev)
        }
        
    # Then stream live events as they occur
    queue = STREAM_QUEUES[execution_id]
    try:
        while True:
            # Wait for next event with a timeout to send heartbeats
            try:
                event_data = await asyncio.wait_for(queue.get(), timeout=15.0)
                if event_data.get("event_type") == "completed" or event_data.get("event_type") == "error":
                    yield {"event": "update", "data": json.dumps(event_data)}
                    break
                yield {"event": "update", "data": json.dumps(event_data)}
            except asyncio.TimeoutError:
                # Send heartbeat
                yield {"event": "ping", "data": "ping"}
    finally:
        if execution_id in STREAM_QUEUES:
            del STREAM_QUEUES[execution_id]

@router.get("/{execution_id}/stream")
async def stream_execution_updates(execution_id: str) -> EventSourceResponse:
    """Server-Sent Events endpoint that streams live workflow execution updates in real-time."""
    return EventSourceResponse(real_event_generator(execution_id))


