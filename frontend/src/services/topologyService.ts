import api from '@/lib/api';
import {
  BlastRadiusAnalysisResponse,
  FailureSimulationRequest,
  FailureSimulationResponse,
  SpofListResponse,
  TopologyGraphResponse,
  TopologyNodeItem,
  TopologyOverviewResponse,
} from '../types/topology';

export interface TopologyFilterParams {
  provider?: string;
  region?: string;
  environment?: string;
}

export const topologyService = {
  getOverview: async (): Promise<TopologyOverviewResponse> => {
    const res = await api.get('/topology/overview');
    return res.data;
  },

  getGraph: async (filters?: TopologyFilterParams): Promise<TopologyGraphResponse> => {
    const res = await api.get('/topology/graph', { params: filters });
    return res.data;
  },

  getNodes: async (filters?: TopologyFilterParams): Promise<TopologyNodeItem[]> => {
    const res = await api.get('/topology/nodes', { params: filters });
    return res.data;
  },

  getServiceNodeDetail: async (nodeId: string): Promise<TopologyNodeItem> => {
    const res = await api.get(`/topology/services/${nodeId}`);
    return res.data;
  },

  getUpstreamDependencies: async (nodeId: string): Promise<TopologyNodeItem[]> => {
    const res = await api.get(`/topology/upstream/${nodeId}`);
    return res.data;
  },

  getDownstreamDependencies: async (nodeId: string): Promise<TopologyNodeItem[]> => {
    const res = await api.get(`/topology/downstream/${nodeId}`);
    return res.data;
  },

  getBlastRadius: async (nodeId: string): Promise<BlastRadiusAnalysisResponse> => {
    const res = await api.get(`/topology/blast-radius/${nodeId}`);
    return res.data;
  },

  getSpofs: async (): Promise<SpofListResponse> => {
    const res = await api.get('/topology/spof');
    return res.data;
  },

  simulateFailure: async (payload: FailureSimulationRequest): Promise<FailureSimulationResponse> => {
    const res = await api.post('/topology/simulate-failure', payload);
    return res.data;
  },
};
