"""End-to-end smoke test: full LangGraph pipeline with a mock LLM."""
from __future__ import annotations
import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ai(text: str) -> AIMessage:
    return AIMessage(content=text)


def _planner_response() -> AIMessage:
    return _ai(json.dumps({
        "identified_domain": "test",
        "approach_strategy": "direct",
        "needs_retrieval": False,
        "retrieval_type_hint": "semantic_rag",
    }))


def _decomposer_response() -> AIMessage:
    return _ai(json.dumps({
        "subtasks": [{"id": "t1", "description": "Subtask 1", "priority": 1, "dependencies": []}],
        "estimated_complexity": "low",
        "parallel_execution_possible": False,
    }))


def _role_response() -> AIMessage:
    return _ai(json.dumps({
        "roles": [{
            "name": "Analyst",
            "expertise": "general",
            "assigned_subtasks": ["t1"],
            "tools": [],
        }]
    }))


def _expert_response() -> AIMessage:
    return _ai(json.dumps({
        "finding_summary": "Test finding",
        "detailed_analysis": "Analysis text",
        "confidence": 0.9,
        "evidence": [],
        "citations": [],
        "reasoning": "Reasoning text",
        "tools_used": [],
    }))


def _verifier_response() -> AIMessage:
    return _ai(json.dumps({
        "verified_claims": [],
        "unverified_claims": [],
        "overall_reliability": 0.9,
        "verification_notes": "",
    }))


def _deliberation_response() -> AIMessage:
    return _ai(json.dumps({
        "convergence_score": 0.9,
        "challenges": [],
        "defenses": [],
        "round_summary": "Converged",
    }))


def _reflection_response() -> AIMessage:
    return _ai(json.dumps({
        "needs_another_iteration": False,
        "quality_score": 0.9,
        "identified_gaps": [],
        "improvement_suggestions": [],
        "overall_assessment": "Good",
    }))


def _judge_response() -> AIMessage:
    return _ai(json.dumps({
        "overall_confidence": 0.9,
        "needs_iteration": False,
        "winning_conclusion": "Test conclusion",
        "dissenting_views": [],
        "key_evidence": [],
    }))


def _consensus_response() -> AIMessage:
    return _ai(json.dumps({
        "executive_summary": "Test summary",
        "detailed_analysis": "Detailed text",
        "key_findings": ["Finding 1"],
        "evidence_citations": [],
        "confidence_score": 0.9,
        "methodology_notes": "",
    }))


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_full_pipeline_smoke():
    """Full graph runs start-to-finish with mock LLM, no API keys needed."""

    responses = [
        _planner_response(),
        _decomposer_response(),
        _role_response(),
        _expert_response(),
        _verifier_response(),
        _deliberation_response(),
        _reflection_response(),
        _judge_response(),
        _consensus_response(),
    ]
    call_index = {"i": 0}

    async def mock_ainvoke(prompt, *args, **kwargs):
        idx = call_index["i"]
        call_index["i"] += 1
        if idx < len(responses):
            return responses[idx]
        return _ai("{}")

    mock_llm = MagicMock()
    mock_llm.ainvoke = mock_ainvoke
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)

    with patch("app.llm.provider.get_llm", return_value=mock_llm), \
         patch("app.llm.provider.get_planner_llm", return_value=mock_llm), \
         patch("app.llm.provider.get_evaluation_llm", return_value=mock_llm), \
         patch("app.storage.vector_store.VectorStore.search_semantic", new_callable=AsyncMock, return_value=[]), \
         patch("app.storage.vector_store.VectorStore.search_hybrid", new_callable=AsyncMock, return_value=[]), \
         patch("app.storage.graph_store.GraphStore.query", new_callable=AsyncMock, return_value=[]), \
         patch("app.orchestrator.nodes.broadcast_event", new_callable=AsyncMock):

        from app.orchestrator.graph import run_goal
        result = await run_goal("What is the capital of France?", execution_id="smoke-test-001")

    assert result.get("status") not in ("error_orchestrator", None), f"Pipeline failed with status: {result.get('status')}"
    assert "consensus" in result or "final_output" in result or result.get("status") == "consensus_built"
