"use client";
import React, { useEffect } from "react";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  className?: string;
}

export function Modal({ isOpen, onClose, title, children, className }: ModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
        onClick={onClose}
      />
      
      <div className={cn(
        "relative w-full max-w-lg bg-[var(--surface)] border border-white/10 rounded-2xl shadow-2xl overflow-hidden",
        "animate-in fade-in zoom-in-95 duration-200",
        className
      )}>
        <div className="flex items-center justify-between p-6 border-b border-white/5">
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">{title}</h2>
          <button 
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-white/5 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
}
