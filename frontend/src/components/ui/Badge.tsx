'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple';
  size?: 'sm' | 'md';
  pulse?: boolean;
}

export const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', size = 'sm', pulse = false, children, ...props }, ref) => {
    
    const variants = {
      default: "bg-white/10 text-slate-300 border-white/10",
      success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
      warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
      danger: "bg-red-500/10 text-red-400 border-red-500/20",
      info: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
      purple: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    };
    
    const sizes = {
      sm: "px-2 py-0.5 text-xs",
      md: "px-3 py-1 text-sm",
    };

    return (
      <div
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-full border font-medium",
          variants[variant],
          sizes[size],
          pulse && "animate-pulse-glow",
          className
        )}
        {...props}
      >
        {pulse && (
          <span className={cn(
            "mr-1.5 h-1.5 w-1.5 rounded-full",
            variant === 'success' ? 'bg-emerald-400' :
            variant === 'warning' ? 'bg-amber-400' :
            variant === 'danger' ? 'bg-red-400' :
            variant === 'info' ? 'bg-cyan-400' :
            variant === 'purple' ? 'bg-purple-400' :
            'bg-slate-400'
          )} />
        )}
        {children}
      </div>
    );
  }
);
Badge.displayName = 'Badge';
