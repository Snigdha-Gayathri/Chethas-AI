from __future__ import annotations

import json
from typing import Any, Dict

def structured_output_prompt(instruction: str, schema: Dict[str, Any]) -> str:
    """
    Helper to construct a prompt that asks Gemini to return JSON
    matching a specific JSON schema.
    """
    return (
        f"{instruction}\n\n"
        f"Please provide your response strictly as a JSON object matching the following schema:\n"
        f"{json.dumps(schema, indent=2)}\n\n"
        f"Return ONLY valid JSON."
    )

def construct_multimodal_prompt(text: str, image_urls: list[str]) -> list[Dict[str, Any]]:
    """
    Helper to construct a multimodal prompt for Gemini.
    """
    content = [{"type": "text", "text": text}]
    for url in image_urls:
        content.append({
            "type": "image_url",
            "image_url": {"url": url}
        })
    return content
