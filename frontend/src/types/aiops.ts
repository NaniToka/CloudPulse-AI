/**
 * TypeScript Type Definitions for Autonomous AIOps Agent & AI Operations Center
 */

export interface AgentTask {
  id: string;
  agent_id: string;
  task_name: string;
  target_system: string;
  status: "Pending" | "In_Progress" | "Completed" | "Failed";
  started_at: string;
  completed_at?: string;
}

export interface AgentExecution {
  id: string;
  recommendation_id: string;
  action_taken: string;
  approved_by: string;
  status: string;
  execution_logs: string[];
  executed_at: string;
}

export interface AgentRecommendation {
  id: string;
  agent_id: string;
  title: string;
  category:
    | "Anomaly_Detection"
    | "Root_Cause"
    | "Performance"
    | "Capacity_Planning"
    | "Risk_Prediction"
    | "Cost_Optimization"
    | "Security_Correlation";
  priority: "P0" | "P1" | "P2" | "P3";
  executive_summary: string;
  root_cause?: string;
  business_impact?: string;
  recommended_actions: string[];
  automation_candidates: string[];
  confidence_score: number;
  expected_recovery_time: string;
  status: "Pending_Approval" | "Approved" | "Rejected" | "Executed";
  created_at: string;
  executions: AgentExecution[];
}

export interface AIOpsAgentStatus {
  id: string;
  agent_name: string;
  status: "Active" | "Autonomous" | "Paused";
  current_phase: "Observe" | "Detect" | "Analyze" | "Plan" | "Recommend" | "Verify";
  health_status: "Healthy" | "Degraded" | "Anomalous";
  last_observation_at: string;
  total_recommendations: number;
  pending_approvals: number;
  active_automations: number;
  tasks: AgentTask[];
}

export interface AIOpsListResponse {
  items: AgentRecommendation[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
