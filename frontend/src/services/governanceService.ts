import apiClient from "@/lib/api";
import type {
  GovernanceOverviewResponse,
  GovernancePolicyListResponse,
  GovernancePolicyItem,
  GovernancePolicyCreatePayload,
  ComplianceFrameworkListResponse,
  ComplianceFrameworkItem,
  PolicyEvaluationListResponse,
  GovernanceViolationListResponse,
  GovernanceViolationItem,
  GovernanceRemediationListResponse,
  AuditTrailListResponse,
  GovernanceTrendResponse,
  GovernanceAnalyzeResponse,
} from "@/types/governance";

export const governanceService = {
  async getOverview(): Promise<GovernanceOverviewResponse> {
    const response = await apiClient.get<GovernanceOverviewResponse>("/governance/overview");
    return response.data;
  },

  async getPolicies(params?: { category?: string; provider?: string; severity?: string }): Promise<GovernancePolicyListResponse> {
    const response = await apiClient.get<GovernancePolicyListResponse>("/governance/policies", { params });
    return response.data;
  },

  async createPolicy(payload: GovernancePolicyCreatePayload): Promise<GovernancePolicyItem> {
    const response = await apiClient.post<GovernancePolicyItem>("/governance/policies", payload);
    return response.data;
  },

  async updatePolicy(id: string, payload: Partial<GovernancePolicyCreatePayload>): Promise<GovernancePolicyItem> {
    const response = await apiClient.put<GovernancePolicyItem>(`/governance/policies/${id}`, payload);
    return response.data;
  },

  async getFrameworks(): Promise<ComplianceFrameworkListResponse> {
    const response = await apiClient.get<ComplianceFrameworkListResponse>("/governance/frameworks");
    return response.data;
  },

  async getFrameworkDetail(frameworkName: string): Promise<ComplianceFrameworkItem> {
    const response = await apiClient.get<ComplianceFrameworkItem>(`/governance/frameworks/${frameworkName}`);
    return response.data;
  },

  async getEvaluations(params?: { provider?: string; status?: string }): Promise<PolicyEvaluationListResponse> {
    const response = await apiClient.get<PolicyEvaluationListResponse>("/governance/evaluations", { params });
    return response.data;
  },

  async getViolations(params?: { status?: string; severity?: string; provider?: string }): Promise<GovernanceViolationListResponse> {
    const response = await apiClient.get<GovernanceViolationListResponse>("/governance/violations", { params });
    return response.data;
  },

  async getViolationDetail(id: string): Promise<GovernanceViolationItem> {
    const response = await apiClient.get<GovernanceViolationItem>(`/governance/violations/${id}`);
    return response.data;
  },

  async updateViolationStatus(id: string, status: string, reason?: string): Promise<GovernanceViolationItem> {
    const response = await apiClient.patch<GovernanceViolationItem>(`/governance/violations/${id}/status`, {
      status,
      reason,
    });
    return response.data;
  },

  async getRecommendations(): Promise<GovernanceRemediationListResponse> {
    const response = await apiClient.get<GovernanceRemediationListResponse>("/governance/recommendations");
    return response.data;
  },

  async getAuditTrail(): Promise<AuditTrailListResponse> {
    const response = await apiClient.get<AuditTrailListResponse>("/governance/audit");
    return response.data;
  },

  async getTrends(days = 30): Promise<GovernanceTrendResponse> {
    const response = await apiClient.get<GovernanceTrendResponse>("/governance/trends", {
      params: { days },
    });
    return response.data;
  },

  async triggerEvaluation(): Promise<PolicyEvaluationListResponse> {
    const response = await apiClient.post<PolicyEvaluationListResponse>("/governance/evaluate");
    return response.data;
  },

  async triggerAnalysis(): Promise<GovernanceAnalyzeResponse> {
    const response = await apiClient.post<GovernanceAnalyzeResponse>("/governance/analyze");
    return response.data;
  },
};
