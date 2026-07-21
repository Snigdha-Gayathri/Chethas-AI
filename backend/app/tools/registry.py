from __future__ import annotations

import logging
from typing import Callable, Any
from langchain_core.tools import BaseTool

from .python_interpreter import python_interpreter
from .evidence_search import evidence_search
from .graph_query import graph_query
from .query_rewrite import query_rewrite
from .citation_verify import citation_verify
from .blackboard import shared_blackboard_post, shared_blackboard_read

logger = logging.getLogger(__name__)

TOOL_REGISTRY: dict[str, BaseTool | Callable] = {
    "python_interpreter": python_interpreter,
    "evidence_search": evidence_search,
    "graph_query": graph_query,
    "query_rewrite": query_rewrite,
    "citation_verify": citation_verify,
    "shared_blackboard_post": shared_blackboard_post,
    "shared_blackboard_read": shared_blackboard_read,
}

def get_tools_by_names(names: list[str]) -> list[BaseTool | Callable]:
    """Retrieve LangChain tool objects by their string registry names."""
    tools = []
    for name in names:
        tool = TOOL_REGISTRY.get(name)
        if tool:
            tools.append(tool)
        else:
            logger.warning(f"Requested tool '{name}' not found in TOOL_REGISTRY.")
    return tools

def get_all_tools() -> list[BaseTool | Callable]:
    """Return all registered sharp tools."""
    return list(TOOL_REGISTRY.values())
