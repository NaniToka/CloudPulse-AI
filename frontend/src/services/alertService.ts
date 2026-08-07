import apiClient from "@/lib/api";

export interface AlertItem {
  id: string;
  title: string;
  message?: string;
  severity: "critical" | "high" | "medium" | "low" | string;
  status: "active" | "acknowledged" | "resolved" | string;
  metric_name?: string;
  metric_value?: number;
  threshold?: number;
  tags?: Record<string, any>;
  resource_id?: string;
  incident_id?: string;
  created_at: string;
  updated_at: string;
}

export const alertService = {
  getAlerts: async (params?: { status?: string; severity?: string; search?: string }): Promise<AlertItem[]> => {
    const response = await apiClient.get<AlertItem[]>("/alerts", { params });
    return response.data;
  },

  acknowledgeAlert: async (alertId: string): Promise<AlertItem> => {
    const response = await apiClient.patch<AlertItem>(`/alerts/${alertId}/acknowledge`);
    return response.data;
  },

  resolveAlert: async (alertId: string): Promise<AlertItem> => {
    const response = await apiClient.patch<AlertItem>(`/alerts/${alertId}/resolve`);
    return response.data;
  },

  acknowledgeAll: async (): Promise<{ status: string; acknowledged_count: number }> => {
    const response = await apiClient.post("/alerts/acknowledge-all");
    return response.data;
  },
};
