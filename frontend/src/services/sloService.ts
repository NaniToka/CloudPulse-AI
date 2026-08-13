import api from '@/lib/api';
import {
  BurnRate,
  CorrelatedIncident,
  ErrorBudget,
  ServiceReliability,
  SliMetrics,
  SloAnalyzeResult,
  SloForecast,
  SloObjective,
  SloOverview,
  SloViolation,
} from '../types/slo';

export const sloService = {
  getOverview: async (): Promise<SloOverview> => {
    const res = await api.get('/slo/overview');
    return res.data;
  },

  getServices: async (service?: string): Promise<ServiceReliability[]> => {
    const res = await api.get('/slo/services', { params: { service } });
    return res.data;
  },

  getServiceDetails: async (service: string): Promise<ServiceReliability> => {
    const res = await api.get(`/slo/services/${service}`);
    return res.data;
  },

  getIndicators: async (service?: string): Promise<SliMetrics[]> => {
    const res = await api.get('/slo/indicators', { params: { service } });
    return res.data;
  },

  getObjectives: async (service?: string): Promise<SloObjective[]> => {
    const res = await api.get('/slo/objectives', { params: { service } });
    return res.data;
  },

  createObjective: async (payload: Partial<SloObjective>): Promise<SloObjective> => {
    const res = await api.post('/slo/objectives', payload);
    return res.data;
  },

  updateObjective: async (id: string, payload: Partial<SloObjective>): Promise<SloObjective> => {
    const res = await api.put(`/slo/objectives/${id}`, payload);
    return res.data;
  },

  deleteObjective: async (id: string): Promise<void> => {
    await api.delete(`/slo/objectives/${id}`);
  },

  getErrorBudgets: async (service?: string): Promise<ErrorBudget[]> => {
    const res = await api.get('/slo/error-budget', { params: { service } });
    return res.data;
  },

  getBurnRates: async (service?: string): Promise<BurnRate[]> => {
    const res = await api.get('/slo/burn-rate', { params: { service } });
    return res.data;
  },

  getViolations: async (service?: string, severity?: string): Promise<SloViolation[]> => {
    const res = await api.get('/slo/violations', { params: { service, severity } });
    return res.data;
  },

  getForecasts: async (service?: string): Promise<SloForecast[]> => {
    const res = await api.get('/slo/forecast', { params: { service } });
    return res.data;
  },

  getIncidents: async (service?: string): Promise<CorrelatedIncident[]> => {
    const res = await api.get('/slo/incidents', { params: { service } });
    return res.data;
  },

  analyzeSlos: async (): Promise<SloAnalyzeResult> => {
    const res = await api.post('/slo/analyze');
    return res.data;
  },
};
