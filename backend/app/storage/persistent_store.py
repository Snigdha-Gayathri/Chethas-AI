from __future__ import annotations
import sqlite3
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, List, Any
from app.models.goal import Goal
from app.models.execution import Execution

logger = logging.getLogger("chethas.persistent_store")

class PersistentStore:
    """Robust persistent storage using SQLite for Goals, Executions, and SSE Event Histories.
    Ensures that executions and histories are never lost during server restarts, cold starts, or multiple uvicorn workers.
    """
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Try to store in ./data/chethas_store.db or fall back to system temp path if not writable
            base_dir = Path("data")
            try:
                base_dir.mkdir(parents=True, exist_ok=True)
                self.db_path = str(base_dir / "chethas_store.db")
            except Exception:
                self.db_path = str(Path(tempfile.gettempdir()) / "chethas_store.db")
        else:
            self.db_path = db_path
            
        self._init_db()
        
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS goals (
                        id TEXT PRIMARY KEY,
                        data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS executions (
                        id TEXT PRIMARY KEY,
                        goal_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        data TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS event_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        execution_id TEXT NOT NULL,
                        event_data TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_exec_goal ON executions(goal_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_event_exec ON event_history(execution_id)")
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize SQLite store at {self.db_path}: {e}")

    # --- Goals ---
    def save_goal(self, goal: Goal) -> None:
        try:
            data_str = goal.model_dump_json() if hasattr(goal, "model_dump_json") else json.dumps(goal.dict())
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO goals (id, data) VALUES (?, ?)",
                    (goal.id, data_str)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save goal {goal.id} to SQLite: {e}")

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT data FROM goals WHERE id = ?", (goal_id,))
                row = cursor.fetchone()
                if row:
                    data = json.loads(row["data"])
                    return Goal(**data)
        except Exception as e:
            logger.error(f"Failed to get goal {goal_id} from SQLite: {e}")
        return None

    def list_goals(self) -> List[Goal]:
        goals = []
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT data FROM goals ORDER BY created_at DESC")
                for row in cursor.fetchall():
                    try:
                        data = json.loads(row["data"])
                        goals.append(Goal(**data))
                    except Exception as ex:
                        logger.warning(f"Skipping malformed goal row: {ex}")
        except Exception as e:
            logger.error(f"Failed to list goals from SQLite: {e}")
        return goals

    # --- Executions ---
    def save_execution(self, execution: Execution) -> None:
        try:
            data_str = execution.model_dump_json() if hasattr(execution, "model_dump_json") else json.dumps(execution.dict())
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO executions (id, goal_id, status, data, updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                    (execution.id, execution.goal.id, execution.status, data_str)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save execution {execution.id} to SQLite: {e}")

    def get_execution(self, execution_id: str) -> Optional[Execution]:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT data FROM executions WHERE id = ?", (execution_id,))
                row = cursor.fetchone()
                if row:
                    data = json.loads(row["data"])
                    return Execution(**data)
        except Exception as e:
            logger.error(f"Failed to get execution {execution_id} from SQLite: {e}")
        return None

    def list_executions(self) -> List[Execution]:
        executions = []
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT data FROM executions ORDER BY updated_at DESC")
                for row in cursor.fetchall():
                    try:
                        data = json.loads(row["data"])
                        executions.append(Execution(**data))
                    except Exception as ex:
                        logger.warning(f"Skipping malformed execution row: {ex}")
        except Exception as e:
            logger.error(f"Failed to list executions from SQLite: {e}")
        return executions

    # --- SSE Event History ---
    def save_event(self, execution_id: str, event_data: dict) -> None:
        try:
            data_str = json.dumps(event_data)
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO event_history (execution_id, event_data) VALUES (?, ?)",
                    (execution_id, data_str)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save event for {execution_id} to SQLite: {e}")

    def get_event_history(self, execution_id: str) -> List[dict]:
        events = []
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT event_data FROM event_history WHERE execution_id = ? ORDER BY id ASC", (execution_id,))
                for row in cursor.fetchall():
                    try:
                        events.append(json.loads(row["event_data"]))
                    except Exception as ex:
                        logger.warning(f"Skipping malformed event row: {ex}")
        except Exception as e:
            logger.error(f"Failed to get event history for {execution_id} from SQLite: {e}")
        return events

# Singleton instance for persistent storage
persistent_store = PersistentStore()
