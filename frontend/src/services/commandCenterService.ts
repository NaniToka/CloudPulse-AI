import api from '@/lib/api';
import {
  CommandCenterAnalyzeResult,
  CommandCenterOverview,
  ExecutiveBrief,
  ExecutiveHealth,
  ExecutiveTrendItem,
  IntelligenceInsight,
  OperationalRisk,
  TimelineItem,
  TopOpportunityItem,
  TopRiskItem,
} from '../types/commandCenter';

export interface FilterParams {
  provider?: string;
  service?: string;
  severity?: string;
}

export const commandCenterService = {
  getOverview: async (filters?: FilterParams): Promise<CommandCenterOverview> => {
    const res = await api.get('/command-center/overview', { params: filters });
    return res.data;
  },

  getHealth: async (): Promise<ExecutiveHealth> => {
    const res = await api.get('/command-center/health');
    return res.data;
  },

  getRisk: async (): Promise<OperationalRisk> => {
    const res = await api.get('/command-center/risk');
    return res.data;
  },

  getIncidents: async (): Promise<IntelligenceInsight[]> => {
    const res = await api.get('/command-center/incidents');
    return res.data;
  },

  getInsights: async (filters?: FilterParams): Promise<IntelligenceInsight[]> => {
    const res = await api.get('/command-center/insights', { params: filters });
    return res.data;
  },

  getTopRisks: async (): Promise<TopRiskItem[]> => {
    const res = await api.get('/command-center/risks');
    return res.data;
  },

  getOpportunities: async (): Promise<TopOpportunityItem[]> => {
    const res = await api.get('/command-center/opportunities');
    return res.data;
  },

  getTimeline: async (): Promise<TimelineItem[]> => {
    const res = await api.get('/command-center/timeline');
    return res.data;
  },

  getTrends: async (): Promise<ExecutiveTrendItem[]> => {
    const res = await api.get('/command-center/trends');
    return res.data;
  },

  getRecommendations: async (): Promise<TopOpportunityItem[]> => {
    const res = await api.get('/command-center/recommendations');
    return res.data;
  },

  analyzeCommandCenter: async (): Promise<CommandCenterAnalyzeResult> => {
    const res = await api.post('/command-center/analyze');
    return res.data;
  },
};
