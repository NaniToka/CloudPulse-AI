import api from '@/lib/api';
import {
  RemediationActionItem,
  RemediationAnalyzeResult,
  RemediationAuditItem,
  RemediationDryRunResult,
  RemediationExecution,
  RemediationOverview,
  RemediationPlan,
  RemediationPolicy,
} from '../types/remediation';

export interface RemediationFilterParams {
  status?: string;
  provider?: string;
  risk_level?: string;
}

export const remediationService = {
  getOverview: async (): Promise<RemediationOverview> => {
    const res = await api.get('/remediation/overview');
    return res.data;
  },

  getActions: async (filters?: RemediationFilterParams): Promise<RemediationPlan[]> => {
    const res = await api.get('/remediation/actions', { params: filters });
    return res.data;
  },

  getActionDefinitions: async (): Promise<RemediationActionItem[]> => {
    const res = await api.get('/remediation/actions/definitions');
    return res.data;
  },

  getActionDetail: async (planId: string): Promise<RemediationPlan> => {
    const res = await api.get(`/remediation/actions/${planId}`);
    return res.data;
  },

  createAction: async (payload: any): Promise<RemediationPlan> => {
    const res = await api.post('/remediation/actions', payload);
    return res.data;
  },

  dryRunAction: async (planId: string): Promise<RemediationDryRunResult> => {
    const res = await api.post(`/remediation/actions/${planId}/dry-run`);
    return res.data;
  },

  approveAction: async (planId: string, comments?: string): Promise<any> => {
    const res = await api.post(`/remediation/actions/${planId}/approve`, { comments });
    return res.data;
  },

  rejectAction: async (planId: string, rejection_reason: string): Promise<any> => {
    const res = await api.post(`/remediation/actions/${planId}/reject`, { rejection_reason });
    return res.data;
  },

  executeAction: async (planId: string, mode?: string): Promise<any> => {
    const res = await api.post(`/remediation/actions/${planId}/execute`, { execution_mode: mode });
    return res.data;
  },

  rollbackAction: async (executionId: string): Promise<any> => {
    const res = await api.post(`/remediation/actions/${executionId}/rollback`);
    return res.data;
  },

  getExecutions: async (): Promise<RemediationExecution[]> => {
    const res = await api.get('/remediation/executions');
    return res.data;
  },

  getPolicies: async (): Promise<RemediationPolicy[]> => {
    const res = await api.get('/remediation/policies');
    return res.data;
  },

  createPolicy: async (payload: any): Promise<RemediationPolicy> => {
    const res = await api.post('/remediation/policies', payload);
    return res.data;
  },

  updatePolicy: async (policyId: string, payload: any): Promise<RemediationPolicy> => {
    const res = await api.put(`/remediation/policies/${policyId}`, payload);
    return res.data;
  },

  getAuditLogs: async (): Promise<RemediationAuditItem[]> => {
    const res = await api.get('/remediation/audit');
    return res.data;
  },

  analyzeRemediation: async (): Promise<RemediationAnalyzeResult> => {
    const res = await api.post('/remediation/analyze');
    return res.data;
  },
};
