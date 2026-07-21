from __future__ import annotations

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM
    google_api_key: str = ""
    openai_api_key: Optional[str] = None
    default_llm_provider: str = "gemini"
    default_model: str = "gemini-2.5-flash"
    planner_model: str = "gemini-2.5-pro"
    evaluation_model: str = "gemini-2.5-flash"
    
    # Embedding
    embedding_provider: str = "fastembed"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    
    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "chethas_password"
    
    # PostgreSQL
    database_url: str = "postgresql://chethas:chethas_password@localhost:5432/chethas"
    
    # Agent Config
    max_iterations: int = 3
    confidence_threshold: float = 0.75
    max_debate_rounds: int = 3
    default_token_budget: int = 100000
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

def get_settings() -> Settings:
    return Settings()
