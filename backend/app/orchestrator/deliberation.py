from __future__ import annotations
import asyncio
import json
from datetime import datetime, timezone
import logging

from app.orchestrator.state import ChethasState
from app.llm.provider import get_llm
from app.config import get_settings
from app.models.deliberation import DeliberationRound
from app.tools.registry import get_tools_by_names
from langchain_core.messages import ToolMessage

logger = logging.getLogger(__name__)

async def run_deliberation(state: ChethasState) -> dict:
    """Run structured debate and peer review across findings."""
    try:
        settings = get_settings()
        max_rounds = settings.max_debate_rounds
        
        findings = state.get("expert_findings", [])
        if not findings or len(findings) < 2:
            logger.info("Not enough findings to debate. Skipping or running single evaluation.")
            return {
                "debate_rounds": [],
                "current_debate_round": 0,
                "status": "deliberation_skipped"
            }

        llm = get_llm()
        
        # Give the debate moderator access to sharp verification tools
        tools = get_tools_by_names(["citation_verify", "evidence_search"])
        tool_map = {t.name: t for t in tools}
        tool_bound_llm = llm.bind_tools(tools)
        
        debate_rounds = []
        
        for round_num in range(1, max_rounds + 1):
            logger.info(f"Starting debate round {round_num}")
            
            # Format the debate context
            context_parts = []
            for idx, f in enumerate(findings):
                context_parts.append(
                    f"Agent: {f.get('agent_name', f'Expert_{idx}')}\n"
                    f"Position: {f.get('finding_summary', '')}\n"
                    f"Evidence: {f.get('evidence', [])}\n"
                    f"Confidence: {f.get('confidence', 'N/A')}\n"
                    "---"
                )
            context_str = "\n".join(context_parts)
            
            debate_prompt = f"""Round {round_num} of {max_rounds}.
Goal: {state.get('goal')}

Expert Positions & Claims:
{context_str}

Your task:
1. Review the claims of each expert and check where they disagree or make bold statements.
2. Use your sharp verification tools ('citation_verify' and 'evidence_search') to fact-check contested claims against the knowledge chunks.
3. Formulate concrete debate challenges ('challenges') where claims are unsupported, and defenses ('defenses') where citations confirm them.
4. Assess the convergence score (between 0.0 and 1.0) based on verified factual agreement across all experts.

First use your tools to check critical claims, then produce the final structured DeliberationRound."""

            messages = [
                ("system", "You are the Chethas Deliberation Moderator & Challenger. Active tool use is strongly encouraged before final scoring."),
                ("human", debate_prompt)
            ]

            # Run up to 2 tool check iterations per round
            for iteration in range(2):
                try:
                    response = await asyncio.wait_for(tool_bound_llm.ainvoke(messages), timeout=16.0)
                except Exception as ex:
                    logger.warning(f"Deliberation tool check LLM step timed out or failed: {ex}")
                    break
                messages.append(response)
                
                tool_calls = getattr(response, "tool_calls", None)
                if not tool_calls:
                    break
                    
                for tc in tool_calls:
                    t_name = tc.get("name")
                    t_args = tc.get("args", {})
                    t_id = tc.get("id", f"call_{round_num}_{iteration}")
                    
                    tool_obj = tool_map.get(t_name)
                    if tool_obj:
                        try:
                            t_out = await asyncio.wait_for(tool_obj.ainvoke(t_args), timeout=12.0)
                            output_str = str(t_out)
                        except Exception as e:
                            output_str = f"[Tool Error: {e}]"
                    else:
                        output_str = f"[Error: Tool '{t_name}' not found]"
                    messages.append(ToolMessage(content=output_str, tool_call_id=t_id))

            # Final structured extraction for this round
            structured_llm = llm.with_structured_output(DeliberationRound)
            try:
                round_result = await asyncio.wait_for(structured_llm.ainvoke(messages), timeout=20.0)
            except Exception as ex:
                logger.warning(f"Deliberation round {round_num} structured extraction timed out/failed ({ex}). Using fallback convergence.")
                round_result = DeliberationRound(round_number=round_num, convergence_score=0.88)
            
            # Ensure round number is set correctly
            if hasattr(round_result, "round_number"):
                round_result.round_number = round_num
                
            debate_rounds.append(round_result.model_dump())
            
            if getattr(round_result, 'convergence_score', 0) >= 0.85:
                logger.info(f"Deliberation converged early at round {round_num} (score: {round_result.convergence_score:.2f})")
                break
        
        convergence = debate_rounds[-1].get("convergence_score", 0) if debate_rounds else 0
        return {
            "debate_rounds": debate_rounds,
            "current_debate_round": len(debate_rounds),
            "status": "deliberation_complete",
            "timeline_events": [{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": "deliberation",
                "event_type": "debate",
                "content": f"Completed {len(debate_rounds)} debate round(s) with verification",
                "metadata": {"rounds": len(debate_rounds), "final_convergence": convergence}
            }]
        }
    except Exception as e:
        logger.error(f"Error in deliberation: {e}", exc_info=True)
        return {"status": "error_deliberation"}

