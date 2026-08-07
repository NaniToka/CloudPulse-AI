import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  twinService,
  InfrastructureTwinItem,
  TwinResourceItem,
  SimulationScenarioItem,
  SimulationExecutionItem,
  BlastRadiusDetailItem,
  WhatIfResponseItem,
} from "@/services/twinService";

export function useDigitalTwin() {
  return useQuery<InfrastructureTwinItem>({
    queryKey: ["digital-twin"],
    queryFn: () => twinService.getTwin(),
    staleTime: 30_000,
  });
}

export function useTwinResources() {
  return useQuery<TwinResourceItem[]>({
    queryKey: ["twin-resources"],
    queryFn: () => twinService.getTwinResources(),
    staleTime: 30_000,
  });
}

export function useTwinScenarios(category?: string) {
  return useQuery<SimulationScenarioItem[]>({
    queryKey: ["twin-scenarios", category],
    queryFn: () => twinService.getScenarios({ category }),
    staleTime: 30_000,
  });
}

export function useTwinHistory() {
  return useQuery<SimulationExecutionItem[]>({
    queryKey: ["twin-history"],
    queryFn: () => twinService.getHistory(),
    staleTime: 10_000,
    refetchInterval: 20_000,
  });
}

export function useBlastRadius(scenarioId?: string) {
  return useQuery<BlastRadiusDetailItem>({
    queryKey: ["twin-blast-radius", scenarioId],
    queryFn: () => twinService.getBlastRadius(scenarioId!),
    enabled: Boolean(scenarioId),
    staleTime: 15_000,
  });
}

export function useDigitalTwinMutations() {
  const queryClient = useQueryClient();

  const runSimulationMutation = useMutation({
    mutationFn: (scenarioId: string) => twinService.runSimulation(scenarioId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["twin-history"] });
      queryClient.invalidateQueries({ queryKey: ["digital-twin"] });
    },
  });

  const askWhatIfMutation = useMutation({
    mutationFn: (query: string) => twinService.askWhatIf(query),
  });

  return {
    runSimulation: runSimulationMutation.mutateAsync,
    isRunningSimulation: runSimulationMutation.isPending,
    askWhatIf: askWhatIfMutation.mutateAsync,
    isAskingWhatIf: askWhatIfMutation.isPending,
  };
}
