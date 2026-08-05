/**
 * TypeScript Type Definitions for AI Runbook Generator & Auto Remediation Center
 */

export interface AutomationStep {
  id: string;
  runbook_id: string;
  step_number: number;
  title: string;
  description?: string;
  command: string;
  expected_output?: string;
  rollback_command?: string;
  estimated_time: string;
  verification_method: string;
  status: "Pending" | "Running" | "Completed" | "Failed";
}

export interface RunbookExecution {
  id: string;
  runbook_id: string;
  executed_by: string;
  started_at: string;
  completed_at?: string;
  status: "In_Progress" | "Completed" | "Failed";
  logs_json: string[];
}

export interface Runbook {
  id: string;
  title: string;
  incident_id?: string;
  service_name: string;
  severity: "P0" | "P1" | "P2" | "P3";
  generated_by_ai: boolean;
  status: "Draft" | "Approved" | "Executing" | "Completed" | "Failed";
  executive_summary?: string;
  root_cause?: string;
  rollback_procedure?: string;
  verification_checklist: string[];
  post_recovery_checklist: string[];
  estimated_resolution_time: string;
  risk_score: number;
  confidence_score: number;
  created_at: string;
  updated_at: string;
  steps: AutomationStep[];
  executions: RunbookExecution[];
}

export interface RunbookListResponse {
  items: Runbook[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface RunbookGeneratePayload {
  incident_id?: string;
  service_name: string;
  severity: "P0" | "P1" | "P2" | "P3";
  title?: string;
}
