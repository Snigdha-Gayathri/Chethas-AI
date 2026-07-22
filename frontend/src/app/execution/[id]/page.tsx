"use client";
import React, { useState, useEffect } from "react";
import { ExecutionProvider, useExecutionStore } from "@/stores/executionStore";
import { ExecutionTimeline } from "@/components/execution/ExecutionTimeline";
import { AgentCard } from "@/components/execution/AgentCard";
import { EvidencePanel } from "@/components/execution/EvidencePanel";
import { DebateView } from "@/components/execution/DebateView";
import { ReflectionView } from "@/components/execution/ReflectionView";
import { JudgeVerdict } from "@/components/execution/JudgeVerdict";
import { ConsensusReport } from "@/components/execution/ConsensusReport";
import { PlannerDecisions } from "@/components/transparency/PlannerDecisions";
import { TaskBreakdown } from "@/components/transparency/TaskBreakdown";
import { RoleAssignments } from "@/components/transparency/RoleAssignments";
import { ToolInvocations } from "@/components/transparency/ToolInvocations";
import { MetricsPanel } from "@/components/transparency/MetricsPanel";
import { ContextStrategyBadge } from "@/components/execution/ContextStrategyBadge";
import { cn } from "@/lib/utils";
import { Loader2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// The actual page content wrapped in the provider context
function ExecutionDashboard({ id }: { id: string }) {
  const { state, dispatch } = useExecutionStore();
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  
  useEffect(() => {
    let sse: EventSource | null = null;
    let isMounted = true;

    async function loadAndSubscribe() {
      try {
        const res = await fetch(`${API_BASE}/api/executions/${id}`);
        if (!res.ok) {
          throw new Error(`Failed to load execution details (${res.status})`);
        }
        const execData = await res.json();
        if (!isMounted) return;
        dispatch({ type: "SET_EXECUTION", payload: execData });
        dispatch({ type: "SET_ACTIVE_PHASE", payload: "p1" });
        setLoading(false);

        // Connect to SSE for real-time agent updates
        sse = new EventSource(`${API_BASE}/api/executions/${id}/stream`);
        sse.addEventListener("update", (event: any) => {
          if (!isMounted) return;
          try {
            const data = JSON.parse(event.data);
            dispatch({ type: "ADD_EVENT", payload: data });
            
            // Map phase name to phase id
            const phaseMap: Record<string, string> = {
              "planning": "p1",
              "task_decomposition": "p2",
              "role_generation": "p3",
              "expert_analysis": "p4",
              "deliberation": "p5",
              "evidence_verification": "p5",
              "reflection": "p6",
              "judging": "p7",
              "consensus": "p8",
            };
            const phaseId = phaseMap[data.phase];
            if (phaseId) {
              dispatch({ type: "SET_ACTIVE_PHASE", payload: phaseId });
            }
          } catch (e) {
            console.error("Error parsing live SSE event:", e);
          }
        });

      } catch (err: any) {
        if (isMounted) {
          setErrorMessage(err.message || "Failed to load execution data.");
          setLoading(false);
        }
      }
    }

    loadAndSubscribe();
    
    return () => {
      isMounted = false;
      if (sse) sse.close();
    };
  }, [id, dispatch]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-80px)] space-y-4">
        <Loader2 size={48} className="animate-spin text-[var(--accent-primary)]" />
        <p className="text-[var(--text-muted)] animate-pulse">Initializing execution environment...</p>
      </div>
    );
  }

  if (!state.currentExecution) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-[var(--accent-danger)]">
        <AlertCircle size={48} className="mb-4" />
        <p>Execution not found or failed to load.</p>
      </div>
    );
  }

  const activePhaseObj = state.currentExecution.phases.find(p => p.id === state.activePhase);

  // Extract dynamic data from live stream events
  const findingsEvents = state.streamEvents.filter(e => e.event_type === "finding");
  const debateEvents = state.streamEvents.filter(e => e.event_type === "debate");
  const reflectionEvents = state.streamEvents.filter(e => e.event_type === "reflection");
  const verdictEvents = state.streamEvents.filter(e => e.event_type === "verdict");
  const consensusEvents = state.streamEvents.filter(e => e.event_type === "consensus");
  const decisionEvents = state.streamEvents.filter(e => e.event_type === "decision");
  const errorEvents = state.streamEvents.filter(e => e.event_type === "error");

  const plannerDecisions = decisionEvents
    .filter(e => e.phase === "planning")
    .map(e => ({ phase: e.phase, action: e.content, reasoning: JSON.stringify(e.metadata) }));

  const generatedRoles = decisionEvents
    .filter(e => e.phase === "role_generation")
    .flatMap(e => (e.metadata?.roles || []).map((r: string) => ({ name: r, description: `Dynamic expert role: ${r}` })));

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] gap-4 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex items-center justify-between bg-[var(--surface)] p-4 rounded-2xl border border-white/5">
        <div>
          <h1 className="text-xl font-bold text-[var(--text-primary)]">Execution: {id}</h1>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-sm text-[var(--text-muted)]">Status: <span className="text-[var(--accent-primary)] uppercase font-semibold">{state.currentExecution.status}</span></span>
            <ContextStrategyBadge strategy="Dynamic ReAct Tooling" reasoning="Active deliberation, search, and citation verification enabled." />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--accent-primary)] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-[var(--accent-primary)]"></span>
          </span>
          <span className="text-sm font-medium text-[var(--accent-primary)]">Live Sync Active ({state.streamEvents.length} events)</span>
        </div>
      </div>

      {errorEvents.length > 0 && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-sm flex items-center justify-between">
          <span>⚠️ {errorEvents[errorEvents.length - 1].content}</span>
        </div>
      )}

      {/* Main Dashboard Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-0">
        
        {/* Left Column: Timeline (~25%) */}
        <div className="lg:col-span-3 h-full">
          <ExecutionTimeline 
            phases={state.currentExecution.phases} 
            activePhaseId={state.activePhase}
            onPhaseSelect={(id) => dispatch({ type: "SET_ACTIVE_PHASE", payload: id })}
          />
        </div>
        
        {/* Center Column: Active Content (~50%) */}
        <div className="lg:col-span-6 h-full flex flex-col bg-[var(--surface)] border border-white/5 rounded-2xl overflow-hidden">
          <div className="p-4 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              {activePhaseObj?.name || 'Overview'}
            </h2>
            <span className="text-xs text-[var(--text-muted)]">Phase Live View</span>
          </div>
          
          <div className="flex-1 overflow-y-auto custom-scrollbar p-4 relative">
            {activePhaseObj?.name === 'Expert Analysis' && (
              <div className="space-y-4">
                {findingsEvents.length > 0 ? (
                  findingsEvents.map((ev, i) => (
                    <AgentCard key={i} finding={{ agent: ev.agent_name, content: ev.content, evidence: ev.metadata?.tools_used || [] }} role={ev.agent_name} />
                  ))
                ) : (
                  <div className="text-center p-8 text-[var(--text-muted)]">Waiting for expert agent findings...</div>
                )}
              </div>
            )}
            {activePhaseObj?.name === 'Deliberation' && (
              <DebateView rounds={debateEvents.map(e => e.metadata)} />
            )}
            {activePhaseObj?.name === 'Reflection' && (
              <ReflectionView report={reflectionEvents.length > 0 ? { content: reflectionEvents[0].content } : null} />
            )}
            {activePhaseObj?.name === 'Judgment' && (
              <JudgeVerdict verdict={verdictEvents.length > 0 ? verdictEvents[0].metadata : null} />
            )}
            {activePhaseObj?.name === 'Consensus' && (
              <ConsensusReport report={consensusEvents.length > 0 ? consensusEvents[0].metadata : null} />
            )}
            {['Planning', 'Task Decomposition', 'Role Generation'].includes(activePhaseObj?.name || '') && (
               <div className="space-y-4">
                 {state.streamEvents.filter(e => e.phase === activePhaseObj?.name.toLowerCase().replace(' ', '_') || (activePhaseObj?.name === 'Task Decomposition' && e.phase === 'task_decomposition') || (activePhaseObj?.name === 'Role Generation' && e.phase === 'role_generation')).map((ev, i) => (
                   <div key={i} className="bg-black/30 border border-white/10 p-4 rounded-xl text-sm">
                     <div className="font-semibold text-[var(--accent-primary)] mb-1">{ev.agent_name}</div>
                     <div className="text-[var(--text-secondary)]">{ev.content}</div>
                   </div>
                 ))}
                 {state.streamEvents.length === 0 && (
                   <div className="flex items-center justify-center h-40 text-[var(--text-muted)]">
                     Phase initialization in progress... Check right inspector panel for details.
                   </div>
                 )}
               </div>
            )}
          </div>
        </div>
        
        {/* Right Column: Transparency Inspector (~25%) */}
        <div className="lg:col-span-3 h-full flex flex-col bg-[var(--surface)] border border-white/5 rounded-2xl overflow-hidden">
          <div className="flex border-b border-white/5 bg-black/20">
            {['planner', 'tasks', 'roles', 'tools', 'metrics'].map((tab) => (
              <button
                key={tab}
                onClick={() => dispatch({ type: "SET_SELECTED_TAB", payload: tab })}
                className={cn(
                  "flex-1 py-3 text-xs font-medium capitalize transition-colors border-b-2",
                  state.selectedTab === tab 
                    ? "text-[var(--accent-primary)] border-[var(--accent-primary)] bg-white/5" 
                    : "text-[var(--text-muted)] border-transparent hover:text-white hover:bg-white/[0.02]"
                )}
              >
                {tab.substring(0, 4)}
              </button>
            ))}
          </div>
          
          <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
            {state.selectedTab === 'planner' && <PlannerDecisions decisions={plannerDecisions.length > 0 ? plannerDecisions : [{phase: "Init", action: "Analyzing Goal", reasoning: "Awaiting strategy..."}]} />}
            {state.selectedTab === 'tasks' && <TaskBreakdown />}
            {state.selectedTab === 'roles' && <RoleAssignments roles={generatedRoles.length > 0 ? generatedRoles : [{name: "Researcher", description: "Default investigation agent"}]} />}
            {state.selectedTab === 'tools' && <ToolInvocations />}
            {state.selectedTab === 'metrics' && <MetricsPanel />}
          </div>
        </div>

      </div>
    </div>
  );
}

// Next.js page component
export default function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = React.use(params);
  return (
    <ExecutionProvider>
      <ExecutionDashboard id={id} />
    </ExecutionProvider>
  );
}
