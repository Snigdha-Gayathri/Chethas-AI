from __future__ import annotations

import logging
from typing import Optional, Dict, Any, List
from app.models.execution import Execution

logger = logging.getLogger(__name__)

try:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    _POSTGRES_AVAILABLE = True
except ImportError:
    _POSTGRES_AVAILABLE = False
    from langgraph.checkpoint.memory import MemorySaver

class StateStore:
    """PostgreSQL state store for LangGraph with graceful memory fallback."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._checkpointer: Optional[Any] = None
    
    async def get_checkpointer(self) -> Any:
        """Get or create the async checkpointer for LangGraph."""
        if self._checkpointer is None:
            if _POSTGRES_AVAILABLE:
                try:
                    self._checkpointer = AsyncPostgresSaver.from_conn_string(self.database_url)
                    await self._checkpointer.setup()
                except Exception as e:
                    logger.warning(f"Failed to setup Postgres checkpointer ({e}). Using MemorySaver.")
                    from langgraph.checkpoint.memory import MemorySaver
                    self._checkpointer = MemorySaver()
            else:
                logger.info("langgraph-checkpoint-postgres not installed. Using MemorySaver fallback.")
                from langgraph.checkpoint.memory import MemorySaver
                self._checkpointer = MemorySaver()
        return self._checkpointer


class InMemoryExecutionStore:
    """Simple in-memory execution store for storing execution records."""
    
    def __init__(self):
        self._executions: Dict[str, Execution] = {}
        
    def save_execution(self, execution: Execution) -> None:
        self._executions[execution.id] = execution
        
    def get_execution(self, execution_id: str) -> Optional[Execution]:
        return self._executions.get(execution_id)
        
    def list_executions(self) -> List[Execution]:
        return list(self._executions.values())
        
    def delete_execution(self, execution_id: str) -> bool:
        if execution_id in self._executions:
            del self._executions[execution_id]
            return True
        return False
