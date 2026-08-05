/**
 * Frontend Service Client for Autonomous AIOps Agent
 */

import apiClient from "@/lib/api";
import type {
  AIOpsAgentStatus,
  AIOpsListResponse,
  AgentRecommendation,
} from "@/types/aiops";

export interface AIOpsFilterParams {
  category?: string;
  priority?: string;
  status?: string;
  search?: string;
  page?: number;
  size?: number;
}

export const aiopsService = {
  async getAgentStatus(): Promise<AIOpsAgentStatus> {
    const response = await apiClient.get<AIOpsAgentStatus>("/aiops/status");
    return response.data;
  },

  async getRecommendations(params?: AIOpsFilterParams): Promise<AIOpsListResponse> {
    const response = await apiClient.get<AIOpsListResponse>("/aiops/recommendations", { params });
    return response.data;
  },

  async triggerAnalysis(targetSystem: string = "All"): Promise<AgentRecommendation> {
    const response = await apiClient.post<AgentRecommendation>("/aiops/analyze", { target_system: targetSystem });
    return response.data;
  },

  async approveOrReject(recommendationId: string, action: "Approve" | "Reject", approvedBy: string = "Lead SRE"): Promise<AgentRecommendation> {
    const response = await apiClient.post<AgentRecommendation>("/aiops/approve", {
      recommendation_id: recommendationId,
      action,
      approved_by: approvedBy,
    });
    return response.data;
  },

  async getExecutionHistory(): Promise<{ total_executions: number; history: AgentRecommendation[] }> {
    const response = await apiClient.get("/aiops/history");
    return response.data;
  },
};
