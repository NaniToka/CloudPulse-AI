import apiClient from "@/lib/api";
import { PlatformHealthDetailedResponse } from "@/types/platform";

export const getDetailedPlatformHealth = async (): Promise<PlatformHealthDetailedResponse> => {
  const response = await apiClient.get<PlatformHealthDetailedResponse>("/platform/health/detailed");
  return response.data;
};
