'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverEffect?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, padding = 'md', hoverEffect = false, children, ...props }, ref) => {
    const paddingStyles = {
      none: '',
      sm: 'p-3',
      md: 'p-5',
      lg: 'p-8',
    };

    return (
      <div
        ref={ref}
        className={cn(
          "glass-card rounded-xl text-slate-200 transition-all duration-300",
          hoverEffect && "hover:-translate-y-1 hover:shadow-lg",
          paddingStyles[padding],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Card.displayName = 'Card';
