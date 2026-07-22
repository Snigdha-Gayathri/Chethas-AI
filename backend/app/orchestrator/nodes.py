from __future__ import annotations
import asyncio
from datetime import datetime, timezone
import logging

from app.orchestrator.state import ChethasState
from app.agents.planner import PlannerAgent
from app.agents.task_decomposer import TaskDecomposerAgent
from app.agents.role_generator import RoleGeneratorAgent
from app.agents.expert_factory import ExpertAgentFactory, DynamicExpertAgent
from app.agents.evidence_verifier import EvidenceVerifierAgent
from app.agents.reflection import ReflectionAgent
from app.agents.judge import JudgeAgent
from app.agents.consensus_builder import ConsensusBuilderAgent
from app.models.agent import AgentRole
from app.orchestrator.deliberation import run_deliberation
from app.api.routes.stream import broadcast_event

logger = logging.getLogger(__name__)

async def _emit(state: ChethasState, event_type: str, phase: str, agent: str, content: str, meta: dict = None):
    exec_id = state.get("execution_id")
    if exec_id:
        try:
            await broadcast_event(exec_id, event_type, phase, agent, content, meta or {})
            from app.api.routes.executions import update_execution_phase_status
            update_execution_phase_status(exec_id, phase, event_type)
        except Exception as e:
            logger.warning(f"Failed to emit broadcast ({e})")

async def planner_node(state: ChethasState) -> dict:
    """Planning phase: analyze goal and create strategy."""
    try:
        await _emit(state, "status_update", "planning", "Planner", "Analyzing goal and formulating strategy...")
        agent = PlannerAgent()
        result = await agent.execute(state)
        decision = result.get("planner_decision", {})
        
        await _emit(state, "decision", "planning", "Planner", f"Identified domain: {decision.get('identified_domain', 'General')}. Strategy: {decision.get('approach_strategy', '')}", decision)
        
        timeline_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "planning",
            "agent_name": "Planner",
            "event_type": "decision",
            "content": f"Identified domain: {decision.get('identified_domain', 'unknown')}",
            "metadata": decision
        }
        return {**result, "timeline_events": [timeline_event], "status": "planning"}
    except Exception as e:
        logger.error(f"Planner node failed: {e}")
        await _emit(state, "error", "planning", "Planner", f"Planning failed: {e}")
        return {"status": "error_planning", "timeline_events": [{"timestamp": datetime.now(timezone.utc).isoformat(), "phase": "planning", "event_type": "error", "content": str(e)}]}


async def task_decomposition_node(state: ChethasState) -> dict:
    """Decompose goal into subtasks."""
    try:
        await _emit(state, "status_update", "task_decomposition", "TaskDecomposer", "Decomposing goal into concrete subtasks...")
        agent = TaskDecomposerAgent()
        result = await agent.execute(state)
        subtasks = result.get("subtasks", [])
        
        await _emit(state, "decision", "task_decomposition", "TaskDecomposer", f"Decomposed goal into {len(subtasks)} subtasks.", {"num_subtasks": len(subtasks)})
        
        timeline_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "task_decomposition",
            "agent_name": "TaskDecomposer",
            "event_type": "decision",
            "content": f"Decomposed into {len(subtasks)} subtasks",
            "metadata": {"num_subtasks": len(subtasks)}
        }
        return {**result, "timeline_events": [timeline_event], "status": "task_decomposition"}
    except Exception as e:
        logger.error(f"Task decomposition node failed: {e}")
        await _emit(state, "error", "task_decomposition", "TaskDecomposer", f"Decomposition failed: {e}")
        return {"status": "error_task_decomposition"}


async def role_generator_node(state: ChethasState) -> dict:
    """Generate expert roles dynamically."""
    try:
        await _emit(state, "status_update", "role_generation", "RoleGenerator", "Designing custom expert roles for subtasks...")
        agent = RoleGeneratorAgent()
        result = await agent.execute(state)
        roles = result.get("generated_roles", [])
        
        await _emit(state, "decision", "role_generation", "RoleGenerator", f"Generated {len(roles)} specialized expert agents.", {"roles": [r.get("name") for r in roles]})
        
        timeline_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "role_generation",
            "agent_name": "RoleGenerator",
            "event_type": "decision",
            "content": f"Generated {len(roles)} expert roles",
            "metadata": {"num_roles": len(roles)}
        }
        return {**result, "timeline_events": [timeline_event], "status": "role_generation"}
    except Exception as e:
        logger.error(f"Role generation node failed: {e}")
        await _emit(state, "error", "role_generation", "RoleGenerator", f"Role generation failed: {e}")
        return {"status": "error_role_generation"}


async def expert_execution_node(state: ChethasState) -> dict:
    """Execute all expert agents concurrently."""
    try:
        factory = ExpertAgentFactory()
        roles = [AgentRole(**role_dict) for role_dict in state.get("generated_roles", [])]
        
        await _emit(state, "status_update", "expert_analysis", "ExpertTeam", f"Executing {len(roles)} expert agents concurrently with tools...")

        async def _run(role: AgentRole) -> dict:
            await _emit(state, "status_update", "expert_analysis", role.name, f"Expert {role.name} investigating subtasks...")
            expert = factory.create_expert(role)
            try:
                res = await expert.execute(state)
                findings = res.get("expert_findings", [])
                summary = findings[0].get("finding_summary", "") if findings else "Completed analysis"
                await _emit(state, "finding", "expert_analysis", role.name, summary, {"tools_used": role.tools})
                return res
            except Exception as e:
                logger.error(f"Expert {role.name} failed: {e}")
                await _emit(state, "error", "expert_analysis", role.name, f"Expert error: {e}")
                return {"expert_findings": [], "evidence_pool": []}

        results = await asyncio.gather(*[_run(role) for role in roles])

        all_findings = []
        all_evidence = []
        timeline_events = []
        for role, result in zip(roles, results):
            all_findings.extend(result.get("expert_findings", []))
            all_evidence.extend(result.get("evidence_pool", []))
            timeline_events.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phase": "expert_execution",
                "agent_name": role.name,
                "event_type": "finding",
                "content": f"Expert {role.name} completed execution",
                "metadata": {"role": role.name}
            })

        return {
            "expert_findings": all_findings,
            "evidence_pool": all_evidence,
            "timeline_events": timeline_events,
            "status": "expert_analysis"
        }
    except Exception as e:
        logger.error(f"Expert execution node failed: {e}")
        await _emit(state, "error", "expert_analysis", "ExpertTeam", f"Execution failed: {e}")
        return {"status": "error_expert_execution"}


async def evidence_verification_node(state: ChethasState) -> dict:
    """Verify evidence quality."""
    try:
        await _emit(state, "status_update", "deliberation", "EvidenceVerifier", "Verifying claims and checking citations...")
        agent = EvidenceVerifierAgent()
        result = await agent.execute(state)
        await _emit(state, "verification", "deliberation", "EvidenceVerifier", "Evidence verification completed.")
        
        timeline_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "evidence_verification",
            "agent_name": "EvidenceVerifier",
            "event_type": "verification",
            "content": "Evidence verification completed",
            "metadata": {}
        }
        return {**result, "timeline_events": [timeline_event], "status": "evidence_verified"}
    except Exception as e:
        logger.error(f"Evidence verification failed: {e}")
        return {"status": "error_evidence_verification"}


async def deliberation_node(state: ChethasState) -> dict:
    """Run deliberation/debate rounds."""
    try:
        await _emit(state, "status_update", "deliberation", "Moderator", "Running structured multi-agent debate and challenging claims...")
        result = await run_deliberation(state)
        rounds = result.get("debate_rounds", [])
        convergence = rounds[-1].get("convergence_score", 0) if rounds else 0
        await _emit(state, "debate", "deliberation", "Moderator", f"Completed {len(rounds)} debate rounds. Convergence score: {convergence:.2f}", {"rounds": len(rounds), "convergence": convergence})
        return result
    except Exception as e:
        logger.error(f"Deliberation node failed: {e}")
        return {"status": "error_deliberation"}


async def reflection_node(state: ChethasState) -> dict:
    """Reflect on the investigation quality."""
    try:
        await _emit(state, "status_update", "reflection", "Reflection", "Performing critical self-reflection on findings...")
        agent = ReflectionAgent()
        result = await agent.execute(state)
        await _emit(state, "reflection", "reflection", "Reflection", "Reflection completed. Identified potential improvements.")
        
        timeline_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "reflection",
            "agent_name": "Reflection",
            "event_type": "reflection",
            "content": "Reflection completed",
            "metadata": {}
        }
        return {**result, "timeline_events": [timeline_event], "status": "reflection_complete"}
    except Exception as e:
        logger.error(f"Reflection node failed: {e}")
        return {"status": "error_reflection"}


async def judge_node(state: ChethasState) -> dict:
    """Judge the overall quality and decide on iteration."""
    try:
        await _emit(state, "status_update", "judging", "Judge", "Evaluating investigation quality and scoring confidence...")
        agent = JudgeAgent()
        result = await agent.execute(state)
        verdict = result.get("judge_verdict", {})
        confidence = verdict.get("overall_confidence", 0.0)
        
        await _emit(state, "verdict", "judging", "Judge", f"Judgement complete. Overall confidence: {confidence * 100:.1f}%. Conclusion: {verdict.get('winning_conclusion', '')}", {"confidence": confidence})
        
        timeline_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "judging",
            "agent_name": "Judge",
            "event_type": "verdict",
            "content": f"Judgement complete with confidence {confidence}",
            "metadata": {"confidence": confidence}
        }
        
        return {
            **result,
            "confidence_score": confidence,
            "iteration": state.get("iteration", 0) + 1,
            "status": "judging",
            "timeline_events": [timeline_event]
        }
    except Exception as e:
        logger.error(f"Judge node failed: {e}")
        return {"status": "error_judging"}


async def consensus_node(state: ChethasState) -> dict:
    """Build final consensus."""
    try:
        await _emit(state, "status_update", "consensus", "ConsensusBuilder", "Synthesizing executive consensus report and citations...")
        agent = ConsensusBuilderAgent()
        result = await agent.execute(state)
        consensus = result.get("consensus", {})
        summary = consensus.get("executive_summary", "Consensus report generated.")
        
        await _emit(state, "consensus", "consensus", "ConsensusBuilder", f"Consensus synthesized: {summary[:120]}...", consensus)
        
        timeline_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "consensus",
            "agent_name": "ConsensusBuilder",
            "event_type": "consensus",
            "content": "Consensus built",
            "metadata": {}
        }
        return {**result, "timeline_events": [timeline_event], "status": "consensus_built"}
    except Exception as e:
        logger.error(f"Consensus node failed: {e}")
        return {"status": "error_consensus"}

