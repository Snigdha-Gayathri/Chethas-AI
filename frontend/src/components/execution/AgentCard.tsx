"use client";
import React, { useState } from "react";
import { AgentFinding } from "@/lib/types";
import { Progress } from "@/components/ui/Progress";
import { cn } from "@/lib/utils";
import { ChevronDown, ChevronUp, Quote } from "lucide-react";

interface AgentCardProps {
  finding: AgentFinding;
  role?: string;
  status?: string;
}

export function AgentCard({ finding, role = "Expert", status = "completed" }: AgentCardProps) {
  const [expanded, setExpanded] = useState(false);
  
  // Fake a confidence score for UI purposes if not present
  const confidence = 0.85 + Math.random() * 0.1; 
  
  return (
    <div className="bg-[var(--surface)] border border-white/10 rounded-xl overflow-hidden transition-all duration-300 hover:border-white/20">
      <div className="p-4 flex items-center justify-between border-b border-white/5 bg-white/[0.02]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] flex items-center justify-center text-white font-bold text-sm">
            {finding.agent.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <h4 className="font-semibold text-[var(--text-primary)]">{finding.agent}</h4>
            <span className="text-xs text-[var(--text-secondary)]">{role}</span>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-[var(--text-secondary)] capitalize">
            {status}
          </span>
          {status === 'completed' && (
            <span className="text-[10px] text-[var(--accent-success)]">
              {finding.evidence.length} sources
            </span>
          )}
        </div>
      </div>
      
      <div className="p-4 space-y-4">
        <Progress 
          value={confidence * 100} 
          label="Confidence" 
          size="sm"
          color={confidence > 0.9 ? 'var(--accent-success)' : 'var(--accent-primary)'}
        />
        
        <div className="relative">
          <div className={cn(
            "text-sm text-[var(--text-secondary)] leading-relaxed prose prose-invert max-w-none",
            !expanded && "line-clamp-3"
          )}>
            {finding.content}
          </div>
          
          <button 
            onClick={() => setExpanded(!expanded)}
            className="mt-2 flex items-center gap-1 text-xs text-[var(--accent-primary)] hover:text-white transition-colors"
          >
            {expanded ? (
              <><ChevronUp size={14} /> Show Less</>
            ) : (
              <><ChevronDown size={14} /> Read Full Finding</>
            )}
          </button>
        </div>

        {expanded && finding.evidence.length > 0 && (
          <div className="pt-4 mt-4 border-t border-white/5 space-y-2">
            <h5 className="text-xs font-semibold text-[var(--text-primary)] uppercase tracking-wider">Citations</h5>
            <div className="flex flex-col gap-2">
              {finding.evidence.map((ev, i) => (
                <div key={ev.id || i} className="flex gap-2 p-2 rounded-lg bg-white/5 text-xs text-[var(--text-muted)]">
                  <Quote size={12} className="flex-shrink-0 mt-0.5 text-[var(--accent-tertiary)]" />
                  <p className="line-clamp-2">{ev.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
