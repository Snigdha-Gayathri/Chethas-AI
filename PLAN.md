# Plan: Make Chethas a Truly Agentic System

## Goal
Take the existing LangGraph scaffold (which cannot currently run end-to-end) and turn it into a working autonomous multi-agent system where each sub-agent has a sharp, useful role and real capabilities (evidence retrieval), degrading gracefully when the backing databases (Qdrant/Neo4j/Postgres) are absent.

## Current state (verified by reading every core file)
The pipeline is well-designed on paper — planner → task_decomposer → role_generator → experts → evidence_verifier → deliberation → reflection → judge → consensus — but **nothing connects**:
- API is dead: all routers commented out in `main.py`; only `/api/health` works.
- The graph (`run_goal`) is never invoked by any route; `create_execution` just stores a dict; `stream.py` yields fake phases.
- Systemic Pydantic field-name mismatches crash nearly every agent (`PlannerDecision.domain` vs `identified_domain`, `JudgeVerdict.confidence_score` vs `overall_confidence`, `ReflectionReport.needs_iteration` vs `needs_another_iteration`, `AgentFinding.analysis` vs `detailed_analysis`).
- State-key mismatch: experts return `{"findings": ...}`, node reads `expert_findings`, all downstream agents read `findings` → findings never propagate.
- `nodes.py` calls `factory.create_expert` (doesn't exist; it's `create_experts`).
- Object-vs-dict confusion throughout (`.get()`/`.dict()` on the wrong type).
- Retrieval layer (`context/`) is entirely disconnected from agents AND broken internally (`.ainvoke` result treated as str; `VectorStore()`/`GraphStore()` called with no args against required-arg constructors; wrong `search_*` signatures).

## Approach: Full agentic build, graceful degradation

### Phase 1 — Make the pipeline actually execute (correctness)
Fix the data contracts so the graph runs start-to-finish.
1. **Unify state contract**: decide state holds plain dicts (LangGraph-serialization-safe). Every node normalizes agent Pydantic output to dict on the way out, and reads dicts on the way in. Update `state.py` reducers/keys as needed.
2. **Fix the `findings`/`expert_findings` key** across `expert_factory.py`, `nodes.py`, and all consumers (verifier, reflection, judge, consensus, deliberation).
3. **Fix `create_expert` → `create_experts`** and the expert-execution loop in `nodes.py`.
4. **Reconcile every Pydantic field access** with the model definitions (Planner, Judge, Reflection, AgentFinding). Standardize on the model field names; fix the agent/node code that reads them.
5. **Fix `final_output` type** (dict, not str) in consensus.

### Phase 2 — Wire the API to the real graph (make it usable)
6. **Uncomment/register routers** in `main.py`; add `dependencies.py` singletons (settings, optional stores, checkpointer).
7. **`create_execution` runs `run_goal`** as a background task, tracking status in the execution store.
8. **Replace mock `stream.py`** with a real SSE stream driven by LangGraph's `astream`/timeline events, so the frontend sees genuine agent progress.

### Phase 3 — Give sub-agents real capabilities (make it agentic)
9. **Repair the retrieval layer**: fix `.content` on `ainvoke` results; fix `VectorStore`/`GraphStore` construction (build from settings, singletons); fix `search_semantic` signature + add the embedding step; make hybrid do real dense+sparse.
10. **Graceful degradation**: a `RetrievalService` that detects unavailable Qdrant/Neo4j and cleanly returns "no external evidence available" instead of crashing — the LLM-only path still works.
11. **Bind retrieval to experts**: `DynamicExpertAgent` calls the `StrategyRouter` (when `planner_decision.needs_retrieval` / documents present), populates `AgentFinding.evidence` and `evidence_pool`. This is the core "truly agentic" change — experts ground claims in retrieved sources instead of hallucinating.
12. **Make evidence_verifier meaningful**: verify claims against the actual `evidence_pool`, not pure self-assessment.
13. **Real deliberation**: per-expert LLM calls that genuinely challenge/defend, replacing the single model that role-plays all sides.

### Phase 4 — Verify
14. Add a smoke test that runs a goal end-to-end with a fake/echo LLM provider (no API key needed) to prove the graph completes and every node's contract holds.
15. Run existing benchmarks/evaluator if runnable; document what needs live keys/DBs.

## Decisions already confirmed
- **Scope**: full agentic build (both correctness + real capabilities).
- **Databases**: optional/graceful — system runs without Qdrant/Neo4j/Postgres.

## Notes
- The `SmartShelf AI` deletions in `git status` are a separate sibling folder, out of scope.
- I'll keep the existing structure/idioms; this is repair + wiring, not a rewrite.
- Suggested commit grouping: (1) contract fixes, (2) API wiring, (3) retrieval + agent capabilities, (4) tests. No commits without your go-ahead.
