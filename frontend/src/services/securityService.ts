/**
 * Frontend Service Client for AI Security & Cloud Compliance Center
 */

import apiClient from "@/lib/api";
import type {
  SecurityListResponse,
  ComplianceReport,
  RiskScoreResponse,
  SecurityScanResponse,
} from "@/types/security";

export interface SecurityFilterParams {
  severity?: string;
  category?: string;
  provider?: string;
  framework?: string;
  status?: string;
  search?: string;
  page?: number;
  size?: number;
}

export const securityService = {
  async triggerScan(provider: string = "AWS"): Promise<SecurityScanResponse> {
    const response = await apiClient.post<SecurityScanResponse>("/security/scan", { provider });
    return response.data;
  },

  async getFindings(params?: SecurityFilterParams): Promise<SecurityListResponse> {
    const response = await apiClient.get<SecurityListResponse>("/security/findings", { params });
    return response.data;
  },

  async getCompliance(): Promise<ComplianceReport[]> {
    const response = await apiClient.get<ComplianceReport[]>("/security/compliance");
    return response.data;
  },

  async getRiskScore(): Promise<RiskScoreResponse> {
    const response = await apiClient.get<RiskScoreResponse>("/security/risk-score");
    return response.data;
  },

  async getExecutiveReport(): Promise<any> {
    const response = await apiClient.get("/security/report");
    return response.data;
  },
};
