import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { telemetryService, TelemetryEventItem, MetricRecordItem, TraceRecordItem, TelemetryHealthItem, AIOperationalSummaryItem } from "@/services/telemetryService";

export const useTelemetryHealth = () => {
  return useQuery({
    queryKey: ["telemetry-health"],
    queryFn: () => telemetryService.getHealth(),
    refetchInterval: 10000,
  });
};

export const useTelemetryEvents = (limit: number = 50, severity?: string) => {
  return useQuery({
    queryKey: ["telemetry-events", limit, severity],
    queryFn: () => telemetryService.getEvents({ limit, severity }),
    refetchInterval: 5000,
  });
};

export const useAIOperationalSummary = () => {
  return useQuery({
    queryKey: ["telemetry-ai-summary"],
    queryFn: () => telemetryService.getAISummary(),
    refetchInterval: 15000,
  });
};
