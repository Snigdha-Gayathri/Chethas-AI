from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from .base import BaseAgent
from app.models.agent import AgentRole, SubTask, PlannerDecision
from .prompts.role_generator import get_role_generator_prompt

class GeneratedRoles(BaseModel):
    """Helper model for generating a list of AgentRole objects."""
    roles: list[AgentRole] = Field(..., description="List of generated expert roles")

class RoleGeneratorAgent(BaseAgent):
    """Role Generator Agent - dynamically creates expert roles based on subtasks."""
    
    def __init__(self):
        super().__init__(
            name="RoleGenerator",
            role="Team Builder",
            expertise="Agent role design, capability matching, and team topology optimization."
        )
    
    def get_system_prompt(self) -> str:
        return get_role_generator_prompt()
    
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("Executing Role Generator Agent")
        
        goal = state.get("goal")
        planner_decision: dict | None = state.get("planner_decision")
        subtasks: list[dict] = state.get("subtasks", [])

        if not goal or not planner_decision or not subtasks:
            raise ValueError("State must contain 'goal', 'planner_decision', and 'subtasks'")

        subtasks_text = "\n".join(
            f"- [{st.get('id')}] {st.get('description')} (Expertise: {st.get('required_expertise')})"
            for st in subtasks
        )

        prompt = f"""
Goal: {goal}
Domain: {planner_decision.get('identified_domain')}
Complexity: {planner_decision.get('complexity_estimate')}

Subtasks:
{subtasks_text}

Design the optimal team of expert agents to handle these subtasks.
"""
        result: GeneratedRoles = await self._invoke_llm(
            prompt=prompt,
            structured_output=GeneratedRoles
        )

        self.logger.info(f"Generated {len(result.roles)} expert roles")
        return {"generated_roles": [r.model_dump() for r in result.roles]}
