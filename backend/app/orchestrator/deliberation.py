from __future__ import annotations
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
    """Run multi-round deliberation between expert agents with active evidence fact-checking."""
    try:
        settings = get_settings()
        max_rounds = settings.max_debate_rounds
        llm = get_llm(temperature=0.4)
        tools = get_tools_by_names(["citation_verify", "evidence_search", "shared_blackboard_read"])
        tool_map = {t.name: t for t in tools if hasattr(t, "name")}
        tool_bound_llm = llm.bind_tools(tools)
        
        expert_findings = state.get("expert_findings", [])
        if len(expert_findings) < 2:
            return {"debate_rounds": [], "current_debate_round": 0, "status": "deliberation_skipped"}
        
        debate_rounds = []
        
        for round_num in range(1, max_rounds + 1):
            logger.info(f"Starting Deliberation Round {round_num} with active tool-based claim checking")
            debate_prompt = f"""You are moderating and rigorously fact-checking Round {round_num} of a multi-agent debate in Chethas.
            
Expert findings so far:
{json.dumps(expert_findings, indent=2)}

Previous debate rounds:
{json.dumps(debate_rounds, indent=2)}

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

            # Run up to 3 tool check iterations per round
            for iteration in range(3):
                response = await tool_bound_llm.ainvoke(messages)
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
                            t_out = await tool_obj.ainvoke(t_args)
                            output_str = str(t_out)
                        except Exception as e:
                            output_str = f"[Tool Error: {e}]"
                    else:
                        output_str = f"[Error: Tool '{t_name}' not found]"
                    messages.append(ToolMessage(content=output_str, tool_call_id=t_id))

            # Final structured extraction for this round
            structured_llm = llm.with_structured_output(DeliberationRound)
            round_result = await structured_llm.ainvoke(messages)
            
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

