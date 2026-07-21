"use client";
import React from "react";
import { AgentRole } from "@/lib/types";
import { UserCog, Wrench } from "lucide-react";

interface RoleAssignmentsProps {
  roles: AgentRole[];
}

export function RoleAssignments({ roles }: RoleAssignmentsProps) {
  if (!roles || roles.length === 0) {
    return <div className="text-[var(--text-muted)] text-sm">No roles assigned yet.</div>;
  }

  return (
    <div className="grid grid-cols-1 gap-4">
      {roles.map((role, i) => (
        <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-4 hover:border-white/20 transition-all animate-in fade-in slide-in-from-bottom-2" style={{ animationDelay: `${i * 100}ms` }}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] flex items-center justify-center shadow-lg">
              <UserCog size={20} className="text-white" />
            </div>
            <div>
              <h4 className="font-semibold text-[var(--text-primary)] text-sm">{role.name}</h4>
              <p className="text-xs text-[var(--text-muted)]">Assigned Expert</p>
            </div>
          </div>
          
          <div className="bg-black/20 rounded-lg p-3 text-xs text-[var(--text-secondary)] leading-relaxed border border-white/5 mb-3">
            {role.description}
          </div>

          <div className="flex items-center gap-1.5 text-xs text-[var(--accent-tertiary)] font-medium">
            <Wrench size={14} /> Available Tools: Search, Document Retrieval, Calculator
          </div>
        </div>
      ))}
    </div>
  );
}
