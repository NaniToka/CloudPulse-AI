/**
 * TypeScript Type Definitions for AI Security & Cloud Compliance Center
 */

export interface SecurityFinding {
  id: string;
  scan_name: string;
  provider: "AWS" | "GCP" | "Azure";
  region: string;
  resource: string;
  severity: "Critical" | "High" | "Medium" | "Low";
  category: "IAM" | "Network" | "Storage" | "Database" | "Secrets";
  compliance_framework: string;
  description: string;
  recommendation: string;
  ai_analysis?: {
    executive_summary?: string;
    risk_score?: number;
    business_impact?: string;
    attack_scenario?: string;
    root_cause?: string;
    remediation_steps?: string[];
    estimated_fix_time?: string;
    priority_order?: number;
    compliance_impact?: string;
    confidence_score?: number;
  };
  status: "Open" | "In_Progress" | "Resolved" | "Ignored";
  created_at: string;
  updated_at: string;
}

export interface ComplianceReport {
  id: string;
  framework: string;
  overall_score: number;
  passed_controls: number;
  failed_controls: number;
  total_controls: number;
  category_scores: Record<string, number>;
  created_at: string;
}

export interface RiskScoreResponse {
  overall_security_score: number;
  overall_risk_score: number;
  critical_findings_count: number;
  high_findings_count: number;
  resources_at_risk_count: number;
  compliance_overall_percentage: number;
  risk_trend: Array<{ day: string; score: number; findings: number }>;
  severity_distribution: Record<string, number>;
}

export interface SecurityListResponse {
  items: SecurityFinding[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface SecurityScanResponse {
  total_findings: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  scanned_resources: number;
  overall_security_score: number;
  message: string;
}
