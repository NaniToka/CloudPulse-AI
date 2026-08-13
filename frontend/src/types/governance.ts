export interface GovernancePolicyItem {
  id: string;
  name: string;
  description?: string | null;
  category: "Security" | "FinOps" | "SRE" | "Kubernetes" | "Tagging" | "Operations" | string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;
  provider: "AWS" | "Azure" | "GCP" | "Kubernetes" | "Multi-Cloud" | string;
  resource_type: string;
  rule_identifier: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface GovernancePolicyCreatePayload {
  name: string;
  description?: string;
  category?: string;
  severity?: string;
  provider?: string;
  resource_type?: string;
  rule_identifier?: string;
  enabled?: boolean;
}

export interface GovernancePolicyListResponse {
  policies: GovernancePolicyItem[];
  total: number;
}

export interface PolicyEvaluationItem {
  policy_name: string;
  rule_identifier: string;
  category: string;
  severity: string;
  provider: string;
  resource_id: string;
  resource_name: string;
  resource_type: string;
  region: string;
  status: "PASS" | "FAIL" | "WARNING" | "NOT_APPLICABLE" | string;
  evidence: string;
  recommended_action: string;
  evaluated_at: string;
}

export interface PolicyEvaluationListResponse {
  evaluations: PolicyEvaluationItem[];
  total: number;
}

export interface ComplianceFrameworkItem {
  framework: string;
  version: string;
  disclaimer: string;
  total_controls: number;
  passing_controls: number;
  failing_controls: number;
  coverage_percentage: number;
  compliance_score: number;
  status: "PASS" | "WARNING" | "FAIL" | string;
}

export interface ComplianceFrameworkListResponse {
  frameworks: ComplianceFrameworkItem[];
  total: number;
}

export interface GovernanceViolationItem {
  id: string;
  policy_id: string;
  policy_name: string;
  category: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;
  provider: string;
  resource_id: string;
  resource_name: string;
  resource_type: string;
  region: string;
  status: "OPEN" | "ACKNOWLEDGED" | "IN_REMEDIATION" | "RESOLVED" | "WAIVED" | string;
  evidence: string;
  recommended_action: string;
  waived_by?: string | null;
  waiver_reason?: string | null;
  detected_at: string;
  updated_at: string;
}

export interface GovernanceViolationListResponse {
  violations: GovernanceViolationItem[];
  total_violations: number;
  critical_violations: number;
}

export interface GovernanceRemediationItem {
  id: string;
  violation_id: string;
  resource: string;
  category: string;
  severity: string;
  reason: string;
  evidence: string;
  recommended_action: string;
  estimated_effort: string;
  risk_reduction: string;
  confidence: number;
  workflow_automation_supported: boolean;
}

export interface GovernanceRemediationListResponse {
  remediations: GovernanceRemediationItem[];
  total: number;
}

export interface AuditEventItem {
  id: string;
  action: string;
  actor_user_id?: string | null;
  details: Record<string, any>;
  timestamp: string;
}

export interface AuditTrailListResponse {
  audit_events: AuditEventItem[];
  total: number;
}

export interface GovernanceTrendPoint {
  day: string;
  score: number;
  violations: number;
}

export interface GovernanceTrendResponse {
  horizon_days: number;
  compliance_trend: GovernanceTrendPoint[];
  resolved_violations_period: number;
  new_violations_period: number;
  policy_coverage_percentage: number;
}

export interface GovernanceOverviewResponse {
  governance_score: number;
  governance_rating: "EXCELLENT" | "GOOD" | "AT_RISK" | "CRITICAL" | string;
  compliance_score: number;
  policies_evaluated_count: number;
  passing_controls_count: number;
  failing_controls_count: number;
  open_violations: number;
  critical_violations: number;
  high_violations: number;
  medium_violations: number;
  low_violations: number;
  data_source?: string;
  scoring_methodology?: string;
}

export interface GovernanceAnalyzeResponse {
  executive_summary: string;
  critical_violations: string[];
  framework_insights: string[];
  remediation_recommendations: GovernanceRemediationItem[];
  analyzed_at: string;
  analysis_engine?: string;
}
