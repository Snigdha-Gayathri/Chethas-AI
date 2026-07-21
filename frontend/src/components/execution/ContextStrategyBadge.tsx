"use client";
import React from "react";
import { Tooltip } from "@/components/ui/Tooltip";
import { cn } from "@/lib/utils";
import { Network, Database, Search } from "lucide-react";

interface ContextStrategyBadgeProps {
  strategy: string;
  reasoning: string;
}

export function ContextStrategyBadge({ strategy, reasoning }: ContextStrategyBadgeProps) {
  let icon = <Search size={14} />;
  let colorClass = "bg-blue-500/20 text-blue-300 border-blue-500/30";
  
  const s = strategy.toLowerCase();
  if (s.includes("graph")) {
    icon = <Network size={14} />;
    colorClass = "bg-purple-500/20 text-purple-300 border-purple-500/30";
  } else if (s.includes("hybrid")) {
    icon = <Database size={14} />;
    colorClass = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
  }

  return (
    <Tooltip content={
      <div className="max-w-xs space-y-1">
        <p className="font-semibold text-[var(--text-primary)]">Strategy Reasoning</p>
        <p className="text-sm text-[var(--text-muted)] whitespace-normal">{reasoning}</p>
      </div>
    }>
      <div className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border",
        colorClass
      )}>
        {icon}
        {strategy}
      </div>
    </Tooltip>
  );
}
