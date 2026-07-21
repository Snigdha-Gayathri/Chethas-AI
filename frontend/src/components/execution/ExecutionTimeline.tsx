"use client";
import React from "react";
import { ExecutionPhase } from "@/lib/types";
import { cn, formatDuration } from "@/lib/utils";
import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react";

interface ExecutionTimelineProps {
  phases: ExecutionPhase[];
  activePhaseId: string | null;
  onPhaseSelect: (phaseId: string) => void;
}

export function ExecutionTimeline({ phases, activePhaseId, onPhaseSelect }: ExecutionTimelineProps) {
  return (
    <div className="relative p-6 bg-[var(--surface)] border border-white/5 rounded-2xl h-full flex flex-col gap-6 overflow-y-auto custom-scrollbar">
      <h3 className="text-lg font-semibold text-[var(--text-primary)] sticky top-0 bg-[var(--surface)] z-10 pb-2">Execution Flow</h3>
      
      <div className="relative flex flex-col gap-4">
        {phases.map((phase, index) => {
          const isActive = activePhaseId === phase.id;
          const isCompleted = phase.status.toLowerCase() === 'completed';
          const isRunning = phase.status.toLowerCase() === 'running';
          const isFailed = phase.status.toLowerCase() === 'failed';
          
          let duration = "";
          if (phase.started_at && phase.completed_at) {
            duration = formatDuration(new Date(phase.completed_at).getTime() - new Date(phase.started_at).getTime());
          }
          
          return (
            <div key={phase.id} className="relative flex gap-4">
              {/* Connecting Line */}
              {index < phases.length - 1 && (
                <div className={cn(
                  "absolute left-4 top-8 bottom-[-16px] w-0.5 -translate-x-1/2",
                  isCompleted ? "bg-[var(--accent-success)]" : "bg-white/10"
                )} />
              )}
              
              {/* Status Icon */}
              <div className="relative z-10 flex-shrink-0 mt-1">
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center bg-[var(--background)]",
                  isCompleted && "text-[var(--accent-success)]",
                  isRunning && "text-[var(--accent-primary)]",
                  isFailed && "text-[var(--accent-danger)]",
                  !isCompleted && !isRunning && !isFailed && "text-[var(--text-muted)]"
                )}>
                  {isCompleted && <CheckCircle2 size={24} />}
                  {isRunning && <Loader2 size={24} className="animate-spin" />}
                  {isFailed && <XCircle size={24} />}
                  {!isCompleted && !isRunning && !isFailed && <Circle size={24} />}
                </div>
              </div>
              
              {/* Phase Card */}
              <div 
                onClick={() => onPhaseSelect(phase.id)}
                className={cn(
                  "flex-1 p-4 rounded-xl cursor-pointer transition-all duration-200 border group backdrop-blur-sm",
                  isActive ? "bg-white/10 border-white/20 shadow-lg" : "bg-white/5 border-white/5 hover:bg-white/[0.07]",
                  isRunning && !isActive && "animate-pulse"
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className={cn(
                      "font-medium transition-colors",
                      isActive ? "text-[var(--text-primary)]" : "text-[var(--text-secondary)] group-hover:text-[var(--text-primary)]"
                    )}>
                      {phase.name}
                    </h4>
                    <p className="text-xs text-[var(--text-muted)] mt-1 capitalize">{phase.status}</p>
                  </div>
                  {duration && (
                    <span className="text-xs text-[var(--text-muted)] bg-white/5 px-2 py-1 rounded-md">
                      {duration}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
