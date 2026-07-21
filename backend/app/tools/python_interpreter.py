from __future__ import annotations

import asyncio
import sys
import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

@tool
async def python_interpreter(code: str, timeout_seconds: int = 10) -> str:
    """Execute Python code in a sandboxed subprocess to compute numbers, test algorithms, analyze data, or verify logic.
    
    Args:
        code: The Python code snippet to execute. Must print or output results to stdout.
        timeout_seconds: Max execution time in seconds (default 10).
    Returns:
        Combined stdout and stderr from the code execution.
    """
    logger.info("Executing Python interpreter tool snippet")
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_seconds)
        
        output = stdout.decode("utf-8", errors="replace")
        error = stderr.decode("utf-8", errors="replace")
        
        result_str = ""
        if output.strip():
            result_str += f"[STDOUT]\n{output.strip()}\n"
        if error.strip():
            result_str += f"[STDERR]\n{error.strip()}\n"
        if not result_str:
            result_str = "[Execution completed with no stdout/stderr. Did you forget to print()?]"
            
        return result_str
    except asyncio.TimeoutError:
        return f"[ERROR] Code execution timed out after {timeout_seconds} seconds."
    except Exception as e:
        return f"[ERROR] Failed to execute code: {e}"
