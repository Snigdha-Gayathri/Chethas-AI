"use client";
import React, { useState } from "react";
import { Evidence } from "@/lib/types";
import { FileText, Image as ImageIcon, Table, Code, ExternalLink, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface EvidencePanelProps {
  evidenceList: Evidence[];
}

export function EvidencePanel({ evidenceList }: EvidencePanelProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const filteredEvidence = evidenceList.filter(e => 
    e.content.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full bg-[var(--surface)] border border-white/5 rounded-2xl overflow-hidden">
      <div className="p-4 border-b border-white/5 bg-white/[0.02]">
        <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-3">Evidence Vault</h3>
        <input 
          type="text"
          placeholder="Search evidence..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-black/20 border border-white/10 rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)] transition-colors"
        />
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3">
        {filteredEvidence.length === 0 ? (
          <div className="text-center text-[var(--text-muted)] py-8 text-sm">
            No evidence found.
          </div>
        ) : (
          filteredEvidence.map((ev, i) => {
            const isExpanded = expandedId === ev.id || (ev.id === undefined && expandedId === i.toString());
            const id = ev.id || i.toString();
            
            // Mock modality
            const modality = "text"; 
            
            return (
              <div key={id} className="bg-white/5 border border-white/10 rounded-lg overflow-hidden transition-all hover:border-white/20">
                <div 
                  className="p-3 flex items-center justify-between cursor-pointer bg-white/[0.02]"
                  onClick={() => setExpandedId(isExpanded ? null : id)}
                >
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-white/10 rounded-md text-[var(--text-secondary)]">
                      <FileText size={16} />
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-[var(--text-primary)] line-clamp-1">
                        Source Document {i + 1}
                      </h4>
                      <div className="flex gap-2 mt-0.5 text-xs text-[var(--text-muted)]">
                        <span>{ev.citations?.length || 0} citations</span>
                      </div>
                    </div>
                  </div>
                  <button className="text-[var(--text-muted)] hover:text-white transition-colors">
                    {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>
                </div>
                
                {isExpanded && (
                  <div className="p-4 text-sm text-[var(--text-secondary)] bg-black/20 border-t border-white/5 leading-relaxed">
                    <div className="whitespace-pre-wrap">{ev.content}</div>
                    
                    {ev.citations && ev.citations.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-white/10">
                        <h5 className="text-xs font-semibold text-[var(--text-primary)] mb-2 uppercase">References</h5>
                        <ul className="space-y-1">
                          {ev.citations.map((cit, idx) => (
                            <li key={idx} className="flex items-center gap-1.5 text-xs text-[var(--accent-tertiary)] hover:underline cursor-pointer">
                              <ExternalLink size={12} />
                              Doc {cit.document_id} {cit.page ? `(Page ${cit.page})` : ''}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
