import apiClient from "@/lib/api";

export interface K8sClusterItem {
  id: string;
  user_id: string;
  name: string;
  provider: "GKE" | "EKS" | "AKS" | "Self-Hosted" | string;
  version: string;
  region: string;
  status: string;
  node_count: number;
  pod_count: number;
  cpu_capacity_cores: number;
  cpu_usage_cores: number;
  memory_capacity_gb: number;
  memory_usage_gb: number;
  created_at: string;
  updated_at: string;
}

export interface K8sNodeItem {
  id: string;
  cluster_id: string;
  name: string;
  role: string;
  status: string;
  instance_type: string;
  internal_ip: string;
  kubelet_version: string;
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  pod_capacity: number;
  pods_running: number;
  created_at: string;
  updated_at: string;
}

export interface K8sPodItem {
  id: string;
  cluster_id: string;
  node_id?: string;
  name: string;
  namespace: string;
  deployment_name?: string;
  status: "Running" | "Pending" | "CrashLoopBackOff" | "OOMKilled" | "ImagePullBackOff" | string;
  restart_count: number;
  cpu_usage_m: number;
  memory_usage_mb: number;
  container_images?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface K8sDeploymentItem {
  id: string;
  cluster_id: string;
  name: string;
  namespace: string;
  desired_replicas: number;
  ready_replicas: number;
  updated_replicas: number;
  strategy: string;
  image: string;
  created_at: string;
  updated_at: string;
}

export interface K8sEventItem {
  id: string;
  event_type: "Normal" | "Warning" | string;
  reason: string;
  object_kind: string;
  object_name: string;
  namespace: string;
  message: string;
  timestamp: string;
  created_at: string;
  updated_at: string;
}

export interface K8sAnalysisResult {
  cluster_health_score: number;
  total_pods_monitored: number;
  failed_pods_count: number;
  warning_events_count: number;
  root_cause_analysis: Array<{
    pod_name: string;
    issue: string;
    root_cause: string;
    recommendation: string;
  }>;
}

export const kubernetesService = {
  getClusters: async (params?: { provider?: string }): Promise<K8sClusterItem[]> => {
    const response = await apiClient.get<K8sClusterItem[]>("/kubernetes/clusters", { params });
    return response.data;
  },

  getNodes: async (params?: { cluster_id?: string }): Promise<K8sNodeItem[]> => {
    const response = await apiClient.get<K8sNodeItem[]>("/kubernetes/nodes", { params });
    return response.data;
  },

  getPods: async (params?: {
    cluster_id?: string;
    namespace?: string;
    status?: string;
    search?: string;
  }): Promise<K8sPodItem[]> => {
    const response = await apiClient.get<K8sPodItem[]>("/kubernetes/pods", { params });
    return response.data;
  },

  getDeployments: async (params?: { cluster_id?: string; namespace?: string }): Promise<K8sDeploymentItem[]> => {
    const response = await apiClient.get<K8sDeploymentItem[]>("/kubernetes/deployments", { params });
    return response.data;
  },

  getEvents: async (params?: { event_type?: string }): Promise<K8sEventItem[]> => {
    const response = await apiClient.get<K8sEventItem[]>("/kubernetes/events", { params });
    return response.data;
  },

  getPodLogs: async (podName: string, tail: number = 100): Promise<{ pod_name: string; logs: string[] }> => {
    const response = await apiClient.get<{ pod_name: string; logs: string[] }>(`/kubernetes/logs/${podName}`, {
      params: { tail },
    });
    return response.data;
  },

  analyzeCluster: async (clusterId?: string): Promise<K8sAnalysisResult> => {
    const response = await apiClient.post<K8sAnalysisResult>("/kubernetes/analyze", null, {
      params: { cluster_id: clusterId },
    });
    return response.data;
  },
};
