# Chethas AI

*Chethas (चेतस्) — Sanskrit for consciousness, intelligence, or mind.*

**Autonomous Multi-Agent Intelligence Platform**

Chethas is a research orchestration system that decomposes complex questions into subtasks, dynamically assembles expert AI agents, and synthesizes high-confidence answers through structured deliberation. Built on LangGraph for stateful multi-agent orchestration with real-time transparency into every reasoning step.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.4+-blueviolet.svg)
![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-red.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20DB-blue.svg)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                            │
│  Real-time execution viewer · Transparency panels · SSE streaming   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTP + SSE
┌────────────────────────────────▼────────────────────────────────────┐
│                      Backend (FastAPI)                               │
│                                                                     │
│  ┌───────────────────── LangGraph Pipeline ──────────────────────┐  │
│  │                                                               │  │
│  │  Planner → TaskDecomposer → RoleGenerator → Experts (||)     │  │
│  │      ↓                                                        │  │
│  │  EvidenceVerifier → Deliberation → Reflection → Judge         │  │
│  │      ↓                          ↑              │              │  │
│  │  Consensus ← ─ ─ finalize ─ ─ ─┘   iterate ──→┘              │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐     │
│  │ Tool System │  │  Context/RAG │  │   Ingestion Pipeline   │     │
│  └─────────────┘  └──────────────┘  └────────────────────────┘     │
└──────────┬──────────────────┬──────────────────────┬────────────────┘
           │                  │                      │
     ┌─────▼─────┐    ┌──────▼──────┐        ┌─────▼─────┐
     │ PostgreSQL │    │   Qdrant    │        │   Neo4j   │
     │  (state)   │    │  (vectors)  │        │  (graph)  │
     └───────────┘    └─────────────┘        └───────────┘
```

---

## Orchestration Pipeline

The core pipeline is a LangGraph `StateGraph` with conditional iteration:

| Phase | Agent | Role |
|-------|-------|------|
| **Planning** | `PlannerAgent` | Identifies domain, selects approach strategy, determines if retrieval is needed |
| **Decomposition** | `TaskDecomposerAgent` | Breaks the goal into 3–7 ordered subtasks with dependencies |
| **Role Generation** | `RoleGeneratorAgent` | Designs 2–5 specialized expert roles with tool assignments |
| **Expert Execution** | `DynamicExpertAgent` (×N) | Experts run concurrently, each with ReAct tool-use loops |
| **Evidence Verification** | `EvidenceVerifierAgent` | Validates citations, detects hallucinations, scores reliability |
| **Deliberation** | Multi-round debate | Structured challenges/defenses between experts, early exit on convergence ≥ 0.85 |
| **Reflection** | `ReflectionAgent` | Meta-analysis detecting gaps, contradictions, and weak arguments |
| **Judging** | `JudgeAgent` | Scores confidence, decides whether to iterate or finalize |
| **Consensus** | `ConsensusBuilderAgent` | Synthesizes all findings into a final cited report |

The Judge can loop back to the Planner (up to `max_iterations`) if confidence is below threshold.

---

## Folder Structure

```
chethas-ai/
├── backend/
│   ├── app/
│   │   ├── agents/              # Agent implementations + prompt templates
│   │   │   ├── base.py             # Abstract BaseAgent (ReAct loop, tool binding)
│   │   │   ├── planner.py          # Strategic planning with higher-reasoning LLM
│   │   │   ├── task_decomposer.py
│   │   │   ├── role_generator.py
│   │   │   ├── expert_factory.py   # Dynamic expert creation from AgentRole specs
│   │   │   ├── evidence_verifier.py
│   │   │   ├── judge.py
│   │   │   ├── reflection.py
│   │   │   ├── consensus_builder.py
│   │   │   └── prompts/            # System prompt templates per agent
│   │   ├── api/                 # FastAPI routes and middleware
│   │   │   ├── routes/
│   │   │   │   ├── executions.py    # Create/list executions (triggers pipeline)
│   │   │   │   ├── stream.py       # SSE broadcast for real-time events
│   │   │   │   ├── goals.py        # Goal CRUD
│   │   │   │   ├── documents.py    # Document upload/management
│   │   │   │   └── evaluations.py
│   │   │   ├── middleware.py       # Request logging with UUID tracing
│   │   │   └── dependencies.py    # Cached store singletons
│   │   ├── context/             # Retrieval and strategy routing
│   │   │   ├── strategy_router.py   # LLM-powered strategy selector
│   │   │   ├── retrieval.py        # High-level retrieve_evidence() API
│   │   │   └── strategies/         # Pluggable retrieval strategies
│   │   │       ├── semantic_rag.py
│   │   │       ├── hybrid_retrieval.py   # Dense + sparse + RRF
│   │   │       ├── graph_retrieval.py    # Neo4j Cypher generation
│   │   │       ├── parent_child.py       # Hierarchical chunk retrieval
│   │   │       ├── long_context.py       # Full document retrieval
│   │   │       └── query_rewriter.py     # HyDE + decomposition
│   │   ├── orchestrator/        # LangGraph pipeline definition
│   │   │   ├── graph.py            # StateGraph construction + run_goal()
│   │   │   ├── nodes.py            # Node functions for each phase
│   │   │   ├── edges.py            # Conditional iteration logic
│   │   │   ├── state.py            # ChethasState TypedDict schema
│   │   │   └── deliberation.py     # Multi-round debate engine
│   │   ├── tools/               # LangChain tools available to agents
│   │   │   ├── registry.py         # TOOL_REGISTRY mapping
│   │   │   ├── evidence_search.py
│   │   │   ├── citation_verify.py
│   │   │   ├── graph_query.py
│   │   │   ├── python_interpreter.py   # Sandboxed code execution
│   │   │   ├── query_rewrite.py
│   │   │   └── blackboard.py       # Inter-agent shared scratchpad
│   │   ├── storage/             # Database adapters
│   │   │   ├── vector_store.py     # Qdrant async wrapper
│   │   │   ├── graph_store.py      # Neo4j async wrapper (lazy init)
│   │   │   └── state_store.py      # PostgreSQL checkpointer
│   │   ├── ingestion/           # Document processing pipeline
│   │   │   ├── pipeline.py         # Route → process → chunk → embed → store
│   │   │   ├── chunking.py         # Adaptive header/size-based splitting
│   │   │   ├── embeddings.py       # fastembed with hash-based fallback
│   │   │   └── processors/         # Per-format extractors (PDF, code, web, etc.)
│   │   ├── evaluation/          # Quality metrics and benchmarks
│   │   │   ├── metrics.py          # Token cost, agreement, evidence coverage
│   │   │   ├── ragas_eval.py       # RAGAS faithfulness/relevancy
│   │   │   ├── deepeval_eval.py    # DeepEval metrics
│   │   │   └── benchmarks/         # NIAH, noise injection, lost-in-middle
│   │   ├── llm/                 # LLM provider abstraction
│   │   │   └── provider.py         # Factory for Gemini / OpenAI models
│   │   ├── models/              # Pydantic schemas
│   │   ├── config.py            # Settings via pydantic-settings
│   │   └── main.py              # FastAPI app entrypoint
│   └── tests/
│       └── test_smoke.py        # Full pipeline smoke test (no API keys)
├── frontend/
│   └── src/
│       ├── app/                 # Next.js pages (App Router)
│       │   ├── page.tsx             # Goal input + suggested questions
│       │   ├── execution/[id]/      # Real-time execution viewer
│       │   ├── history/             # Past executions list
│       │   ├── documents/           # Knowledge base management
│       │   └── benchmarks/          # Performance benchmarks UI
│       ├── components/
│       │   ├── execution/           # AgentCard, Timeline, Debate, Consensus
│       │   ├── transparency/        # Metrics, Planner, Roles, Tasks, Tools
│       │   └── ui/                 # Badge, Button, Card, Modal, Progress, Tooltip
│       ├── hooks/useSSE.ts      # EventSource hook for streaming
│       ├── lib/                 # API client, types, utilities
│       └── stores/              # React Context execution state
├── docker-compose.yml           # Full stack: Qdrant + Neo4j + Postgres + app
├── .env.example                 # Environment variable template
└── PLAN.md                      # Development roadmap
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | LangGraph (StateGraph with conditional edges) |
| Backend | FastAPI, Python 3.12 |
| Frontend | Next.js 15, React 19, Tailwind CSS |
| LLM | Gemini 2.5 Flash/Pro (default), OpenAI-compatible |
| Embeddings | FastEmbed (local) with deterministic hash fallback |
| Vector DB | Qdrant (semantic + hybrid search) |
| Graph DB | Neo4j (entity relationships, multi-hop queries) |
| State | PostgreSQL (LangGraph checkpointing) |
| Streaming | Server-Sent Events (SSE) via sse-starlette |
| Evaluation | RAGAS, DeepEval, custom benchmarks |

---

## Tools Available to Agents

Agents use a ReAct loop and can invoke these tools during execution:

| Tool | Purpose |
|------|---------|
| `evidence_search` | Search vector/hybrid knowledge base |
| `citation_verify` | Verify a claim against retrieved evidence |
| `graph_query` | Query Neo4j for entity relationships |
| `python_interpreter` | Execute Python in a sandboxed subprocess |
| `query_rewrite` | Decompose or rewrite complex queries (HyDE) |
| `shared_blackboard_post` | Post findings to shared inter-agent scratchpad |
| `shared_blackboard_read` | Read other agents' posted findings |

---

## Retrieval Strategies

The Strategy Router uses an LLM to select the optimal retrieval approach per query:

| Strategy | Best For |
|----------|----------|
| `semantic_rag` | Conceptual similarity, meaning-based search |
| `hybrid_retrieval` | Specific terms + semantic meaning (RRF fusion) |
| `graph_retrieval` | Multi-hop relationships, entity connections |
| `parent_child` | Detailed queries needing broader document context |
| `long_context` | Small corpora where full documents fit in context |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional, for databases)

### Quick Start

```bash
# Clone
git clone https://github.com/Snigdha-Gayathri/Chethas-AI.git
cd Chethas-AI

# Backend
cd backend
cp ../.env.example .env          # Add your GOOGLE_API_KEY
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                       # http://localhost:3000
```

### With Docker (full stack)

```bash
cp .env.example .env             # Configure API keys
docker compose up -d
```

This starts: backend (8000), frontend (3000), Qdrant (6333), Neo4j (7687), PostgreSQL (5432).

### Environment Variables

```env
GOOGLE_API_KEY=                  # Required: Gemini API key
DEFAULT_LLM_PROVIDER=gemini      # gemini | openai
DEFAULT_MODEL=gemini-2.5-flash
PLANNER_MODEL=gemini-2.5-pro
QDRANT_URL=http://localhost:6333
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
POSTGRES_URL=postgresql+asyncpg://user:pass@localhost:5432/chethas
```

All external services are optional — the system degrades gracefully without them.

---

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio
python -m pytest tests/ -v
```

The smoke test runs the full pipeline with a mock LLM — no API keys needed.

---

## Graceful Degradation

Chethas runs without any external databases:

- **No Qdrant** → retrieval returns empty results, agents work from LLM knowledge
- **No Neo4j** → graph strategy disabled, other strategies remain available
- **No PostgreSQL** → in-memory checkpointing (state not persisted across restarts)
- **No API key** → tests pass with mock LLM; production requires at least one LLM key

---

## License

MIT
