import {
  Goal, GoalCreate, Execution, ExecutionSummary, 
  DocumentMetadata, StreamEvent, EvaluationResult
} from './types';

export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const envUrl = process.env.NEXT_PUBLIC_API_URL;
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    
    if (envUrl && envUrl.trim() !== '') {
      if (!isLocalhost && envUrl.includes('localhost')) {
        return window.location.origin;
      }
      return envUrl.replace(/\/$/, '');
    }
    
    if (!isLocalhost) {
      return window.location.origin;
    }
  }
  return (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
}

class ChethasAPI {
  private get baseUrl(): string {
    return getApiBaseUrl();
  }
  
  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      ...options,
    });
    if (!res.ok) {
      let detail = '';
      try {
        const body = await res.json();
        detail = typeof body === 'string' ? body : JSON.stringify(body);
      } catch {
        detail = await res.text().catch(() => '');
      }
      throw new Error(`API Error ${res.status} on ${path}: ${detail}`);
    }
    return res.json();
  }
  
  // Goals
  async createGoal(input: GoalCreate): Promise<Goal> {
    return this.request<Goal>('/api/goals', {
      method: 'POST',
      body: JSON.stringify(input)
    });
  }
  
  async listGoals(): Promise<Goal[]> {
    return this.request<Goal[]>('/api/goals');
  }
  
  async getGoal(id: string): Promise<Goal> {
    return this.request<Goal>(`/api/goals/${id}`);
  }
  
  // Executions
  async startExecution(goalId: string): Promise<Execution> {
    return this.request<Execution>(`/api/executions`, {
      method: 'POST',
      body: JSON.stringify({ goal_id: goalId })
    });
  }
  
  async getExecution(id: string): Promise<Execution> {
    return this.request<Execution>(`/api/executions/${id}`);
  }
  
  async listExecutions(): Promise<ExecutionSummary[]> {
    return this.request<ExecutionSummary[]>('/api/executions');
  }
  
  // Documents
  async uploadDocument(file: File, metadata?: { title?: string; description?: string }): Promise<DocumentMetadata> {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    const res = await fetch(`${this.baseUrl}/api/documents`, {
      method: 'POST',
      body: formData,
    });
    
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  }
  
  async listDocuments(): Promise<DocumentMetadata[]> {
    return this.request<DocumentMetadata[]>('/api/documents');
  }
  
  async deleteDocument(id: string): Promise<void> {
    await this.request<void>(`/api/documents/${id}`, { method: 'DELETE' });
  }
  
  // Streaming
  streamExecution(executionId: string, onEvent: (event: StreamEvent) => void): EventSource {
    const sse = new EventSource(`${this.baseUrl}/api/executions/${executionId}/stream`);
    sse.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        onEvent(parsed);
      } catch (e) {
        console.error('Failed to parse SSE event:', e);
      }
    };
    return sse;
  }
  
  // Evaluations
  async getEvaluation(executionId: string): Promise<EvaluationResult> {
    return this.request<EvaluationResult>(`/api/evaluations/${executionId}`);
  }
}

export const api = new ChethasAPI();
