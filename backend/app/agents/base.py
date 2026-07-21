from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional
import logging
import json
from langchain_core.messages import ToolMessage, HumanMessage, SystemMessage
from app.tools.registry import get_tools_by_names

class BaseAgent(ABC):
    """Base class for all Chethas agents."""
    
    def __init__(self, name: str, role: str, expertise: str, tools: Optional[List[str]] = None):
        self.name = name
        self.role = role
        self.expertise = expertise
        self.tool_names = tools or []
        self.logger = logging.getLogger(f"chethas.agent.{name}")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        ...
    
    @abstractmethod
    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent's task given the current workflow state."""
        ...
    
    def get_tools(self) -> list:
        """Return tools available to this agent based on registry or subclass override."""
        if self.tool_names:
            return get_tools_by_names(self.tool_names)
        return []
    
    async def _run_agentic_loop(self, llm: Any, prompt: str, tools: list, max_iterations: int = 4) -> list:
        """Execute a ReAct tool loop where the agent calls tools, observes outputs, and self-corrects."""
        tool_map = {t.name: t for t in tools if hasattr(t, "name")}
        tool_bound_llm = llm.bind_tools(tools)
        
        system_msg = (
            self.get_system_prompt() + 
            "\n\nYou have access to sharp tools (Python execution, evidence search, graph queries, query rewrite, verification, and blackboard). "
            "Always use your tools to actively search for evidence, verify math/code, and check facts before finalizing your conclusion."
        )
        messages = [
            ("system", system_msg),
            ("human", prompt)
        ]
        
        for iteration in range(max_iterations):
            self.logger.debug(f"Agent '{self.name}' tool loop iteration {iteration + 1}")
            response = await tool_bound_llm.ainvoke(messages)
            messages.append(response)
            
            tool_calls = getattr(response, "tool_calls", None)
            if not tool_calls:
                break
                
            for tc in tool_calls:
                t_name = tc.get("name")
                t_args = tc.get("args", {})
                t_id = tc.get("id", f"call_{iteration}")
                
                self.logger.info(f"Agent '{self.name}' executing tool '{t_name}' with args {t_args}")
                tool_obj = tool_map.get(t_name)
                if tool_obj:
                    try:
                        t_output = await tool_obj.ainvoke(t_args)
                        output_str = str(t_output)
                    except Exception as e:
                        output_str = f"[Tool Error: {e}]"
                else:
                    output_str = f"[Error: Tool '{t_name}' not found]"
                    
                messages.append(ToolMessage(content=output_str, tool_call_id=t_id))
                
        return messages

    async def _invoke_llm(self, prompt: str, structured_output: Optional[Any] = None, max_tool_iterations: int = 4):
        """Invoke the LLM with an active ReAct tool loop (if tools exist) and optional structured output."""
        from app.llm.provider import get_llm
        llm = get_llm()
        tools = self.get_tools()
        
        if tools and len(tools) > 0:
            # Run the agentic tool-use loop first to gather observations and evidence
            try:
                enriched_messages = await self._run_agentic_loop(llm, prompt, tools, max_iterations=max_tool_iterations)
                if structured_output:
                    # Request the structured output given the entire enriched history
                    structured_llm = llm.with_structured_output(structured_output)
                    return await structured_llm.ainvoke(enriched_messages)
                else:
                    # Return final message content if no structured output required
                    return enriched_messages[-1].content if enriched_messages else ""
            except Exception as e:
                self.logger.warning(f"Tool loop encountered issue ({e}). Falling back to direct structured invoke.")
        
        # Standard one-shot structured invocation when no tools assigned or fallback
        if structured_output:
            llm = llm.with_structured_output(structured_output)
        messages = [
            ("system", self.get_system_prompt()),
            ("human", prompt),
        ]
        return await llm.ainvoke(messages)

