from __future__ import annotations

from typing import Any
from .base import BaseAgent
from app.models.agent import AgentRole, AgentFinding
from .prompts.expert import get_expert_prompt
from app.context.retrieval import retrieve_evidence
from app.tools.registry import get_tools_by_names

class DynamicExpertAgent(BaseAgent):
    """Expert Agent created dynamically based on a generated AgentRole."""

    def __init__(self, role: AgentRole):
        super().__init__(
            name=f"Expert_{role.name.replace(' ', '')}",
            role=role.name,
            expertise=role.expertise,
            tools=role.tools
        )
        self.agent_role = role

    def get_system_prompt(self) -> str:
        return get_expert_prompt(self.agent_role)

    def get_tools(self) -> list:
        if self.agent_role.tools:
            return get_tools_by_names(self.agent_role.tools)
        return []

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self.logger.info(f"Executing Expert Agent: {self.name} with tools: {self.agent_role.tools}")

        goal = state.get("goal", "")
        all_subtasks: list[dict] = state.get("subtasks", [])
        assigned_ids = set(self.agent_role.assigned_subtasks)

        # Filter subtasks assigned to this specific role (state holds dicts).
        assigned_subtasks = [st for st in all_subtasks if st.get("id") in assigned_ids]

        if not assigned_subtasks:
            self.logger.warning(f"No subtasks assigned to {self.name}. Proceeding with general analysis.")
            subtasks_text = "Analyze the goal directly based on your expertise."
            query_seed = goal
        else:
            subtasks_text = "\n".join(f"- {st.get('description', '')}" for st in assigned_subtasks)
            query_seed = f"{goal}\n" + "\n".join(st.get("description", "") for st in assigned_subtasks)

        # Ground the expert with real retrieved evidence when documents are available.
        document_ids = state.get("document_ids", [])
        evidence_items = await retrieve_evidence(
            query=query_seed,
            document_ids=document_ids,
            strategy_hint=state.get("planner_decision", {}).get("retrieval_type_hint"),
        )
        if evidence_items:
            evidence_text = "\n\n".join(
                f"[{i+1}] (source: {e.get('source', 'unknown')}, score: {e.get('confidence', 0.0):.2f})\n{e.get('content', '')}"
                for i, e in enumerate(evidence_items)
            )
            evidence_block = (
                "Retrieved Evidence (cite by [n] in your citations; do not invent sources beyond these):\n"
                f"{evidence_text}"
            )
        else:
            evidence_block = (
                "No initial external evidence retrieved. Reason from your expertise, and use your tools "
                "('evidence_search', 'python_interpreter', 'graph_query') actively if you need more evidence or calculation."
            )

        prompt = f"""
Overall Goal: {goal}

Your Assigned Subtasks:
{subtasks_text}

{evidence_block}

Provide your expert findings, detailed analysis, a realistic confidence score, reasoning, and citations
grounded in the retrieved evidence or tool results.
"""
        finding: AgentFinding = await self._invoke_llm(
            prompt=prompt,
            structured_output=AgentFinding,
        )

        # Ensure identity fields are populated regardless of what the LLM returned.
        finding.agent_name = self.name
        finding.role = self.agent_role.name
        if not finding.evidence:
            finding.evidence = evidence_items
        if not finding.tools_used and self.agent_role.tools:
            finding.tools_used = list(self.agent_role.tools)

        self.logger.info(f"{self.name} completed findings with confidence {finding.confidence}")
        return {
            "expert_findings": [finding.model_dump()],
            "evidence_pool": evidence_items,
        }


class ExpertAgentFactory:
    """Factory to create and execute dynamic expert agents."""

    @staticmethod
    def create_expert(role: AgentRole) -> DynamicExpertAgent:
        """Create a single DynamicExpertAgent from an AgentRole."""
        return DynamicExpertAgent(role)

    @staticmethod
    def create_experts(roles: list[AgentRole]) -> list[DynamicExpertAgent]:
        """Create instances of DynamicExpertAgent from a list of AgentRoles."""
        return [DynamicExpertAgent(role) for role in roles]

    @staticmethod
    async def execute_expert(role: AgentRole, state: dict[str, Any]) -> dict[str, Any]:
        """Static method to execute a single expert, useful as a LangGraph node."""
        agent = DynamicExpertAgent(role)
        return await agent.execute(state)
