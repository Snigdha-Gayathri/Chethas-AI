"use client";
import React from "react";
import { Play, TrendingUp, Zap, Target } from "lucide-react";
import { Progress } from "@/components/ui/Progress";

export default function BenchmarksPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text-primary)]">System Benchmarks</h1>
          <p className="text-[var(--text-muted)] mt-2">Evaluate the multi-agent system's performance on standard datasets.</p>
        </div>
        <button className="px-6 py-2 bg-[var(--accent-primary)] text-white font-medium rounded-lg hover:bg-opacity-90 transition-colors shadow-[0_0_15px_rgba(var(--accent-primary-rgb),0.5)] flex items-center gap-2">
          <Play size={18} fill="currentColor" /> Run All Benchmarks
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "Overall Score", value: "86.4", icon: <TrendingUp size={20} className="text-[var(--accent-primary)]" /> },
          { label: "Retrieval Accuracy", value: "92.1", icon: <Target size={20} className="text-[var(--accent-success)]" /> },
          { label: "Avg Latency", value: "1.2s", icon: <Zap size={20} className="text-yellow-400" /> },
          { label: "Hallucination Rate", value: "2.4%", icon: <TrendingUp size={20} className="text-red-400 transform rotate-180" /> },
        ].map((kpi, i) => (
          <div key={i} className="bg-[var(--surface)] border border-white/5 rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-white/5 rounded-lg">{kpi.icon}</div>
              <span className="text-sm font-medium text-[var(--text-secondary)]">{kpi.label}</span>
            </div>
            <div className="text-3xl font-bold text-white mt-4">{kpi.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* NIAH */}
        <div className="bg-[var(--surface)] border border-white/5 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Needle In A Haystack (NIAH)</h3>
          
          <div className="w-full aspect-video bg-black/20 rounded-xl border border-white/5 p-4 flex flex-col">
            <div className="flex justify-between text-xs text-[var(--text-muted)] mb-2">
              <span>Context Length (Tokens)</span>
              <span>100k</span>
            </div>
            {/* Heatmap mock using divs */}
            <div className="flex-1 grid grid-cols-10 gap-1 grid-rows-5">
              {Array.from({ length: 50 }).map((_, i) => {
                const isFail = Math.random() > 0.9;
                const isWarn = !isFail && Math.random() > 0.7;
                return (
                  <div key={i} className={`rounded-sm ${isFail ? 'bg-red-500' : isWarn ? 'bg-yellow-500' : 'bg-emerald-500'}`} />
                )
              })}
            </div>
            <div className="flex justify-between text-xs text-[var(--text-muted)] mt-2">
              <span>Document Depth (0%)</span>
              <span>(100%)</span>
            </div>
          </div>
        </div>

        {/* Long-Context vs RAG */}
        <div className="bg-[var(--surface)] border border-white/5 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Long-Context vs Hybrid RAG</h3>
          
          <div className="space-y-6">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-white">Pure Long-Context</span>
                <span className="text-[var(--text-muted)]">74% accuracy / 14s latency</span>
              </div>
              <Progress value={74} color="var(--accent-tertiary)" />
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-white font-medium">Chethas Hybrid System</span>
                <span className="text-[var(--text-muted)]">92% accuracy / 2s latency</span>
              </div>
              <Progress value={92} color="var(--accent-primary)" />
            </div>
          </div>
        </div>

        {/* Lost in the middle */}
        <div className="bg-[var(--surface)] border border-white/5 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Lost in the Middle Effect</h3>
          
          <div className="w-full h-48 bg-black/20 rounded-xl border border-white/5 p-4 flex items-end justify-between gap-2">
            {[98, 85, 70, 65, 72, 88, 95].map((val, i) => (
              <div key={i} className="w-full relative group">
                <div 
                  className="w-full bg-[var(--accent-primary)]/80 rounded-t-sm transition-all group-hover:bg-[var(--accent-primary)]" 
                  style={{ height: `${val}%` }}
                />
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 text-xs bg-black px-2 py-1 rounded text-white transition-opacity">
                  {val}%
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-[var(--text-muted)] mt-2">
            <span>Beginning</span>
            <span>Middle</span>
            <span>End</span>
          </div>
        </div>

      </div>
    </div>
  );
}
