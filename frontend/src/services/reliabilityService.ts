import api from '@/lib/api';
import {
  DependencyImpactItem,
  ErrorBudgetOverview,
  ReliabilityAnalyzeResult,
  ReliabilityIncidentItem,
  ReliabilityOverview,
  ReliabilityRecommendationItem,
  ReliabilityRiskItem,
  ServiceDetailView,
  ServiceReliabilityProfile,
  SloForecastItem,
} from '../types/reliability';

export interface ReliabilityFilterParams {
  provider?: string;
  service?: string;
  status?: string;
}

export const reliabilityService = {
  getOverview: async (): Promise<ReliabilityOverview> => {
    const res = await api.get('/reliability/overview');
    return res.data;
  },

  getServices: async (filters?: ReliabilityFilterParams): Promise<ServiceReliabilityProfile[]> => {
    const res = await api.get('/reliability/services', { params: filters });
    return res.data;
  },

  getServiceDetail: async (serviceId: string): Promise<ServiceDetailView> => {
    const res = await api.get(`/reliability/services/${serviceId}`);
    return res.data;
  },

  getSloCompliance: async (): Promise<any[]> => {
    const res = await api.get('/reliability/slo');
    return res.data;
  },

  getErrorBudgets: async (): Promise<ErrorBudgetOverview[]> => {
    const res = await api.get('/reliability/error-budget');
    return res.data;
  },

  getBurnRates: async (): Promise<any[]> => {
    const res = await api.get('/reliability/burn-rate');
    return res.data;
  },

  getRisks: async (): Promise<ReliabilityRiskItem[]> => {
    const res = await api.get('/reliability/risks');
    return res.data;
  },

  getForecasts: async (): Promise<SloForecastItem[]> => {
    const res = await api.get('/reliability/forecast');
    return res.data;
  },

  getDependencies: async (): Promise<DependencyImpactItem[]> => {
    const res = await api.get('/reliability/dependencies');
    return res.data;
  },

  getIncidents: async (): Promise<ReliabilityIncidentItem[]> => {
    const res = await api.get('/reliability/incidents');
    return res.data;
  },

  getRecommendations: async (): Promise<ReliabilityRecommendationItem[]> => {
    const res = await api.get('/reliability/recommendations');
    return res.data;
  },

  analyzeReliability: async (): Promise<ReliabilityAnalyzeResult> => {
    const res = await api.post('/reliability/analyze');
    return res.data;
  },
};
