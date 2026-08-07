import apiClient from "@/lib/api";

export interface ServerItem {
  id: string;
  name: string;
  hostname: string;
  ip_address?: string;
  server_type: string;
  provider: string;
  region?: string;
  environment: string;
  status: string;
  cpu_percent?: number;
  memory_percent?: number;
  disk_percent?: number;
  network_in_mbps?: number;
  network_out_mbps?: number;
  uptime_seconds?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateServerPayload {
  name: string;
  hostname?: string;
  ip_address?: string;
  server_type?: string;
  provider?: string;
  region?: string;
  environment?: string;
}

export const serverService = {
  getServers: async (params?: { provider?: string; status?: string; search?: string }): Promise<ServerItem[]> => {
    const response = await apiClient.get<ServerItem[]>("/servers", { params });
    return response.data;
  },

  getServer: async (serverId: string): Promise<ServerItem> => {
    const response = await apiClient.get<ServerItem>(`/servers/${serverId}`);
    return response.data;
  },

  createServer: async (payload: CreateServerPayload): Promise<ServerItem> => {
    const response = await apiClient.post<ServerItem>("/servers", payload);
    return response.data;
  },

  deleteServer: async (serverId: string): Promise<void> => {
    await apiClient.delete(`/servers/${serverId}`);
  },
};
