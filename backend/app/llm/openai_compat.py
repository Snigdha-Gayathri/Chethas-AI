from __future__ import annotations

from typing import Any, Dict

def create_openai_chat_message(role: str, content: str) -> Dict[str, Any]:
    """
    Helper to format a message in the standard OpenAI format.
    """
    if role not in ("system", "user", "assistant", "tool"):
        raise ValueError("Invalid role provided.")
    
    return {
        "role": role,
        "content": content
    }

def extract_content_from_openai_response(response: Dict[str, Any]) -> str:
    """
    Helper to extract text content from an OpenAI compatible API response.
    """
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise ValueError(f"Invalid response format: {e}")
