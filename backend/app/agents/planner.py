from __future__ import annotations

from typing import Any
from .base import BaseAgent
from app.models.agent import PlannerDecision
from app.llm.provider import get_planner_llm
from .prompts.planner import get_planner_prompt

class PlannerAgent(BaseAgent):
    """Planner Agent - analyzes goal, determines strategy and evidence needs."""
    
    def __init__(self):
        super().__init__(
            name="Planner",
            role="Strategic Planner",
            expertise="Goal analysis, domain identification, strategy formulation, and resource allocation.",
            tools=["evidence_search", "query_rewrite"]
        )
    
    def get_system_prompt(self) -> str:
        return get_planner_prompt()
    
    async def _invoke_planner_llm(self, prompt: str, structured_output=None):
        """Uses planner specific LLM which has higher reasoning capability."""
        try:
            llm = get_planner_llm()
            if structured_output:
                llm = llm.with_structured_output(structured_output)
            messages = [
                ("system", self.get_system_prompt()),
                ("human", prompt),
            ]
            return await llm.ainvoke(messages)
        except Exception as e:
            self.logger.warning(f"Planner LLM invocation failed ({e}). Returning fallback PlannerDecision. Set GOOGLE_API_KEY in .env for live reasoning.")
            from app.models.agent import PlannerDecision
            return PlannerDecision(
                identified_domain="Systems Architecture & Research Strategy",
                approach_strategy="Hybrid empirical validation and ReAct multi-agent evidence synthesis",
                complexity_estimate="high",
                required_capabilities=["evidence_search", "python_interpreter", "citation_verify", "graph_query"],
                needs_retrieval=True,
                retrieval_type_hint="semantic_hybrid",
                reasoning="Goal requires deep comparative reasoning and empirical verification across diverse knowledge domains."
            )
    
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        self.logger.info("Executing Planner Agent")
        
        goal = state.get("goal")
        if not goal:
            raise ValueError("State must contain 'goal'")
            
        prompt = f"Please analyze the following goal and formulate a planner decision:\nGoal: {goal}"
        
        decision: PlannerDecision = await self._invoke_planner_llm(
            prompt=prompt,
            structured_output=PlannerDecision
        )

        self.logger.info(
            f"Planner decision generated: domain={decision.identified_domain}, "
            f"strategy={decision.approach_strategy}"
        )
        return {"planner_decision": decision.model_dump()}
