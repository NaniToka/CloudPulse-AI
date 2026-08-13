import api from '@/lib/api';
import {
  ActionDefinition,
  AutonomousOverview,
  AutonomyPolicy,
  RemediationAuditLog,
  RemediationExecution,
  RemediationPlan,
  SimulationResult,
} from '../types/autonomous';

export const autonomousService = {
  getOverview: async (): Promise<AutonomousOverview> => {
    const res = await api.get('/autonomous/overview');
    return res.data;
  },

  getConfig: async (): Promise<AutonomyPolicy> => {
    const res = await api.get('/autonomous/config');
    return res.data;
  },

  updateConfig: async (payload: Partial<AutonomyPolicy>): Promise<AutonomyPolicy> => {
    const res = await api.put('/autonomous/config', payload);
    return res.data;
  },

  listActions: async (): Promise<ActionDefinition[]> => {
    const res = await api.get('/autonomous/actions');
    return res.data;
  },

  listPlans: async (status?: string): Promise<RemediationPlan[]> => {
    const res = await api.get('/autonomous/plans', { params: { status } });
    return res.data;
  },

  createPlan: async (payload: Partial<RemediationPlan>): Promise<RemediationPlan> => {
    const res = await api.post('/autonomous/plans', payload);
    return res.data;
  },

  validatePlan: async (planId: string) => {
    const res = await api.post(`/autonomous/plans/${planId}/validate`);
    return res.data;
  },

  approvePlan: async (planId: string): Promise<RemediationPlan> => {
    const res = await api.post(`/autonomous/plans/${planId}/approve`);
    return res.data;
  },

  executePlan: async (planId: string, mode?: string) => {
    const res = await api.post(`/autonomous/plans/${planId}/execute`, null, { params: { mode } });
    return res.data;
  },

  rollbackPlan: async (planId: string) => {
    const res = await api.post(`/autonomous/plans/${planId}/rollback`);
    return res.data;
  },

  listExecutions: async (): Promise<RemediationExecution[]> => {
    const res = await api.get('/autonomous/executions');
    return res.data;
  },

  getQueue: async (): Promise<RemediationExecution[]> => {
    const res = await api.get('/autonomous/queue');
    return res.data;
  },

  getAuditLogs: async (): Promise<RemediationAuditLog[]> => {
    const res = await api.get('/autonomous/audit');
    return res.data;
  },

  simulateAction: async (payload: {
    action_type: string;
    affected_resource: string;
    provider?: string;
    environment?: string;
    execution_mode?: string;
  }): Promise<SimulationResult> => {
    const res = await api.post('/autonomous/simulate', payload);
    return res.data;
  },
};
