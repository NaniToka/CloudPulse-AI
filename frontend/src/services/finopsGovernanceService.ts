import apiClient from "@/lib/api";
import type {
  CostPolicy,
  CostPolicyCreatePayload,
  CostViolation,
  FinOpsAuditLog,
  GovernanceOverviewResponse,
  GovernanceScoreResponse,
  PolicyException,
  PolicyExceptionCreatePayload,
  RemediationAction,
  RemediationRequestPayload,
} from "@/types/finopsGovernance";

export const finopsGovernanceService = {
  async getOverview(): Promise<GovernanceOverviewResponse> {
    const response = await apiClient.get<GovernanceOverviewResponse>("/finops/governance/overview");
    return response.data;
  },

  async getScore(): Promise<GovernanceScoreResponse> {
    const response = await apiClient.get<GovernanceScoreResponse>("/finops/governance/score");
    return response.data;
  },

  async getPolicies(params?: {
    provider?: string;
    category?: string;
    severity?: string;
    enabled?: boolean;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ policies: CostPolicy[]; total: number }> {
    const response = await apiClient.get<{ policies: CostPolicy[]; total: number }>("/finops/policies", { params });
    return response.data;
  },

  async createPolicy(payload: CostPolicyCreatePayload): Promise<CostPolicy> {
    const response = await apiClient.post<CostPolicy>("/finops/policies", payload);
    return response.data;
  },

  async updatePolicy(id: string, payload: Partial<CostPolicyCreatePayload>): Promise<CostPolicy> {
    const response = await apiClient.put<CostPolicy>(`/finops/policies/${id}`, payload);
    return response.data;
  },

  async togglePolicyStatus(id: string, enabled: boolean): Promise<CostPolicy> {
    const response = await apiClient.patch<CostPolicy>(`/finops/policies/${id}/status`, null, {
      params: { enabled },
    });
    return response.data;
  },

  async deletePolicy(id: string): Promise<void> {
    await apiClient.delete(`/finops/policies/${id}`);
  },

  async evaluatePolicy(id: string): Promise<Record<string, unknown>> {
    const response = await apiClient.post<Record<string, unknown>>(`/finops/policies/${id}/evaluate`);
    return response.data;
  },

  async getViolations(params?: {
    severity?: string;
    status?: string;
    provider?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ violations: CostViolation[]; total: number; critical_count: number; high_count: number }> {
    const response = await apiClient.get<{
      violations: CostViolation[];
      total: number;
      critical_count: number;
      high_count: number;
    }>("/finops/violations", { params });
    return response.data;
  },

  async updateViolationStatus(id: string, status: string): Promise<CostViolation> {
    const response = await apiClient.patch<CostViolation>(`/finops/violations/${id}/status`, { status });
    return response.data;
  },

  async getExceptions(): Promise<{ exceptions: PolicyException[]; total: number }> {
    const response = await apiClient.get<{ exceptions: PolicyException[]; total: number }>("/finops/exceptions");
    return response.data;
  },

  async createException(payload: PolicyExceptionCreatePayload): Promise<PolicyException> {
    const response = await apiClient.post<PolicyException>("/finops/exceptions", payload);
    return response.data;
  },

  async updateExceptionStatus(id: string, status: string, approvedBy?: string): Promise<PolicyException> {
    const response = await apiClient.patch<PolicyException>(`/finops/exceptions/${id}`, {
      status,
      approved_by: approvedBy,
    });
    return response.data;
  },

  async getRemediations(): Promise<{
    remediations: RemediationAction[];
    total: number;
    pending_approvals: number;
    potential_savings: number;
  }> {
    const response = await apiClient.get<{
      remediations: RemediationAction[];
      total: number;
      pending_approvals: number;
      potential_savings: number;
    }>("/finops/remediations");
    return response.data;
  },

  async requestRemediation(payload: RemediationRequestPayload): Promise<RemediationAction> {
    const response = await apiClient.post<RemediationAction>("/finops/remediations/request", payload);
    return response.data;
  },

  async approveRemediation(id: string, status: string): Promise<RemediationAction> {
    const response = await apiClient.post<RemediationAction>(`/finops/remediations/${id}/approve`, { status });
    return response.data;
  },

  async executeRemediation(id: string, executionMode = "SIMULATED"): Promise<RemediationAction> {
    const response = await apiClient.post<RemediationAction>(`/finops/remediations/${id}/execute`, {
      execution_mode: executionMode,
    });
    return response.data;
  },

  async rollbackRemediation(id: string): Promise<RemediationAction> {
    const response = await apiClient.post<RemediationAction>(`/finops/remediations/${id}/rollback`);
    return response.data;
  },

  async getAuditTrail(skip = 0, limit = 50): Promise<{ audit_logs: FinOpsAuditLog[]; total: number }> {
    const response = await apiClient.get<{ audit_logs: FinOpsAuditLog[]; total: number }>("/finops/audit", {
      params: { skip, limit },
    });
    return response.data;
  },
};
