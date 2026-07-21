# Chethas

*Chethas (चेतस्) - Sanskrit for consciousness, intelligence, or mind.*

Chethas is a research-grade autonomous multi-agent intelligence platform. It moves beyond traditional retrieval assistants by providing an autonomous, domain-agnostic platform capable of complex reasoning, collaborative deliberation, and evidence-backed decision-making.

## Architecture

```mermaid
graph TD;
    Client-->API Gateway;
    API Gateway-->Agent Orchestrator;
    Agent Orchestrator-->LangGraph;
    LangGraph-->Planner;
    LangGraph-->Evaluator;
    LangGraph-->Worker Agent;
    Worker Agent-->Tools;
    Worker Agent-->Qdrant[Vector DB];
    Worker Agent-->Neo4j[Graph DB];
    Worker Agent-->PostgreSQL[Relational DB];
```

## Quick Start

1. **Start Infrastructure**:
   ```bash
   docker-compose up -d
   ```
2. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt # Or poetry install/pip install .
   uvicorn app.main:app --reload
   ```
3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Tech Stack
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.4+-blueviolet.svg)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-red.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20DB-blue.svg)

## License
MIT License
