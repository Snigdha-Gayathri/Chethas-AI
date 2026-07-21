"use client";
import React from "react";
import { DeliberationRound } from "@/lib/types";
import { cn } from "@/lib/utils";
import { MessageSquare, Shield, AlertTriangle, User } from "lucide-react";
import { Progress } from "@/components/ui/Progress";

interface DebateViewProps {
  rounds: DeliberationRound[];
}

export function DebateView({ rounds }: DebateViewProps) {
  if (!rounds || rounds.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-[var(--text-muted)] space-y-4 p-8">
        <MessageSquare size={48} className="opacity-20" />
        <p>No deliberation data available yet.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 p-4">
      {rounds.map((round, idx) => (
        <div key={round.id || idx} className="bg-black/20 rounded-2xl p-6 border border-white/5 animate-in slide-in-from-bottom-4 duration-500">
          <div className="flex items-center justify-between mb-6 border-b border-white/10 pb-4">
            <div>
              <h3 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2">
                <MessageSquare size={20} className="text-[var(--accent-tertiary)]" />
                Round {idx + 1}
              </h3>
              <p className="text-sm text-[var(--text-muted)] mt-1">{round.topic}</p>
            </div>
            <div className="w-32">
              <Progress value={25 + (idx * 25)} label="Convergence" size="sm" color="var(--accent-primary)" />
            </div>
          </div>

          <div className="space-y-6">
            {round.findings.map((finding, fIdx) => {
              // Mock different debate actions based on index for UI variety
              const type = fIdx % 3 === 0 ? 'argument' : fIdx % 3 === 1 ? 'challenge' : 'defense';
              
              const typeConfig = {
                argument: { color: "bg-blue-500/10 border-blue-500/20", icon: <User size={16} className="text-blue-400" /> },
                challenge: { color: "bg-red-500/10 border-red-500/20", icon: <AlertTriangle size={16} className="text-red-400" /> },
                defense: { color: "bg-emerald-500/10 border-emerald-500/20", icon: <Shield size={16} className="text-emerald-400" /> }
              };

              return (
                <div key={fIdx} className={cn(
                  "flex gap-4 p-4 rounded-xl border backdrop-blur-md",
                  typeConfig[type].color,
                  fIdx % 2 !== 0 ? "ml-8" : "mr-8"
                )}>
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
                      {typeConfig[type].icon}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-baseline gap-2 mb-2">
                      <span className="font-semibold text-[var(--text-primary)]">{finding.agent}</span>
                      <span className="text-xs text-[var(--text-muted)] uppercase tracking-wider">{type}</span>
                    </div>
                    <div className="text-sm text-[var(--text-secondary)] leading-relaxed">
                      {finding.content}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
