from __future__ import annotations

from typing import Any
from .base import BaseAgent
from app.models.agent import TaskDecomposition
from .prompts.task_decomposer import get_task_decomposer_prompt

class TaskDecomposerAgent(BaseAgent):
    """Task Decomposer Agent - breaks goals into manageable subtasks."""
    
    def __init__(self):
        super().__init__(
            name="TaskDecomposer",
            role="Task Decomposer",
            expertise="Work breakdown structures, dependency mapping, and task prioritization.",
            tools=["evidence_search"]
        )
    
    def get_system_prompt(self) -> str:
        return get_task_decomposer_prompt()
    
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("Executing Task Decomposer Agent")
        
        goal = state.get("goal")
        planner_decision = state.get("planner_decision")

        if not goal or not planner_decision:
            raise ValueError("State must contain 'goal' and 'planner_decision'")

        prompt = f"""
Goal: {goal}
Planner Decision:
- Domain: {planner_decision.get('identified_domain')}
- Complexity: {planner_decision.get('complexity_estimate')}
- Strategy: {planner_decision.get('approach_strategy')}
- Capabilities Required: {planner_decision.get('required_capabilities')}

Please decompose this goal into subtasks.
"""
        decomposition: TaskDecomposition = await self._invoke_llm(
            prompt=prompt,
            structured_output=TaskDecomposition
        )

        self.logger.info(f"Generated {len(decomposition.subtasks)} subtasks")
        return {
            "task_decomposition": decomposition.model_dump(),
            "subtasks": [st.model_dump() for st in decomposition.subtasks]
        }
