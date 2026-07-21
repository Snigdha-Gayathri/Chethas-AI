"use client";
import React from "react";
import { Progress } from "@/components/ui/Progress";

export function MetricsPanel() {
  const metrics = [
    { label: "Faithfulness", value: 92 },
    { label: "Answer Relevancy", value: 88 },
    { label: "Context Precision", value: 85 },
    { label: "Context Recall", value: 79 },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        {metrics.map((m, i) => (
          <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-4 flex flex-col justify-between">
            <span className="text-xs text-[var(--text-secondary)] font-medium mb-3">{m.label}</span>
            <div className="flex items-end justify-between">
              <span className="text-2xl font-bold text-white">{m.value}<span className="text-sm text-[var(--text-muted)]">%</span></span>
            </div>
            <div className="mt-3">
              <Progress 
                value={m.value} 
                size="sm" 
                color={m.value > 90 ? 'var(--accent-success)' : m.value > 80 ? 'var(--accent-primary)' : 'var(--accent-tertiary)'} 
              />
            </div>
          </div>
        ))}
      </div>

      <div className="bg-black/20 rounded-xl p-4 border border-white/5 space-y-4">
        <h4 className="text-sm font-semibold text-[var(--text-primary)]">System Telemetry</h4>
        <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
          <span className="text-[var(--text-muted)]">Latency</span>
          <span className="text-white font-mono">2.4s</span>
        </div>
        <div className="flex justify-between items-center text-sm border-b border-white/5 pb-2">
          <span className="text-[var(--text-muted)]">Token Cost</span>
          <span className="text-white font-mono">~$0.04</span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-[var(--text-muted)]">Hallucination Risk</span>
          <span className="text-[var(--accent-success)] font-mono">Low</span>
        </div>
      </div>
    </div>
  );
}
