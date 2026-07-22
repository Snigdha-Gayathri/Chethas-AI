"use client";
import React from "react";
import { Execution, ExecutionPhase, StreamEvent } from "@/lib/types";
import { cn, formatDuration } from "@/lib/utils";
import { 
  CheckCircle2, Circle, Loader2, XCircle, Activity, 
  Target, Users, ShieldCheck, Sparkles, ArrowRight,
  Terminal, Award, Layers
} from "lucide-react";
import { Progress } from "@/components/ui/Progress";

interface OverviewPanelProps {
  execution: Execution;
  streamEvents: StreamEvent[];
  onPhaseSelect: (phaseId: string) => void;
}

export function OverviewPanel({ execution, streamEvents, onPhaseSelect }: OverviewPanelProps) {
  const isRunning = execution.status.toLowerCase() === "running" || execution.status.toLowerCase() === "pending";
  const isCompleted = execution.status.toLowerCase() === "completed";
  const isFailed = execution.status.toLowerCase() === "failed";

  // Calculate stats
  const completedPhasesCount = (execution.phases || []).filter(p => p.status.toLowerCase() === "completed").length;
  const totalPhasesCount = (execution.phases || []).length || 8;
  const progressPercent = Math.min(100, Math.round((completedPhasesCount / totalPhasesCount) * 100));

  // Extract latest verdict or consensus
  const consensusEvents = streamEvents.filter(e => (e as any).type === "consensus" || (e as any).event_type === "consensus");
  const verdictEvents = streamEvents.filter(e => (e as any).type === "verdict" || (e as any).event_type === "verdict");
  const findingEvents = streamEvents.filter(e => (e as any).type === "finding" || (e as any).event_type === "finding");
  const debateEvents = streamEvents.filter(e => (e as any).type === "debate" || (e as any).event_type === "debate");

  const latestConsensus = consensusEvents.length > 0 
    ? ((consensusEvents[consensusEvents.length - 1] as any).data || (consensusEvents[consensusEvents.length - 1] as any).metadata) 
    : null;
    
  const latestVerdict = verdictEvents.length > 0 
    ? ((verdictEvents[verdictEvents.length - 1] as any).data || (verdictEvents[verdictEvents.length - 1] as any).metadata) 
    : null;

  const confidenceScore = (execution as any).confidence_score || latestVerdict?.confidence || latestConsensus?.confidence || 0;

  // Latest events for terminal view
  const recentEvents = [...streamEvents].reverse().slice(0, 12);

  return (
    <div className="space-y-6 pb-8 animate-in fade-in duration-300">
      {/* Top Banner: Goal Summary & Health Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div className="lg:col-span-8 bg-gradient-to-br from-white/[0.07] to-white/[0.02] border border-white/10 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between">
          <div className="absolute -right-10 -bottom-10 w-48 h-48 bg-[var(--accent-primary)]/10 rounded-full blur-3xl pointer-events-none" />
          
          <div>
            <div className="flex items-center justify-between gap-3 mb-3 flex-wrap">
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 bg-[var(--accent-primary)]/20 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30 rounded-full text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5">
                  <Target size={14} /> Investigation Goal
                </span>
                <span className={cn(
                  "px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5 border",
                  isRunning && "bg-blue-500/10 text-blue-400 border-blue-500/20",
                  isCompleted && "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
                  isFailed && "bg-red-500/10 text-red-400 border-red-500/20"
                )}>
                  {isRunning && <Loader2 size={12} className="animate-spin" />}
                  {isCompleted && <CheckCircle2 size={12} />}
                  {isFailed && <XCircle size={12} />}
                  {execution.status}
                </span>
              </div>
              <span className="text-xs text-[var(--text-muted)]">ID: {execution.id}</span>
            </div>
            
            <h2 className="text-xl md:text-2xl font-bold text-[var(--text-primary)] leading-snug break-words">
              {(execution as any).goal?.user_input || "Autonomous Multi-Agent ReAct Investigation"}
            </h2>
          </div>

          <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 border-t border-white/10 pt-4">
            <div>
              <div className="text-xs text-[var(--text-muted)] flex items-center gap-1">
                <Layers size={12} /> Phases Done
              </div>
              <div className="text-lg font-bold text-[var(--text-primary)] mt-1">
                {completedPhasesCount} <span className="text-xs font-normal text-[var(--text-muted)]">/ {totalPhasesCount}</span>
              </div>
            </div>
            <div>
              <div className="text-xs text-[var(--text-muted)] flex items-center gap-1">
                <Users size={12} /> Experts Deployed
              </div>
              <div className="text-lg font-bold text-[var(--text-primary)] mt-1">
                {findingEvents.length || (completedPhasesCount >= 3 ? 3 : 0)} <span className="text-xs font-normal text-[var(--text-muted)]">agents</span>
              </div>
            </div>
            <div>
              <div className="text-xs text-[var(--text-muted)] flex items-center gap-1">
                <ShieldCheck size={12} /> Debate Rounds
              </div>
              <div className="text-lg font-bold text-[var(--text-primary)] mt-1">
                {debateEvents.length || (completedPhasesCount >= 5 ? 1 : 0)} <span className="text-xs font-normal text-[var(--text-muted)]">rounds</span>
              </div>
            </div>
            <div>
              <div className="text-xs text-[var(--text-muted)] flex items-center gap-1">
                <Activity size={12} /> Live Events
              </div>
              <div className="text-lg font-bold text-[var(--text-primary)] mt-1">
                {streamEvents.length} <span className="text-xs font-normal text-[var(--text-muted)]">synced</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Health / Confidence Meter Card */}
        <div className="lg:col-span-4 bg-gradient-to-br from-white/[0.05] to-white/[0.01] border border-white/10 rounded-2xl p-6 flex flex-col justify-between relative">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
                <Award size={16} className="text-[var(--accent-success)]" />
                Confidence Rating
              </span>
              <span className="text-xs px-2 py-0.5 bg-white/10 rounded text-[var(--text-secondary)]">
                {confidenceScore > 0 ? "Verified" : "Deliberating"}
              </span>
            </div>

            <div className="flex items-baseline gap-2 mb-3">
              <span className="text-4xl font-extrabold text-[var(--text-primary)]">
                {confidenceScore > 0 ? `${Math.round(confidenceScore * 100)}%` : `${progressPercent}%`}
              </span>
              <span className="text-xs text-[var(--text-muted)]">
                {confidenceScore > 0 ? "verification confidence" : "workflow completion"}
              </span>
            </div>

            <Progress 
              value={confidenceScore > 0 ? confidenceScore * 100 : progressPercent} 
              size="md" 
              color={confidenceScore > 0 ? "var(--accent-success)" : "var(--accent-primary)"} 
            />
          </div>

          <div className="mt-6 pt-4 border-t border-white/5 text-xs text-[var(--text-secondary)] leading-relaxed">
            {confidenceScore > 0 ? (
              <span>Claims rigorously fact-checked via ReAct tool verification and multi-agent debate.</span>
            ) : isRunning ? (
              <span className="flex items-center gap-2 text-[var(--accent-primary)] animate-pulse">
                <Sparkles size={14} /> Active synthesis & verification in progress...
              </span>
            ) : (
              <span>System ready for review. Select any phase below to inspect internal logs.</span>
            )}
          </div>
        </div>
      </div>

      {/* Executive Consensus Spotlight Card (When Available) */}
      {(latestConsensus || latestVerdict) && (
        <div className="bg-gradient-to-r from-[var(--accent-primary)]/15 via-purple-500/10 to-transparent border border-[var(--accent-primary)]/30 rounded-2xl p-6 relative overflow-hidden">
          <div className="flex items-center justify-between gap-4 mb-3 flex-wrap">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="text-[var(--accent-primary)]" size={20} />
              Executive Synthesis & Final Consensus
            </h3>
            <button 
              onClick={() => onPhaseSelect("p8")}
              className="px-4 py-1.5 bg-[var(--accent-primary)] hover:opacity-90 rounded-xl text-xs font-semibold text-white transition-opacity flex items-center gap-1.5"
            >
              View Full Report <ArrowRight size={14} />
            </button>
          </div>
          <p className="text-sm md:text-base text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap">
            {latestConsensus?.executive_summary || latestConsensus?.conclusion || latestVerdict?.winning_conclusion || latestVerdict?.consensus_view || "Consensus report synthesized and verified across panel."}
          </p>
        </div>
      )}

      {/* Interactive Phase Matrix */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-md font-semibold text-[var(--text-primary)] flex items-center gap-2">
            <Layers size={18} className="text-[var(--accent-primary)]" />
            Interactive Workflow Phases
          </h3>
          <span className="text-xs text-[var(--text-muted)]">Click any phase to open detailed live inspector</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {(execution.phases || []).map((phase, idx) => {
            const pStatus = phase.status.toLowerCase();
            const isDone = pStatus === "completed";
            const isAct = pStatus === "running";
            const isErr = pStatus === "failed";
            const phaseId = phase.id || `p${idx + 1}`;

            let duration = "";
            if (phase.started_at && phase.completed_at) {
              duration = formatDuration(new Date(phase.completed_at).getTime() - new Date(phase.started_at).getTime());
            }

            return (
              <div
                key={phaseId}
                onClick={() => onPhaseSelect(phaseId)}
                className={cn(
                  "p-4 rounded-xl border cursor-pointer transition-all duration-200 flex flex-col justify-between relative group overflow-hidden",
                  isDone && "bg-white/[0.04] border-white/10 hover:border-emerald-500/40 hover:bg-white/[0.07]",
                  isAct && "bg-[var(--accent-primary)]/10 border-[var(--accent-primary)]/40 shadow-lg shadow-[var(--accent-primary)]/5 animate-pulse",
                  isErr && "bg-red-500/10 border-red-500/30",
                  !isDone && !isAct && !isErr && "bg-white/[0.02] border-white/5 hover:border-white/20 hover:bg-white/[0.05]"
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold",
                      isDone && "bg-emerald-500/20 text-emerald-400",
                      isAct && "bg-blue-500/20 text-blue-400",
                      isErr && "bg-red-500/20 text-red-400",
                      !isDone && !isAct && !isErr && "bg-white/5 text-[var(--text-muted)]"
                    )}>
                      {idx + 1}
                    </span>
                    <h4 className="font-semibold text-sm text-[var(--text-primary)] group-hover:text-[var(--accent-primary)] transition-colors line-clamp-1">
                      {phase.name}
                    </h4>
                  </div>
                  <div className="flex-shrink-0">
                    {isDone && <CheckCircle2 size={18} className="text-emerald-400" />}
                    {isAct && <Loader2 size={18} className="text-blue-400 animate-spin" />}
                    {isErr && <XCircle size={18} className="text-red-400" />}
                    {!isDone && !isAct && !isErr && <Circle size={18} className="text-white/20" />}
                  </div>
                </div>

                <div className="mt-4 flex items-center justify-between text-xs text-[var(--text-muted)] pt-2 border-t border-white/5">
                  <span className="capitalize">{pStatus}</span>
                  {duration && <span className="bg-white/10 px-2 py-0.5 rounded text-[var(--text-secondary)]">{duration}</span>}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Real-time Activity Terminal / Feed */}
      <div className="bg-black/40 border border-white/10 rounded-2xl p-5 overflow-hidden">
        <div className="flex items-center justify-between mb-4 border-b border-white/10 pb-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-[var(--text-primary)]">
            <Terminal size={16} className="text-[var(--accent-primary)]" />
            Live Agent Activity Terminal
          </div>
          <span className="text-xs text-[var(--text-muted)]">
            Showing latest {recentEvents.length} events
          </span>
        </div>

        <div className="space-y-2.5 max-h-72 overflow-y-auto custom-scrollbar pr-2 font-mono text-xs">
          {recentEvents.length > 0 ? (
            recentEvents.map((ev, idx) => (
              <div key={idx} className="flex items-start gap-3 p-2.5 rounded-lg bg-white/[0.02] border border-white/5 hover:bg-white/[0.05] transition-colors">
                <span className="text-[var(--text-muted)] flex-shrink-0 select-none">
                  {(ev as any).timestamp ? new Date((ev as any).timestamp).toLocaleTimeString() : "--:--"}
                </span>
                <span className={cn(
                  "px-2 py-0.5 rounded uppercase text-[10px] font-semibold flex-shrink-0",
                  (ev as any).event_type === "completed" || (ev as any).event_type === "verdict" || (ev as any).event_type === "consensus" ? "bg-emerald-500/20 text-emerald-400" :
                  (ev as any).event_type === "error" ? "bg-red-500/20 text-red-400" :
                  (ev as any).event_type === "decision" || (ev as any).event_type === "finding" ? "bg-blue-500/20 text-blue-400" :
                  "bg-white/10 text-white"
                )}>
                  {(ev as any).event_type || (ev as any).type}
                </span>
                <span className="font-semibold text-[var(--accent-primary)] flex-shrink-0">
                  [{(ev as any).agent_name || "System"}]
                </span>
                <span className="text-[var(--text-secondary)] break-words flex-1">
                  {(ev as any).content || (ev as any).message}
                </span>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-[var(--text-muted)] font-sans">
              Waiting for real-time agent telemetry stream...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
