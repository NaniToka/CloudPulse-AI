import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  kubernetesService,
  K8sClusterItem,
  K8sNodeItem,
  K8sPodItem,
  K8sDeploymentItem,
  K8sEventItem,
  K8sAnalysisResult,
} from "@/services/kubernetesService";

export function useK8sClusters(params?: { provider?: string }) {
  return useQuery<K8sClusterItem[]>({
    queryKey: ["k8s-clusters", params],
    queryFn: () => kubernetesService.getClusters(params),
    staleTime: 30_000,
  });
}

export function useK8sNodes(params?: { cluster_id?: string }) {
  return useQuery<K8sNodeItem[]>({
    queryKey: ["k8s-nodes", params],
    queryFn: () => kubernetesService.getNodes(params),
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}

export function useK8sPods(params?: {
  cluster_id?: string;
  namespace?: string;
  status?: string;
  search?: string;
}) {
  return useQuery<K8sPodItem[]>({
    queryKey: ["k8s-pods", params],
    queryFn: () => kubernetesService.getPods(params),
    staleTime: 10_000,
    refetchInterval: 15_000,
  });
}

export function useK8sDeployments(params?: { cluster_id?: string; namespace?: string }) {
  return useQuery<K8sDeploymentItem[]>({
    queryKey: ["k8s-deployments", params],
    queryFn: () => kubernetesService.getDeployments(params),
    staleTime: 15_000,
  });
}

export function useK8sEvents(params?: { event_type?: string }) {
  return useQuery<K8sEventItem[]>({
    queryKey: ["k8s-events", params],
    queryFn: () => kubernetesService.getEvents(params),
    staleTime: 10_000,
    refetchInterval: 15_000,
  });
}

export function useK8sPodLogs(podName: string | null) {
  return useQuery<{ pod_name: string; logs: string[] }>({
    queryKey: ["k8s-logs", podName],
    queryFn: () => kubernetesService.getPodLogs(podName!),
    enabled: Boolean(podName),
    staleTime: 5_000,
  });
}

export function useK8sAnalyze() {
  const queryClient = useQueryClient();

  const analyzeMutation = useMutation({
    mutationFn: (clusterId?: string) => kubernetesService.analyzeCluster(clusterId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["k8s-pods"] });
      queryClient.invalidateQueries({ queryKey: ["k8s-events"] });
    },
  });

  return {
    analyzeCluster: analyzeMutation.mutateAsync,
    isAnalyzing: analyzeMutation.isPending,
  };
}
