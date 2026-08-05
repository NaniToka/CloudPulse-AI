/**
 * Frontend Service Client for Auto Remediation Center & Runbooks
 */

import apiClient from "@/lib/api";
import type {
  Runbook,
  RunbookListResponse,
  RunbookGeneratePayload,
  RunbookExecution,
} from "@/types/runbook";

export interface RunbookFilterParams {
  service_name?: string;
  severity?: string;
  status?: string;
  search?: string;
  page?: number;
  size?: number;
}

export const runbookService = {
  async getRunbooks(params?: RunbookFilterParams): Promise<RunbookListResponse> {
    const response = await apiClient.get<RunbookListResponse>("/runbooks", { params });
    return response.data;
  },

  async getRunbookById(id: string): Promise<Runbook> {
    const response = await apiClient.get<Runbook>(`/runbooks/${id}`);
    return response.data;
  },

  async generateRunbook(payload: RunbookGeneratePayload): Promise<Runbook> {
    const response = await apiClient.post<Runbook>("/runbooks/generate", payload);
    return response.data;
  },

  async approveRunbook(id: string, approvedBy: string = "SRE Lead"): Promise<Runbook> {
    const response = await apiClient.post<Runbook>(`/runbooks/${id}/approve`, { approved_by: approvedBy });
    return response.data;
  },

  async executeRunbook(id: string): Promise<RunbookExecution> {
    const response = await apiClient.post<RunbookExecution>(`/runbooks/${id}/execute`);
    return response.data;
  },
};
