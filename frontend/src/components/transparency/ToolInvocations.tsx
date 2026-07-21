"use client";
import React from "react";
import { Terminal, Clock, Check, X } from "lucide-react";

export function ToolInvocations() {
  // Mock data
  const logs = [
    { id: 1, tool: "Search_Web", agent: "Researcher", status: "success", time: "10:24:12 AM", duration: "1.2s" },
    { id: 2, tool: "Read_Document", agent: "Researcher", status: "success", time: "10:24:15 AM", duration: "0.8s" },
    { id: 3, tool: "Execute_Code", agent: "Analyst", status: "error", time: "10:24:20 AM", duration: "3.4s" },
    { id: 4, tool: "Execute_Code", agent: "Analyst", status: "success", time: "10:24:25 AM", duration: "1.1s" },
  ];

  return (
    <div className="space-y-3 font-mono text-xs">
      {logs.map((log) => (
        <div key={log.id} className="bg-black/40 border border-white/10 rounded-lg p-3 group hover:bg-black/60 transition-colors cursor-pointer">
          <div className="flex justify-between items-center mb-2">
            <div className="flex items-center gap-2">
              {log.status === 'success' ? (
                <Check size={14} className="text-[var(--accent-success)]" />
              ) : (
                <X size={14} className="text-[var(--accent-danger)]" />
              )}
              <span className="font-semibold text-white">{log.tool}</span>
            </div>
            <div className="flex items-center gap-2 text-[var(--text-muted)]">
              <Clock size={12} />
              <span>{log.time}</span>
            </div>
          </div>
          
          <div className="flex justify-between text-[var(--text-muted)]">
            <span className="flex items-center gap-1"><Terminal size={12}/> {log.agent}</span>
            <span>{log.duration}</span>
          </div>
        </div>
      ))}
      <div className="text-center pt-2">
        <button className="text-[var(--accent-primary)] hover:underline">View Full Logs</button>
      </div>
    </div>
  );
}
