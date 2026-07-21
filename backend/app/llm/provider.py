from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from app.config import get_settings

def get_llm(
    provider: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> BaseChatModel:
    """Factory function returning a LangChain-compatible LLM."""
    settings = get_settings()
    provider = provider or settings.default_llm_provider
    model = model or settings.default_model
    
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.google_api_key,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            api_key=settings.openai_api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

def get_planner_llm() -> BaseChatModel:
    """Returns the LLM configured for planning tasks."""
    settings = get_settings()
    return get_llm(model=settings.planner_model, temperature=0.3)

def get_evaluation_llm() -> BaseChatModel:
    """Returns the LLM configured for evaluation tasks."""
    settings = get_settings()
    return get_llm(model=settings.evaluation_model, temperature=0.0)
