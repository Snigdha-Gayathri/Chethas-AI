# Chethas AI (चेतस्)
**Research-Grade Autonomous Multi-Agent Intelligence & Orchestration Platform**

*Chethas (derived from the Sanskrit "Chetas" - चेतस्) represents the mind, cognition, awareness, intelligence, and the faculty of thought. The platform embodies autonomous reasoning, evidence-based decision making, and collaborative multi-agent cognition.*

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.4+-8A2BE2.svg?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-16%20(React%2019)-black.svg?style=for-the-badge&logo=next.js&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-FF4B4B.svg?style=for-the-badge)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20DB-008CC1.svg?style=for-the-badge&logo=neo4j&logoColor=white)

---

## 🌟 What is Chethas?

Chethas is **not** a chatbot. It is **not** a simple document Q&A system or a basic Retrieval-Augmented Generation (RAG) wrapper.

Chethas is a **domain-agnostic autonomous multi-agent intelligence platform** designed to solve complex, open-ended real-world problems through rigorous **strategic planning, dynamic task decomposition, role generation, concurrent ReAct tool execution, structured adversarial debate, factual verification, critical self-reflection, and evidence-backed consensus building**.

When provided with a high-level **GOAL**, Chethas orchestrates a specialized team of AI experts that autonomously investigate, challenge each other's assumptions, verify mathematical and factual claims against retrieved evidence, and synthesize an executive-level, citation-verified consensus report.

---

## 🏛️ System Architecture & Workflow

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Frontend (Next.js 16)                                        │
│  Real-Time Phase Viewer · Interactive Timeline · Transparency Inspector · Live SSE Streaming  │
└─────────────────────────────────────────────────▲──────────────────────────────────────────────┘
                                                  │ HTTP REST + SSE Event Stream
┌─────────────────────────────────────────────────┼──────────────────────────────────────────────┐
│                                   Backend (FastAPI)                                            │
│                                                                                                │
│  ┌─────────────────────────────────── LangGraph Pipeline ──────────────────────────────────┐  │
│  │                                                                                           │  │
│  │   START ──► Planner ──► Task Decomposer ──► Role Generator ──► Expert Execution (||)      │  │
│  │               ▲                                                        │                  │  │
│  │               │                                                        ▼                  │  │
│  │           [iterate]                                            Evidence Verification      │  │
│  │               │                                                        │                  │  │
│  │               │                                                        ▼                  │  │
│  │               └─── Judge ◄─── Reflection ◄─── Deliberation (Debate) ───┘                  │  │
│  │                      │                                                                    │  │
│  │                  [finalize]                                                               │  │
│  │                      │                                                                    │  │
│  │                      ▼                                                                    │  │
│  │                  Consensus ──► END                                                        │  │
│  │                                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                │
│  ┌────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────────┐    │
│  │      Tool Registry     │  │ Strategy Router / RAG   │  │   Ingestion & Chunking      │    │
│  │  (ReAct Interceptors)  │  │ (Hybrid/Graph/Semantic) │  │  (FastEmbed + Multi-format) │    │
│  └────────────────────────┘  └─────────────────────────┘  └─────────────────────────────┘    │
└─────────────────────┬──────────────────────────┬──────────────────────────┬────────────────────┘
                      │                          │                          │
              ┌───────▼────────┐         ┌───────▼────────┐         ┌───────▼────────┐
              │  PostgreSQL    │         │    Qdrant      │         │     Neo4j      │
              │ (State Store)  │         │  (Vector DB)   │         │   (Graph DB)   │
              └────────────────┘         └────────────────┘         └────────────────┘
```

### The 8-Phase Deliberation Lifecycle

1. **Strategic Planning (`PlannerAgent`)**: Analyzes the raw goal, identifies the domain, estimates complexity, determines capabilities required, and selects the initial investigation strategy.
2. **Task Decomposition (`TaskDecomposerAgent`)**: Breaks complex goals down into a dependency-mapped Work Breakdown Structure (WBS) with prioritized subtasks (`SubTask`).
3. **Dynamic Role Generation (`RoleGeneratorAgent`)**: Automatically designs custom expert roles (`AgentRole`) tailored precisely to the required subtasks (e.g., *Principal Systems Architect*, *Empirical Performance Analyst*, *Cryptographic Specialist*).
4. **Concurrent ReAct Expert Execution (`DynamicExpertAgent` × N)**: Instantiates multiple specialized agents running concurrently. Each agent executes an autonomous **ReAct (Reason + Act)** tool-use loop to search vector databases, query graph connections, run Python code, and write observations to a shared blackboard.
5. **Evidence Verification (`EvidenceVerifierAgent`)**: Scrutinizes all expert findings, cross-checking citations (`Citation`), detecting hallucination risks, and scoring factual reliability (`VerificationReport`).
6. **Structured Deliberation (`Moderator` / Debate Engine)**: Executes multi-round adversarial debate rounds (`DeliberationRound`). Experts challenge conflicting claims (`DebateChallenge`), defend their positions with fresh citations (`DebateDefense`), and revise confidence scores until convergence ($\ge 0.85$) is reached.
7. **Critical Reflection (`ReflectionAgent`)**: Conducts a meta-analysis on the synthesized findings, identifying unaddressed edge cases, logical gaps, or contradictions (`ReflectionReport`).
8. **Judgement & Consensus (`JudgeAgent` & `ConsensusBuilderAgent`)**: The Judge scores overall investigation confidence. If below threshold ($\le 0.75$), the system loops back to planning with refined constraints (`should_iterate`). Once finalized, the Consensus Builder synthesizes all evidence into a definitive, citation-backed executive report (`ConsensusReport`).

---

## 🛠️ ReAct Agent Tools (`TOOL_REGISTRY`)

Every agent in Chethas is equipped with modular, ReAct-capable tools that bind directly to the LLM (`bind_tools` in `BaseAgent._run_agentic_loop`).

| Tool Name | Capability & Description |
| :--- | :--- |
| `evidence_search` | Searches the hybrid vector/keyword knowledge base (Qdrant with Reciprocal Rank Fusion) for factual evidence chunks. |
| `citation_verify` | Verifies whether a specific claim is rigorously supported by retrieved source text, returning exact relevance scores. |
| `graph_query` | Translates questions into Cypher queries to traverse multi-hop entity relationships and dependencies in Neo4j. |
| `python_interpreter` | Executes Python code in a sandboxed subprocess to perform mathematical modeling, statistical analysis, or algorithm verification. |
| `query_rewrite` | Employs Hypothetical Document Embeddings (HyDE) and query decomposition to optimize search recall across tricky phrasing. |
| `shared_blackboard_post` | Posts critical findings, intermediate hypotheses, and verified facts to an inter-agent shared memory scratchpad. |
| `shared_blackboard_read` | Reads findings posted by peer agents from the shared scratchpad, enabling collaborative cross-referencing. |

---

## 📂 Complete Repository Folder Structure

```text
Chethas-AI/
├── backend/                             # Python FastAPI Backend & LangGraph Orchestrator
│   ├── app/
│   │   ├── agents/                      # ReAct Agent Suite & Prompt Engineering
│   │   │   ├── base.py                  # BaseAgent abstract class with ReAct tool loop (_run_agentic_loop)
│   │   │   ├── planner.py               # Strategic Planner agent implementation & fallback logic
│   │   │   ├── task_decomposer.py       # Dependency-aware task breakdown agent
│   │   │   ├── role_generator.py        # Dynamic expert role designer
│   │   │   ├── expert_factory.py        # Dynamic expert instantiation & concurrent execution engine
│   │   │   ├── evidence_verifier.py     # Hallucination detector & citation cross-checker
│   │   │   ├── deliberation.py          # Multi-round adversarial debate moderator
│   │   │   ├── reflection.py            # Meta-analytical self-reflection agent
│   │   │   ├── judge.py                 # Confidence evaluation & iteration controller
│   │   │   ├── consensus_builder.py     # Executive report synthesizer
│   │   │   └── prompts/                 # Modular system prompt builders for all roles
│   │   │       ├── planner.py
│   │   │       ├── task_decomposer.py
│   │   │       ├── role_generator.py
│   │   │       └── evidence_verifier.py
│   │   ├── api/                         # FastAPI REST Endpoints & Streaming Router
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── goals.py             # POST/GET /api/goals (Goal submission & management)
│   │   │   │   ├── executions.py        # POST/GET /api/executions (Triggers background LangGraph workflow)
│   │   │   │   ├── stream.py            # GET /api/executions/{id}/stream (Real-time SSE event broadcaster)
│   │   │   │   ├── documents.py         # POST/GET /api/documents (File upload & indexing)
│   │   │   │   └── evaluations.py       # GET /api/evaluations (Quality metrics & RAGAS scores)
│   │   │   ├── middleware.py            # Request tracing & UUID logging middleware
│   │   │   └── dependencies.py          # Singleton dependency injectors
│   │   ├── context/                     # Intelligent Strategy Routing & RAG Engines
│   │   │   ├── strategy_router.py       # LLM-powered query strategy selector
│   │   │   ├── retrieval.py             # Unified retrieve_evidence() API interface
│   │   │   └── strategies/              # Pluggable retrieval architectures
│   │   │       ├── semantic_rag.py      # Dense vector similarity search
│   │   │       ├── hybrid_retrieval.py  # Dense + Sparse + Reciprocal Rank Fusion (RRF)
│   │   │       ├── graph_retrieval.py   # Knowledge graph traversal (Neo4j)
│   │   │       ├── parent_child.py      # Small-to-large hierarchical chunk retrieval
│   │   │       ├── long_context.py      # Full document injection for high-capacity LLMs
│   │   │       └── query_rewriter.py    # Query transformation & expansion
│   │   ├── orchestrator/                # LangGraph StateGraph Definition & Nodes
│   │   │   ├── graph.py                 # build_chethas_graph() & run_goal() async entrypoint
│   │   │   ├── nodes.py                 # Node execution wrappers emitting live SSE broadcasts
│   │   │   ├── edges.py                 # Conditional edge routing (should_iterate evaluation)
│   │   │   ├── state.py                 # ChethasState TypedDict state schema
│   │   │   └── deliberation.py          # Multi-agent debate convergence algorithm
│   │   ├── tools/                       # Tool Implementations for Agent ReAct Binding
│   │   │   ├── registry.py              # TOOL_REGISTRY & get_tools_by_names()
│   │   │   ├── python_interpreter.py    # Sandboxed Python execution engine
│   │   │   ├── evidence_search.py       # Knowledge base search tool
│   │   │   ├── graph_query.py           # Neo4j graph traversal tool
│   │   │   ├── query_rewrite.py         # HyDE search expansion tool
│   │   │   ├── citation_verify.py       # Factual citation verification tool
│   │   │   └── blackboard.py            # Shared inter-agent memory scratchpad tools
│   │   ├── storage/                     # Database Adapters & Checkpointers
│   │   │   ├── vector_store.py          # Qdrant async collection & vector management
│   │   │   ├── graph_store.py           # Neo4j async driver wrapper with lazy init
│   │   │   └── state_store.py           # PostgreSQL / MemorySaver checkpointer
│   │   ├── ingestion/                   # Document Processing & Embedding Pipeline
│   │   │   ├── pipeline.py              # Multi-step ingestion orchestration
│   │   │   ├── chunking.py              # Adaptive recursive text chunking
│   │   │   ├── embeddings.py            # FastEmbed / deterministic hash embeddings
│   │   │   └── processors/              # Format extractors (PDF, Markdown, Code, Web)
│   │   ├── evaluation/                  # Automated Quality Benchmarking Engine
│   │   │   ├── metrics.py               # Token budgeting, latency, and inter-agent agreement
│   │   │   ├── ragas_eval.py            # RAGAS faithfulness & answer relevancy scoring
│   │   │   ├── deepeval_eval.py         # DeepEval evaluation suite integration
│   │   │   └── benchmarks/              # Needle-in-a-Haystack & noise injection benchmarks
│   │   ├── llm/                         # LLM Provider Abstraction
│   │   │   └── provider.py              # LangChain ChatGoogleGenerativeAI / ChatOpenAI factory
│   │   ├── models/                      # Pydantic Schemas & Data Contracts
│   │   │   ├── agent.py                 # AgentRole, SubTask, AgentFinding, PlannerDecision
│   │   │   ├── deliberation.py          # DebateRound, ReflectionReport, JudgeVerdict, ConsensusReport
│   │   │   ├── evidence.py              # Evidence, Citation, RetrievalResult
│   │   │   ├── execution.py             # Execution, ExecutionCreate, ExecutionSummary
│   │   │   └── goal.py                  # Goal, GoalCreate
│   │   ├── config.py                    # Application Settings via pydantic-settings
│   │   └── main.py                      # FastAPI Application Lifespan & CORS Middleware Setup
│   ├── tests/
│   │   └── test_smoke.py                # End-to-end integration verification tests
│   ├── pyproject.toml                   # Python dependencies & build definitions
│   └── .env                             # Local configuration file with API keys
├── frontend/                            # Next.js 16 / React 19 Frontend Dashboard
│   ├── src/
│   │   ├── app/                         # Next.js App Router Pages
│   │   │   ├── page.tsx                 # Hero landing page & Goal submission interface
│   │   │   ├── layout.tsx               # Global application layout & theme styling
│   │   │   ├── execution/[id]/          # Dynamic execution dashboard with live sync
│   │   │   │   └── page.tsx             # Main dashboard controller with SSE listeners
│   │   │   ├── history/                 # Execution archive & past investigation browser
│   │   │   ├── documents/               # Knowledge base file management dashboard
│   │   │   └── benchmarks/              # RAGAS quality benchmarks & metrics display
│   │   ├── components/
│   │   │   ├── execution/               # Active Investigation Visualizers
│   │   │   │   ├── ExecutionTimeline.tsx # Interactive 8-phase timeline selector
│   │   │   │   ├── AgentCard.tsx        # Dynamic expert finding card with tool chips
│   │   │   │   ├── DebateView.tsx       # Multi-round adversarial debate visualizer
│   │   │   │   ├── EvidencePanel.tsx    # Citation & retrieved chunk inspector
│   │   │   │   ├── ReflectionView.tsx   # Meta-analytical reflection report viewer
│   │   │   │   ├── JudgeVerdict.tsx     # Judge confidence breakdown & verdict card
│   │   │   │   ├── ConsensusReport.tsx  # Executive consensus report presentation
│   │   │   │   └── ContextStrategyBadge.tsx # Active RAG strategy indicator badge
│   │   │   ├── transparency/            # Transparency Inspector Right-Panel Tabs
│   │   │   │   ├── PlannerDecisions.tsx # Strategic planning decisions tab
│   │   │   │   ├── TaskBreakdown.tsx    # WBS task dependency breakdown tab
│   │   │   │   ├── RoleAssignments.tsx  # Assigned dynamic expert roles tab
│   │   │   │   ├── ToolInvocations.tsx  # ReAct tool execution audit log tab
│   │   │   │   └── MetricsPanel.tsx     # Token usage & performance metrics tab
│   │   │   └── ui/                      # Reusable Design System Components
│   │   │       ├── Badge.tsx, Button.tsx, Card.tsx, Modal.tsx, Progress.tsx, Tooltip.tsx
│   │   ├── hooks/
│   │   │   └── useSSE.ts                # Custom hook for Server-Sent Events management
│   │   ├── lib/                         # Client Utilities & API Client
│   │   │   ├── api.ts                   # Typed ChethasAPI REST & SSE wrapper
│   │   │   ├── types.ts                 # TypeScript interfaces mirroring backend Pydantic schemas
│   │   │   └── utils.ts                 # Tailwind class merger (cn) & helper utilities
│   │   └── stores/
│   │       └── executionStore.tsx       # React Context provider & reducer for live state
│   ├── package.json                     # Frontend dependencies & scripts
│   └── tsconfig.json                    # TypeScript configuration
├── docker-compose.yml                   # Container orchestration (Qdrant + Neo4j + Postgres + App)
└── README.md                            # Comprehensive project documentation
```

---

## ⚡ Real-Time Transparency Dashboard & Live Sync

Chethas guarantees **zero black-box reasoning**. Every decision made by the orchestrator is emitted via **Server-Sent Events (SSE)** directly to the live dashboard (`http://localhost:3000`).

As the LangGraph graph executes in the background, the dashboard dynamically updates across three rich visual panes:
1. **Left Pane (Execution Timeline)**: An interactive 8-phase step progress bar showing exact status (`pending`, `running`, `completed`) and allowing instant navigation between phase details.
2. **Center Pane (Active Phase View)**: Renders live outputs for the currently active phase:
   - *Planning/Tasks/Roles*: Displays real-time decision logs and WBS structures.
   - *Expert Analysis*: Displays `AgentCard`s for each dynamic expert showing their finding summary, confidence score, and chips indicating exact tools used (e.g., `[Search_Web]`, `[Execute_Code]`).
   - *Deliberation*: Displays round-by-round arguments, adversarial challenges, defenses, and the mathematical convergence curve (`DebateView`).
   - *Judgment & Consensus*: Displays the Judge's multi-criteria scoring scorecard (`JudgeVerdict`) and the final executive consensus report (`ConsensusReport`).
3. **Right Pane (Transparency Inspector)**: A 5-tab inspector panel detailing:
   - `PLAN`: Strategic approach and capability allocation.
   - `TASK`: Work Breakdown Structure (`SubTask` dependencies).
   - `ROLE`: Assigned expert roles and tool boundaries.
   - `TOOL`: Audit log of exact ReAct tool calls and arguments.
   - `METR`: Token budgets, latency, and RAGAS benchmark indicators.

---

## 🚀 Getting Started & Local Installation

### Prerequisites
- **Python**: 3.11 or 3.12+
- **Node.js**: 18+ or 20+
- **npm**: 9+

### 1. Clone & Configure Environment

```bash
git clone https://github.com/Snigdha-Gayathri/Chethas-AI.git
cd Chethas-AI
```

Create or check `backend/.env`. To enable **live reasoning with Gemini 2.5 Pro / 3.1 Pro**, add your API key:
```env
GOOGLE_API_KEY="AIzaSyYourActualGoogleGeminiApiKeyHere"
DEFAULT_LLM_PROVIDER="gemini"
DEFAULT_MODEL="gemini-2.5-flash"
PLANNER_MODEL="gemini-2.5-pro"
EVALUATION_MODEL="gemini-2.5-flash"
FRONTEND_URL="http://localhost:3000"
```
*(Note: Chethas includes **intelligent simulation fallback resilience**. If `GOOGLE_API_KEY` is left empty or not provided, the entire 8-phase pipeline and dashboard UI continue to operate seamlessly on local development ports using domain-accurate simulation outputs, ensuring zero crashes).*

### 2. Launch Backend API Server (Port 8000)

Open your terminal, navigate to `backend/`, install dependencies, and run `uvicorn`:
```bash
cd backend
pip install -e ".[dev]"   # or pip install fastapi uvicorn pydantic pydantic-settings sse-starlette
python -m uvicorn app.main:app --reload --port 8000
```
- **Backend Server**: `http://localhost:8000`
- **Interactive Swagger API Documentation**: `http://localhost:8000/docs`

### 3. Launch Next.js Frontend Dashboard (Port 3000)

Open a second terminal, navigate to `frontend/`, install packages, and start the development server:
```bash
cd frontend
npm install
npm run dev
```
- **Frontend Dashboard**: `http://localhost:3000`

---

## 🧪 Running Tests & Verification

Chethas includes robust verification suites and smoke tests that validate the multi-agent orchestration graph without external database dependencies:

```bash
cd backend
python -m pytest tests/ -v
```

---

## 🛡️ Graceful Degradation & Resilience

Chethas is engineered to run in any environment with complete reliability:
- **No Qdrant Vector DB Running?** The storage layer falls back gracefully to in-memory/local embeddings without breaking agent execution.
- **No Neo4j Graph DB Running?** Graph query tools return safe advisory notices while hybrid semantic retrieval continues unhindered.
- **No PostgreSQL Database Running?** `StateStore` automatically falls back to LangGraph's local `MemorySaver`, keeping full state persistence across the live execution session.
- **No API Key?** All endpoints and dashboard features run cleanly via intelligent simulation fallback, letting you test and present the full UI immediately.

---

## 📄 License
This project is licensed under the MIT License. Built for the next generation of autonomous multi-agent cognition and evidence-backed AI research.
