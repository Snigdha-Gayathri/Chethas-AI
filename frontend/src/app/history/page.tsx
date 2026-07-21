"use client";
import React, { useState } from "react";
import { Search, Calendar, Target, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

export default function HistoryPage() {
  const [search, setSearch] = useState("");

  const executions = [
    { id: "exec-1a2b", goal: "Analyze market trends for Q3", status: "completed", date: "2023-10-25T14:30:00Z", confidence: 0.92, domain: "Finance" },
    { id: "exec-3c4d", goal: "Verify claims in the recent climate report", status: "failed", date: "2023-10-24T09:15:00Z", confidence: 0.45, domain: "Science" },
    { id: "exec-5e6f", goal: "Synthesize user feedback for new feature", status: "completed", date: "2023-10-22T16:45:00Z", confidence: 0.88, domain: "Product" },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text-primary)]">Execution History</h1>
          <p className="text-[var(--text-muted)] mt-2">Review past goals, deliberations, and consensus reports.</p>
        </div>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" size={20} />
          <input 
            type="text"
            placeholder="Search by goal..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[var(--surface)] border border-white/10 rounded-xl pl-11 pr-4 py-3 text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)] transition-colors shadow-lg"
          />
        </div>
        <button className="px-6 py-3 bg-[var(--surface)] border border-white/10 rounded-xl text-white hover:bg-white/5 transition-colors flex items-center gap-2">
          <Calendar size={18} /> Filter by Date
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {executions.map((exec) => (
          <Link href={`/execution/${exec.id}`} key={exec.id}>
            <div className="bg-[var(--surface)] border border-white/5 rounded-2xl p-6 hover:border-white/20 hover:bg-white/[0.02] transition-all group cursor-pointer flex items-center gap-6">
              
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className={cn(
                    "px-2.5 py-0.5 rounded-full text-xs capitalize font-medium",
                    exec.status === 'completed' ? "bg-[var(--accent-success)]/20 text-[var(--accent-success)]" : "bg-red-500/20 text-red-400"
                  )}>
                    {exec.status}
                  </span>
                  <span className="text-xs text-[var(--text-muted)] flex items-center gap-1">
                    <Target size={12} /> {exec.domain}
                  </span>
                  <span className="text-xs text-[var(--text-muted)] bg-black/40 px-2 py-0.5 rounded font-mono">
                    {exec.id}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-white group-hover:text-[var(--accent-primary)] transition-colors">
                  {exec.goal}
                </h3>
              </div>

              <div className="text-right">
                <div className="text-2xl font-bold text-white mb-1">
                  {(exec.confidence * 100).toFixed(0)}% <span className="text-sm font-normal text-[var(--text-muted)]">conf</span>
                </div>
                <div className="text-sm text-[var(--text-muted)]">
                  {new Date(exec.date).toLocaleDateString()}
                </div>
              </div>

              <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center text-[var(--text-muted)] group-hover:bg-[var(--accent-primary)] group-hover:text-white transition-colors">
                <ChevronRight size={24} />
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
