import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  const s = ms / 1000;
  if (s < 60) return `${s.toFixed(1)}s`;
  const m = Math.floor(s / 60);
  const remainingS = Math.floor(s % 60);
  return `${m}m ${remainingS}s`;
}

export function getConfidenceColor(score: number): string {
  if (score >= 0.8) return 'var(--accent-success)';
  if (score >= 0.5) return 'var(--accent-tertiary)';
  return 'var(--accent-danger)';
}

export function getStatusColor(status: string): string {
  const s = status.toLowerCase();
  if (s === 'completed' || s === 'success') return 'var(--accent-success)';
  if (s === 'failed' || s === 'error') return 'var(--accent-danger)';
  if (s === 'running' || s === 'in_progress') return 'var(--accent-primary)';
  if (s === 'pending') return 'var(--accent-tertiary)';
  return 'var(--text-muted)';
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + '...';
}
