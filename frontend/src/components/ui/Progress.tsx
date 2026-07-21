"use client";
import React from "react";
import { cn } from "@/lib/utils";

interface ProgressProps {
  value: number;
  max?: number;
  label?: string;
  size?: "sm" | "md" | "lg";
  color?: string;
  className?: string;
}

export function Progress({
  value,
  max = 100,
  label,
  size = "md",
  color = "var(--accent-primary)",
  className
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const sizeClasses = {
    sm: "h-1.5",
    md: "h-2.5",
    lg: "h-4"
  };

  return (
    <div className={cn("w-full flex flex-col gap-1.5", className)}>
      {label && (
        <div className="flex justify-between items-center text-xs text-[var(--text-muted)] font-medium">
          <span>{label}</span>
          <span>{percentage.toFixed(0)}%</span>
        </div>
      )}
      <div className={cn("w-full bg-white/5 rounded-full overflow-hidden backdrop-blur-sm", sizeClasses[size])}>
        <div
          className="h-full rounded-full transition-all duration-1000 ease-out"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}
