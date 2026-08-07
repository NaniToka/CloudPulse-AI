import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  cloudService,
  CloudAccountItem,
  CloudResourceItem,
  CloudCostSummary,
  CloudSecuritySummary,
  CloudHealthSummary,
  ConnectAccountPayload,
} from "@/services/cloudService";

export function useCloudAccounts(params?: { provider?: string; status?: string }) {
  const queryClient = useQueryClient();

  const query = useQuery<CloudAccountItem[]>({
    queryKey: ["cloud-accounts", params],
    queryFn: () => cloudService.getAccounts(params),
    staleTime: 30_000,
  });

  const connectMutation = useMutation({
    mutationFn: (payload: ConnectAccountPayload) => cloudService.connectAccount(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cloud-accounts"] });
      queryClient.invalidateQueries({ queryKey: ["cloud-resources"] });
      queryClient.invalidateQueries({ queryKey: ["cloud-health"] });
    },
  });

  return {
    ...query,
    connectAccount: connectMutation.mutateAsync,
    isConnecting: connectMutation.isPending,
  };
}

export function useCloudResources(params?: {
  provider?: string;
  resource_type?: string;
  region?: string;
  status?: string;
  search?: string;
}) {
  return useQuery<CloudResourceItem[]>({
    queryKey: ["cloud-resources", params],
    queryFn: () => cloudService.getResources(params),
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}

export function useCloudCost() {
  return useQuery<CloudCostSummary>({
    queryKey: ["cloud-cost"],
    queryFn: () => cloudService.getCostSummary(),
    staleTime: 60_000,
  });
}

export function useCloudSecurity() {
  return useQuery<CloudSecuritySummary>({
    queryKey: ["cloud-security"],
    queryFn: () => cloudService.getSecuritySummary(),
    staleTime: 30_000,
  });
}

export function useCloudHealth() {
  return useQuery<CloudHealthSummary>({
    queryKey: ["cloud-health"],
    queryFn: () => cloudService.getHealthSummary(),
    staleTime: 20_000,
  });
}

export function useCloudSync() {
  const queryClient = useQueryClient();

  const syncMutation = useMutation({
    mutationFn: (accountId?: string) => cloudService.triggerSync(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cloud-resources"] });
      queryClient.invalidateQueries({ queryKey: ["cloud-health"] });
      queryClient.invalidateQueries({ queryKey: ["cloud-cost"] });
    },
  });

  return {
    triggerSync: syncMutation.mutateAsync,
    isSyncing: syncMutation.isPending,
  };
}
