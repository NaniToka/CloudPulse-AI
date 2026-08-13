import api from '@/lib/api';
import {
  CloudProviderHealthResponse,
  CloudRiskMatrixResponse,
  ExecutiveAlertsResponse,
  ExecutiveOverviewResponse,
  ExecutivePriorityListResponse,
  ExecutiveRecommendationsResponse,
  ExecutiveSummaryResponse,
  HealthScoreResponse,
  OperationalTrendsResponse,
  ServiceHealthMapResponse,
  WhatChangedResponse,
} from '../types/executive';

export const executiveService = {
  getOverview: async (): Promise<ExecutiveOverviewResponse> => {
    const response = await api.get<ExecutiveOverviewResponse>('/executive/overview');
    return response.data;
  },

  getHealthScore: async (): Promise<HealthScoreResponse> => {
    const response = await api.get<HealthScoreResponse>('/executive/health');
    return response.data;
  },

  getSummary: async (): Promise<ExecutiveSummaryResponse> => {
    const response = await api.get<ExecutiveSummaryResponse>('/executive/summary');
    return response.data;
  },

  getPriorities: async (params?: { domain?: string; severity?: string }): Promise<ExecutivePriorityListResponse> => {
    const response = await api.get<ExecutivePriorityListResponse>('/executive/priorities', { params });
    return response.data;
  },

  getTrends: async (): Promise<OperationalTrendsResponse> => {
    const response = await api.get<OperationalTrendsResponse>('/executive/trends');
    return response.data;
  },

  getProviders: async (): Promise<CloudProviderHealthResponse> => {
    const response = await api.get<CloudProviderHealthResponse>('/executive/providers');
    return response.data;
  },

  getServices: async (): Promise<ServiceHealthMapResponse> => {
    const response = await api.get<ServiceHealthMapResponse>('/executive/services');
    return response.data;
  },

  getRisks: async (): Promise<CloudRiskMatrixResponse> => {
    const response = await api.get<CloudRiskMatrixResponse>('/executive/risks');
    return response.data;
  },

  getChanges: async (): Promise<WhatChangedResponse> => {
    const response = await api.get<WhatChangedResponse>('/executive/changes');
    return response.data;
  },

  getTimeline: async (): Promise<{ events: any[]; total: number }> => {
    const response = await api.get('/executive/timeline');
    return response.data;
  },

  getAlerts: async (): Promise<ExecutiveAlertsResponse> => {
    const response = await api.get<ExecutiveAlertsResponse>('/executive/alerts');
    return response.data;
  },

  getRecommendations: async (): Promise<ExecutiveRecommendationsResponse> => {
    const response = await api.get<ExecutiveRecommendationsResponse>('/executive/recommendations');
    return response.data;
  },

  exportPdf: async (): Promise<Blob> => {
    const response = await api.post('/executive/export/pdf', {}, { responseType: 'blob' });
    return response.data;
  },

  exportCsv: async (): Promise<Blob> => {
    const response = await api.post('/executive/export/csv', {}, { responseType: 'blob' });
    return response.data;
  },
};
