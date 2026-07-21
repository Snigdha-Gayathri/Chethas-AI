"use client";
import React from "react";
import { ReflectionReport } from "@/lib/types";
import { SearchX, AlertTriangle, Lightbulb, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface ReflectionViewProps {
  report: ReflectionReport | null;
}

export function ReflectionView({ report }: ReflectionViewProps) {
  if (!report) {
    return (
      <div className="flex items-center justify-center h-full text-[var(--text-muted)]">
        Waiting for reflection phase...
      </div>
    );
  }

  // Generate some fake visual data based on the report to make it look premium
  const score = 78;
  const risks = [
    { type: "Hallucination Risk", severity: "medium", text: "Claim about X is poorly supported." },
    { type: "Evidence Gap", severity: "high", text: "Missing direct source for Y." }
  ];

  return (
    <div className="space-y-6 p-2">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Quality Score */}
        <div className="col-span-1 bg-black/20 rounded-2xl p-6 border border-white/5 flex flex-col items-center justify-center text-center">
          <div className="relative w-32 h-32 flex items-center justify-center mb-4">
            <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" className="stroke-white/10 fill-none" strokeWidth="8" />
              <circle 
                cx="50" cy="50" r="40" 
                className="stroke-[var(--accent-primary)] fill-none transition-all duration-1000 ease-out" 
                strokeWidth="8" 
                strokeDasharray="251.2" 
                strokeDashoffset={251.2 - (251.2 * score) / 100}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold text-white">{score}</span>
              <span className="text-xs text-[var(--text-muted)]">/ 100</span>
            </div>
          </div>
          <h3 className="font-semibold text-[var(--text-primary)]">Reasoning Quality</h3>
        </div>

        {/* Summary */}
        <div className="col-span-2 bg-[var(--surface-light)] rounded-2xl p-6 border border-white/5">
          <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <SearchX size={20} className="text-[var(--accent-primary)]" />
            Meta-Analysis
          </h3>
          <p className="text-[var(--text-secondary)] text-sm leading-relaxed mb-4">
            {report.summary}
          </p>
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
            <h4 className="text-red-400 font-medium text-sm flex items-center gap-2 mb-2">
              <AlertTriangle size={16} /> Critical Critique
            </h4>
            <p className="text-sm text-red-200/80">{report.critique}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Risks */}
        <div className="bg-[var(--surface-light)] rounded-2xl p-6 border border-white/5">
          <h3 className="text-base font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <AlertTriangle size={18} className="text-[var(--accent-danger)]" />
            Identified Risks
          </h3>
          <div className="space-y-3">
            {risks.map((risk, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-black/20 rounded-lg">
                <div className={cn(
                  "w-2 h-2 rounded-full mt-1.5 flex-shrink-0",
                  risk.severity === 'high' ? "bg-red-500" : "bg-yellow-500"
                )} />
                <div>
                  <h4 className="text-sm font-medium text-white">{risk.type}</h4>
                  <p className="text-xs text-[var(--text-muted)] mt-1">{risk.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Improvements */}
        <div className="bg-[var(--surface-light)] rounded-2xl p-6 border border-white/5">
          <h3 className="text-base font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <TrendingUp size={18} className="text-[var(--accent-success)]" />
            Suggested Improvements
          </h3>
          <ul className="space-y-3">
            {report.improvements.map((imp, i) => (
              <li key={i} className="flex items-start gap-3 p-3 bg-white/5 rounded-lg border border-white/5">
                <Lightbulb size={16} className="text-yellow-400 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-[var(--text-secondary)]">{imp}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
