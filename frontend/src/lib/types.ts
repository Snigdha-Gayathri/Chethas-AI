// Types mirroring the backend Pydantic models

export interface GoalCreate {
  query: string;
  context?: string;
}

export interface Goal {
  id: string;
  query: string;
  context?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface TimelineEvent {
  timestamp: string;
  type: string;
  message: string;
  metadata?: any;
}

export interface ExecutionPhase {
  id: string;
  name: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  logs: TimelineEvent[];
}

export interface Execution {
  id: string;
  goal_id: string;
  status: string;
  phases: ExecutionPhase[];
  created_at: string;
  updated_at: string;
}

export interface ExecutionSummary {
  id: string;
  goal_id: string;
  status: string;
  created_at: string;
}

export interface AgentRole {
  name: string;
  description: string;
}

export interface Citation {
  document_id: string;
  page?: number;
  text_snippet?: string;
}

export interface Evidence {
  id: string;
  content: string;
  citations: Citation[];
}

export interface AgentFinding {
  agent: string;
  content: string;
  evidence: Evidence[];
}

export interface PlannerDecision {
  phase: string;
  action: string;
  reasoning: string;
}

export interface DeliberationRound {
  id: string;
  topic: string;
  findings: AgentFinding[];
}

export interface ReflectionReport {
  id: string;
  summary: string;
  critique: string;
  improvements: string[];
}

export interface JudgeVerdict {
  passed: boolean;
  score: number;
  reasoning: string;
}

export interface ConsensusReport {
  id: string;
  conclusion: string;
  confidence: number;
  supporting_evidence: Evidence[];
}

export interface EvaluationResult {
  id: string;
  execution_id: string;
  score: number;
  metrics: Record<string, number>;
  feedback: string;
}

export interface BenchmarkResult {
  id: string;
  dataset: string;
  overall_score: number;
  evaluations: EvaluationResult[];
}

export interface StreamEvent {
  type: string;
  data: any;
}

export interface DocumentMetadata {
  id: string;
  filename: string;
  title?: string;
  description?: string;
  uploaded_at: string;
  size: number;
}

export interface ContextStrategyDecision {
  strategy: string;
  reasoning: string;
}
