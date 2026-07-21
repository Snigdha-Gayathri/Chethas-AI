"use client";
import React from "react";
import { ConsensusReport as ConsensusReportType } from "@/lib/types";
import { FileText, Download, Target, Users } from "lucide-react";
import { Progress } from "@/components/ui/Progress";

interface ConsensusReportProps {
  report: ConsensusReportType | null;
}

export function ConsensusReport({ report }: ConsensusReportProps) {
  if (!report) {
    return (
      <div className="flex items-center justify-center h-full text-[var(--text-muted)]">
        Generating final report...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto pb-12">
      {/* Header Actions */}
      <div className="flex justify-end mb-6">
        <button className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-white transition-colors">
          <Download size={16} />
          Export PDF
        </button>
      </div>

      {/* Main Document */}
      <div className="bg-[var(--surface)] border border-white/10 rounded-3xl overflow-hidden shadow-2xl">
        {/* Cover */}
        <div className="px-10 py-12 bg-gradient-to-br from-indigo-900/40 to-black border-b border-white/10">
          <div className="flex gap-3 mb-6">
            <span className="px-3 py-1 bg-white/10 rounded-full text-xs text-white backdrop-blur-md border border-white/10 flex items-center gap-1.5">
              <Target size={12} /> Final Synthesis
            </span>
            <span className="px-3 py-1 bg-[var(--accent-primary)]/20 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30 rounded-full text-xs backdrop-blur-md flex items-center gap-1.5">
              <Users size={12} /> Multi-Agent Consensus
            </span>
          </div>
          
          <h1 className="text-3xl font-bold text-white mb-6 leading-tight">
            Executive Summary & Findings
          </h1>
          
          <div className="flex items-center gap-6 text-sm text-[var(--text-muted)]">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-white">Confidence Level:</span>
              <div className="w-32">
                <Progress value={report.confidence * 100} size="sm" color="var(--accent-success)" />
              </div>
              <span className="text-white">{(report.confidence * 100).toFixed(0)}%</span>
            </div>
            <div>
              <span className="font-semibold text-white">Sources:</span> {report.supporting_evidence?.length || 0}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-10 space-y-10">
          <section>
            <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
              <FileText size={20} className="text-[var(--accent-primary)]" />
              Conclusion
            </h2>
            <div className="prose prose-invert max-w-none">
              <p className="text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap text-[15px]">
                {report.conclusion}
              </p>
            </div>
          </section>

          {report.supporting_evidence && report.supporting_evidence.length > 0 && (
            <section className="pt-8 border-t border-white/10">
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
                Key Supporting Evidence
              </h2>
              <div className="grid gap-4">
                {report.supporting_evidence.map((ev, i) => (
                  <div key={ev.id || i} className="p-4 bg-white/5 rounded-xl border border-white/5">
                    <p className="text-sm text-[var(--text-secondary)] mb-3">{ev.content}</p>
                    {ev.citations && ev.citations.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {ev.citations.map((c, j) => (
                          <span key={j} className="text-xs px-2 py-1 bg-black/40 rounded-md text-[var(--text-muted)] border border-white/5">
                            Doc: {c.document_id} {c.page ? `p.${c.page}` : ''}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
