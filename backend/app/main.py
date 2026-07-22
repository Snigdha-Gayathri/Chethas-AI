from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.routes import goals, executions, documents, stream, evaluations

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Chethas backend...")
    yield
    logger.info("Shutting down Chethas backend...")

app = FastAPI(
    title="Chethas AI",
    description="Autonomous Multi-Agent Intelligence Platform",
    version="0.1.0",
    lifespan=lifespan
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://chethasai.onrender.com",
        "https://chethas-ai.onrender.com",
    ],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "project": "Chethas AI",
        "description": "Autonomous Multi-Agent Intelligence Platform API is running."
    }

app.include_router(goals.router)
app.include_router(executions.router)
app.include_router(documents.router)
app.include_router(stream.router)
app.include_router(evaluations.router)
