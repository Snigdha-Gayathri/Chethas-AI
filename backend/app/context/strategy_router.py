from __future__ import annotations
import time
import json
from typing import Any
from app.llm.provider import get_llm
from .models import RetrievalConfig, StrategyDecision, RetrievalResult
from .strategies import (
    SemanticRagStrategy,
    HybridRetrievalStrategy,
    GraphRetrievalStrategy,
    ParentChildStrategy,
    LongContextStrategy
)
from .strategies.base import BaseStrategy

class StrategyRouter:
    STRATEGIES = [
        "semantic_rag",
        "hybrid_retrieval", 
        "graph_retrieval",
        "parent_child",
        "long_context",
        "multi_stage"
    ]
    
    def __init__(self):
        self._strategies: dict[str, BaseStrategy] = {}
        for name, cls in [
            ("semantic_rag", SemanticRagStrategy),
            ("hybrid_retrieval", HybridRetrievalStrategy),
            ("graph_retrieval", GraphRetrievalStrategy),
            ("parent_child", ParentChildStrategy),
            ("long_context", LongContextStrategy),
        ]:
            try:
                self._strategies[name] = cls()
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Strategy '{name}' unavailable: {e}")
        if not self._strategies:
            self._strategies["hybrid_retrieval"] = HybridRetrievalStrategy()
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = get_llm()
        return self._llm

    async def route(self, config: RetrievalConfig, corpus_stats: dict[str, Any] | None = None) -> StrategyDecision:
        """Select optimal retrieval strategy based on query characteristics."""
        if config.strategy_override and config.strategy_override in self._strategies:
            return StrategyDecision(
                selected_strategy=config.strategy_override,
                reasoning="Strategy explicitly overridden by configuration.",
                alternatives_considered=[],
                confidence=1.0,
                decision_factors={"override": True}
            )

        prompt = f"""You are an expert retrieval strategy router.
Your task is to analyze the user's query and select the most appropriate retrieval strategy from the available options.

Available Strategies:
1. semantic_rag: Good for conceptual queries, finding similar meaning text.
2. hybrid_retrieval: Combines keyword precision with semantic meaning. Good for specific terms, IDs, or general queries.
3. graph_retrieval: Good for queries involving relationships between entities, multi-hop reasoning.
4. parent_child: Good when specific details need broad context.
5. long_context: Good when corpus size is small and full documents can be analyzed.

User Query: "{config.query}"

Corpus Stats: {corpus_stats or 'Unknown'}
Token Budget: {config.token_budget}
Top K: {config.top_k}

Analyze the query type (factual, analytical, comparative, relationship-based).
Consider the corpus statistics and token budget constraints.
Choose one of the strategies. Output your response as a valid JSON object matching this schema:
{{
    "selected_strategy": "string (one of the available strategies)",
    "reasoning": "string (detailed explanation of why this strategy was chosen)",
    "alternatives_considered": ["string", "string"],
    "confidence": float (between 0.0 and 1.0),
    "decision_factors": {{"key": "value"}}
}}
Do not wrap the JSON in markdown blocks, return just the JSON string.
"""
        try:
            response = await self._get_llm().ainvoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            # clean potential markdown
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(response_text)
            
            selected = data.get("selected_strategy")
            if selected not in self._strategies:
                selected = "hybrid_retrieval"
                
            return StrategyDecision(
                selected_strategy=selected,
                reasoning=data.get("reasoning", "Fallback reasoning"),
                alternatives_considered=data.get("alternatives_considered", []),
                confidence=data.get("confidence", 0.5),
                decision_factors=data.get("decision_factors", {})
            )
        except Exception as e:
            # Fallback strategy on failure
            return StrategyDecision(
                selected_strategy="hybrid_retrieval",
                reasoning=f"LLM routing failed ({str(e)}). Falling back to hybrid retrieval.",
                alternatives_considered=[],
                confidence=0.5,
                decision_factors={"error": str(e)}
            )
            
    async def retrieve(self, config: RetrievalConfig) -> RetrievalResult:
        """Route to the best strategy and execute retrieval."""
        start_time = time.time()
        decision = await self.route(config)
        strategy = self._get_strategy(decision.selected_strategy)
        
        # Execute the strategy
        result = await strategy.retrieve(config)
        
        # Augment result with routing info
        result.strategy_used = decision.selected_strategy
        result.strategy_reasoning = decision.reasoning
        
        retrieval_time_ms = int((time.time() - start_time) * 1000)
        result.retrieval_time_ms = retrieval_time_ms
        
        return result
    
    def _get_strategy(self, name: str) -> BaseStrategy:
        return self._strategies.get(name, self._strategies["hybrid_retrieval"])
