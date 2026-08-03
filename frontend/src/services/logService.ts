import apiClient from "@/lib/api";
import type { LogAnalysis, UploadResponse, HistoryResponse } from "@/types/log_analysis";

export const logService = {
  async uploadLog(file: File, onUploadProgress?: (progressEvent: { loaded: number; total?: number }) => void): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post<UploadResponse>("/logs/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });
    return response.data;
  },

  async getHistory(skip = 0, limit = 50): Promise<HistoryResponse> {
    const response = await apiClient.get<HistoryResponse>("/logs/history", {
      params: { skip, limit },
    });
    return response.data;
  },

  async getAnalysis(id: string): Promise<LogAnalysis> {
    const response = await apiClient.get<LogAnalysis>(`/logs/${id}`);
    return response.data;
  },

  async deleteAnalysis(id: string): Promise<void> {
    await apiClient.delete(`/logs/${id}`);
  },
};
