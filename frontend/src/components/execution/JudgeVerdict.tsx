"use client";
import React from "react";
import { JudgeVerdict as JudgeVerdictType } from "@/lib/types";
import { Gavel, CheckCircle2, XCircle, BarChart3 } from "lucide-react";
import { Progress } from "@/components/ui/Progress";
import { cn } from "@/lib/utils";

interface JudgeVerdictProps {
  verdict: JudgeVerdictType | null;
}

export function JudgeVerdict({ verdict }: JudgeVerdictProps) {
  if (!verdict) {
    return (
      <div className="flex items-center justify-center h-full text-[var(--text-muted)]">
        Awaiting final judgment...
      </div>
    );
  }

  // Mock sub-scores
  const scores = [
    { label: "Factual Consistency", val: verdict.score * 100 },
    { label: "Evidence Quality", val: Math.max((verdict.score - 0.1) * 100, 0) },
    { label: "Logical Coherence", val: Math.min((verdict.score + 0.1) * 100, 100) },
    { label: "Citation Accuracy", val: verdict.score * 100 }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8 p-4">
      {/* Hero Section */}
      <div className={cn(
        "relative overflow-hidden rounded-3xl p-8 border",
        verdict.passed 
          ? "bg-emerald-500/10 border-emerald-500/30" 
          : "bg-red-500/10 border-red-500/30"
      )}>
        <div className="absolute top-0 right-0 p-8 opacity-10">
          <Gavel size={120} />
        </div>
        
        <div className="relative z-10 flex flex-col items-center text-center">
          <div className={cn(
            "w-20 h-20 rounded-full flex items-center justify-center mb-6 shadow-2xl",
            verdict.passed ? "bg-emerald-500 text-white" : "bg-red-500 text-white"
          )}>
            {verdict.passed ? <CheckCircle2 size={40} /> : <XCircle size={40} />}
          </div>
          
          <h2 className="text-3xl font-bold text-white mb-2">
            {verdict.passed ? "Consensus Approved" : "Consensus Rejected"}
          </h2>
          <p className={cn(
            "text-lg",
            verdict.passed ? "text-emerald-200" : "text-red-200"
          )}>
            Final Score: {(verdict.score * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Reasoning */}
        <div className="bg-[var(--surface-light)] rounded-2xl p-6 border border-white/5">
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <Gavel size={20} className="text-[var(--accent-secondary)]" />
            Judge's Reasoning
          </h3>
          <div className="prose prose-invert max-w-none">
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap">
              {verdict.reasoning}
            </p>
          </div>
        </div>

        {/* Sub-scores */}
        <div className="bg-[var(--surface-light)] rounded-2xl p-6 border border-white/5">
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-6 flex items-center gap-2">
            <BarChart3 size={20} className="text-[var(--accent-primary)]" />
            Evaluation Metrics
          </h3>
          <div className="space-y-6">
            {scores.map((s, i) => (
              <Progress 
                key={i} 
                value={s.val} 
                label={s.label} 
                color={s.val > 80 ? 'var(--accent-success)' : s.val > 60 ? 'var(--accent-tertiary)' : 'var(--accent-danger)'}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
