"use client";
import React from "react";
import { PlannerDecision } from "@/lib/types";
import { BrainCircuit, Zap, CheckCircle2 } from "lucide-react";

interface PlannerDecisionsProps {
  decisions: PlannerDecision[];
}

export function PlannerDecisions({ decisions }: PlannerDecisionsProps) {
  if (!decisions || decisions.length === 0) {
    return <div className="text-[var(--text-muted)] text-sm">No planner decisions recorded.</div>;
  }

  return (
    <div className="space-y-4">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <div className="bg-black/20 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 text-xs font-semibold text-[var(--accent-tertiary)] uppercase tracking-wider mb-2">
            <BrainCircuit size={14} /> Domain
          </div>
          <div className="text-white font-medium">Complex Analysis</div>
        </div>
        <div className="bg-black/20 rounded-xl p-4 border border-white/5">
          <div className="flex items-center gap-2 text-xs font-semibold text-[var(--accent-primary)] uppercase tracking-wider mb-2">
            <Zap size={14} /> Complexity
          </div>
          <div className="flex gap-1">
            {[1,2,3,4,5].map(i => (
              <div key={i} className={`h-2 flex-1 rounded-full ${i <= 4 ? 'bg-[var(--accent-primary)]' : 'bg-white/10'}`} />
            ))}
          </div>
        </div>
      </div>

      <h4 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Strategic Decisions</h4>
      
      <div className="space-y-3">
        {decisions.map((dec, i) => (
          <div key={i} className="bg-white/5 rounded-xl border border-white/10 overflow-hidden hover:border-white/20 transition-colors">
            <div className="p-3 bg-white/[0.02] border-b border-white/5 flex items-center gap-2">
              <CheckCircle2 size={16} className="text-[var(--accent-success)]" />
              <span className="font-medium text-sm text-[var(--text-primary)]">{dec.action}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-white/10 text-[var(--text-muted)] ml-auto">
                {dec.phase}
              </span>
            </div>
            <div className="p-3 text-sm text-[var(--text-secondary)] leading-relaxed bg-black/20">
              {dec.reasoning}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
