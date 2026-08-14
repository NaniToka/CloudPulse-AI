import api from '@/lib/api';
import {
  AssetDetailResponse,
  AssetOverviewResponse,
  AssetProviderDistributionResponse,
  AssetRegionDistributionResponse,
  AssetResourceItem,
  AssetServiceDistributionResponse,
  AssetTopologyResponse,
  AssetTypeDistributionResponse,
  OrphanedResourcesResponse,
} from '../types/assets';

export interface AssetFilterParams {
  provider?: string;
  resource_type?: string;
  region?: string;
  status?: string;
  search?: string;
}

export const assetService = {
  getOverview: async (): Promise<AssetOverviewResponse> => {
    const res = await api.get('/assets/overview');
    return res.data;
  },

  getResources: async (filters?: AssetFilterParams): Promise<AssetResourceItem[]> => {
    const res = await api.get('/assets/resources', { params: filters });
    return res.data;
  },

  getResourceDetail: async (resourceId: string): Promise<AssetDetailResponse> => {
    const res = await api.get(`/assets/resources/${resourceId}`);
    return res.data;
  },

  getProviders: async (): Promise<AssetProviderDistributionResponse> => {
    const res = await api.get('/assets/providers');
    return res.data;
  },

  getServices: async (): Promise<AssetServiceDistributionResponse> => {
    const res = await api.get('/assets/services');
    return res.data;
  },

  getRegions: async (): Promise<AssetRegionDistributionResponse> => {
    const res = await api.get('/assets/regions');
    return res.data;
  },

  getTypes: async (): Promise<AssetTypeDistributionResponse> => {
    const res = await api.get('/assets/types');
    return res.data;
  },

  searchResources: async (query: string): Promise<AssetResourceItem[]> => {
    const res = await api.get('/assets/search', { params: { q: query } });
    return res.data;
  },

  getTopology: async (): Promise<AssetTopologyResponse> => {
    const res = await api.get('/assets/topology');
    return res.data;
  },

  getOrphaned: async (): Promise<OrphanedResourcesResponse> => {
    const res = await api.get('/assets/orphaned');
    return res.data;
  },

  triggerDiscover: async (): Promise<any> => {
    const res = await api.post('/assets/discover');
    return res.data;
  },

  triggerRefresh: async (): Promise<any> => {
    const res = await api.post('/assets/refresh');
    return res.data;
  },
};
