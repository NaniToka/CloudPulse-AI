import apiClient from "@/lib/api";
import { PlatformHealthDetailedResponse, PlatformHealthSummaryResponse } from "@/types/platform";

export const getPlatformHealthSummary = async (): Promise<PlatformHealthSummaryResponse> => {
  const response = await apiClient.get<PlatformHealthSummaryResponse>("/platform/health");
  return response.data;
};

export const getDetailedPlatformHealth = async (): Promise<PlatformHealthDetailedResponse> => {
  const response = await apiClient.get<PlatformHealthDetailedResponse>("/platform/health/detailed");
  return response.data;
};

