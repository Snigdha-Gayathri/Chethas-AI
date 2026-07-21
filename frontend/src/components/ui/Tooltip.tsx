"use client";
import React, { useState } from "react";
import { cn } from "@/lib/utils";

interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactElement;
  className?: string;
}

export function Tooltip({ content, children, className }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div 
      className="relative inline-flex"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div className={cn(
          "absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2",
          "bg-[var(--surface-light)] border border-white/10 rounded-lg shadow-xl backdrop-blur-xl",
          "text-sm text-[var(--text-primary)] whitespace-nowrap z-50",
          "animate-in fade-in zoom-in-95 duration-200",
          className
        )}>
          {content}
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-[var(--surface-light)]" />
        </div>
      )}
    </div>
  );
}
