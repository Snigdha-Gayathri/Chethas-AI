"use client";
import React from "react";
import { cn } from "@/lib/utils";
import { ListTree, PlayCircle, CheckCircle2 } from "lucide-react";

export function TaskBreakdown() {
  // Mock data since we don't have exact types for this yet
  const tasks = [
    { id: 1, title: "Information Retrieval", status: "completed", priority: 1, expertise: "Researcher" },
    { id: 2, title: "Fact Verification", status: "completed", priority: 2, expertise: "Fact Checker" },
    { id: 3, title: "Synthesis", status: "running", priority: 3, expertise: "Analyst" },
    { id: 4, title: "Final Review", status: "pending", priority: 4, expertise: "Judge" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
          <ListTree size={16} className="text-[var(--accent-secondary)]" />
          Execution Graph
        </h4>
      </div>

      <div className="relative border-l border-white/10 ml-3 space-y-6">
        {tasks.map((task) => {
          const isCompleted = task.status === 'completed';
          const isRunning = task.status === 'running';

          return (
            <div key={task.id} className="relative pl-6">
              {/* Node indicator */}
              <div className={cn(
                "absolute -left-[9px] top-1 w-4 h-4 rounded-full flex items-center justify-center bg-[var(--surface-light)]",
                isCompleted ? "text-[var(--accent-success)]" : isRunning ? "text-[var(--accent-primary)] animate-pulse" : "text-white/20"
              )}>
                {isCompleted ? <CheckCircle2 size={16} /> : isRunning ? <PlayCircle size={16} /> : <div className="w-2 h-2 rounded-full bg-white/20" />}
              </div>

              <div className={cn(
                "p-3 rounded-xl border transition-colors",
                isRunning ? "bg-[var(--accent-primary)]/10 border-[var(--accent-primary)]/30" : "bg-white/5 border-white/10"
              )}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm text-[var(--text-primary)]">{task.title}</span>
                  <span className="text-[10px] uppercase font-bold text-[var(--text-muted)] bg-black/40 px-1.5 py-0.5 rounded">
                    P{task.priority}
                  </span>
                </div>
                <div className="flex gap-2 text-xs">
                  <span className="px-2 py-1 rounded bg-white/5 text-[var(--text-secondary)]">
                    Requires: {task.expertise}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
