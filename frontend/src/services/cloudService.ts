import apiClient from "@/lib/api";

export interface CloudAccountItem {
  id: string;
  user_id: string;
  name: string;
  provider: "AWS" | "Azure" | "GCP" | string;
  account_id: string;
  credentials_type: string;
  credentials_meta: Record<string, any>;
  default_region: string;
  environment: string;
  status: string;
  last_synced_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CloudResourceItem {
  id: string;
  account_id: string;
  name: string;
  resource_type: string;
  service: string;
  provider: "AWS" | "Azure" | "GCP" | string;
  region: string;
  availability_zone?: string;
  environment: string;
  status: string;
  cpu_percent?: number;
  memory_percent?: number;
  disk_percent?: number;
  network_in_mbps?: number;
  network_out_mbps?: number;
  monthly_cost: number;
  risk_score: number;
  tags?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CloudCostSummary {
  total_monthly_spend: number;
  forecasted_next_month: number;
  provider_breakdown: Record<string, number>;
  idle_resource_savings: number;
}

export interface CloudSecuritySummary {
  overall_compliance_score: number;
  high_risk_resources_count: number;
  open_vulnerabilities: number;
  high_risk_list: Array<{ id: string; name: string; provider: string; risk_score: number }>;
}

export interface CloudHealthSummary {
  total_resources: number;
  healthy_count: number;
  degraded_count: number;
  critical_count: number;
  health_score_percent: number;
  ai_insights: Array<{ category: string; severity: string; title: string; description: string }>;
}

export interface ConnectAccountPayload {
  name: string;
  provider: "AWS" | "Azure" | "GCP" | string;
  account_id: string;
  credentials_type: string;
  credentials_meta: Record<string, any>;
  default_region?: string;
  environment?: string;
}

export const cloudService = {
  getAccounts: async (params?: { provider?: string; status?: string }): Promise<CloudAccountItem[]> => {
    const response = await apiClient.get<CloudAccountItem[]>("/cloud/accounts", { params });
    return response.data;
  },

  connectAccount: async (payload: ConnectAccountPayload): Promise<CloudAccountItem> => {
    const response = await apiClient.post<CloudAccountItem>("/cloud/accounts", payload);
    return response.data;
  },

  getResources: async (params?: {
    provider?: string;
    resource_type?: string;
    region?: string;
    status?: string;
    search?: string;
  }): Promise<CloudResourceItem[]> => {
    const response = await apiClient.get<CloudResourceItem[]>("/cloud/resources", { params });
    return response.data;
  },

  getCostSummary: async (): Promise<CloudCostSummary> => {
    const response = await apiClient.get<CloudCostSummary>("/cloud/cost");
    return response.data;
  },

  getSecuritySummary: async (): Promise<CloudSecuritySummary> => {
    const response = await apiClient.get<CloudSecuritySummary>("/cloud/security");
    return response.data;
  },

  getHealthSummary: async (): Promise<CloudHealthSummary> => {
    const response = await apiClient.get<CloudHealthSummary>("/cloud/health");
    return response.data;
  },

  triggerSync: async (accountId?: string): Promise<{ status: string; discovered_count: number }> => {
    const response = await apiClient.post("/cloud/sync", null, { params: { account_id: accountId } });
    return response.data;
  },
};
