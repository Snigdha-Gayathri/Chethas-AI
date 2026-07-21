"use client";
import React, { useState } from "react";
import { UploadCloud, File, Trash2, Search, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

export default function DocumentsPage() {
  const [isDragging, setIsDragging] = useState(false);
  const [search, setSearch] = useState("");

  const mockDocs = [
    { id: "1", name: "Q2_Financial_Report.pdf", size: "2.4 MB", status: "indexed", chunks: 145 },
    { id: "2", name: "Market_Analysis_2023.docx", size: "1.1 MB", status: "processing", chunks: 0 },
    { id: "3", name: "User_Interviews.txt", size: "45 KB", status: "indexed", chunks: 12 },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text-primary)]">Knowledge Base</h1>
          <p className="text-[var(--text-muted)] mt-2">Manage documents available to the multi-agent system.</p>
        </div>
      </div>

      {/* Upload Zone */}
      <div 
        className={cn(
          "w-full rounded-2xl border-2 border-dashed transition-all duration-300 flex flex-col items-center justify-center py-16",
          isDragging 
            ? "border-[var(--accent-primary)] bg-[var(--accent-primary)]/10 scale-[1.01]" 
            : "border-white/20 bg-[var(--surface)] hover:border-white/40 hover:bg-white/5"
        )}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => { e.preventDefault(); setIsDragging(false); }}
      >
        <div className="w-16 h-16 rounded-full bg-black/40 flex items-center justify-center mb-4 text-[var(--accent-secondary)]">
          <UploadCloud size={32} />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">Drag & Drop Files Here</h3>
        <p className="text-sm text-[var(--text-muted)] mb-6">Support for PDF, TXT, DOCX, CSV (Max 50MB)</p>
        <button className="px-6 py-2 bg-[var(--accent-primary)] text-white font-medium rounded-lg hover:bg-opacity-90 transition-colors shadow-[0_0_15px_rgba(var(--accent-primary-rgb),0.5)]">
          Browse Files
        </button>
      </div>

      {/* Document List */}
      <div className="bg-[var(--surface)] rounded-2xl border border-white/5 overflow-hidden">
        <div className="p-4 border-b border-white/5 flex items-center gap-4 bg-white/[0.02]">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" size={18} />
            <input 
              type="text"
              placeholder="Search documents..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-black/20 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)] transition-colors"
            />
          </div>
          <div className="text-sm text-[var(--text-muted)] ml-auto">
            {mockDocs.length} Documents
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-black/20 text-[var(--text-muted)] font-medium">
              <tr>
                <th className="px-6 py-4">File Name</th>
                <th className="px-6 py-4">Size</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Chunks</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {mockDocs.map((doc) => (
                <tr key={doc.id} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="px-6 py-4 flex items-center gap-3">
                    <FileText size={16} className="text-[var(--accent-tertiary)]" />
                    <span className="font-medium text-[var(--text-primary)]">{doc.name}</span>
                  </td>
                  <td className="px-6 py-4 text-[var(--text-secondary)]">{doc.size}</td>
                  <td className="px-6 py-4">
                    <span className={cn(
                      "px-2.5 py-1 rounded-full text-xs capitalize font-medium",
                      doc.status === 'indexed' ? "bg-[var(--accent-success)]/20 text-[var(--accent-success)] border border-[var(--accent-success)]/30" :
                      "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                    )}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-[var(--text-secondary)]">{doc.chunks}</td>
                  <td className="px-6 py-4 text-right">
                    <button className="p-2 text-[var(--text-muted)] hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
