from __future__ import annotations
from typing import Any
from app.llm.provider import get_llm


def _extract_text(response) -> str:
    """Extract text content from an LLM response (AIMessage or plain string)."""
    if hasattr(response, 'content'):
        return response.content
    return str(response)


class QueryRewriter:
    def __init__(self):
        self.llm = get_llm()

    async def hyde(self, query: str) -> str:
        """Generate hypothetical document embedding query."""
        prompt = f"Please write a passage to answer the question: {query}"
        try:
            response = await self.llm.ainvoke(prompt)
            return _extract_text(response)
        except Exception:
            return query

    async def decompose(self, query: str) -> list[str]:
        """Break complex query into sub-queries."""
        prompt = f"""Decompose the following complex query into a list of simpler sub-queries.
Query: "{query}"
Return each sub-query on a new line."""
        try:
            response = await self.llm.ainvoke(prompt)
            text = _extract_text(response)
            sub_queries = [line.strip() for line in text.split('\n') if line.strip()]
            return sub_queries if sub_queries else [query]
        except Exception:
            return [query]

    async def standalone(self, query: str, history: list[dict[str, str]]) -> str:
        """Resolve pronouns using conversation history."""
        prompt = f"""Given the conversation history and a follow up question, rephrase the follow up question to be a standalone question.
History: {history}
Follow up: {query}
Standalone Question:"""
        try:
            response = await self.llm.ainvoke(prompt)
            return _extract_text(response).strip()
        except Exception:
            return query
