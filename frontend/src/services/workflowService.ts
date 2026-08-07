import apiClient from "@/lib/api";

export interface WorkflowItem {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  status: "active" | "paused" | "draft" | string;
  trigger_type: string;
  trigger_config?: Record<string, any>;
  nodes: Array<{
    id: string;
    type: "trigger" | "action" | "condition" | "approval" | "ai" | string;
    label: string;
    position: { x: number; y: number };
    config?: Record<string, any>;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    condition?: string;
  }>;
  tags: string[];
  version: number;
  created_at: string;
  updated_at: string;
}

export interface WorkflowExecutionItem {
  id: string;
  workflow_id: string;
  status: "running" | "completed" | "failed" | "awaiting_approval" | "rolled_back" | string;
  trigger_source: string;
  trigger_payload: Record<string, any>;
  duration_ms?: number;
  started_at: string;
  completed_at?: string;
  error_message?: string;
  context_variables: Record<string, any>;
  step_results: Array<{
    node_id: string;
    label: string;
    status: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface WorkflowTemplateItem {
  id: string;
  name: string;
  category: string;
  description: string;
  trigger_type: string;
  nodes: any[];
  edges: any[];
  tags: string[];
  icon: string;
  created_at: string;
}

export interface WorkflowApprovalDecisionPayload {
  approval_id: string;
  decision: "approved" | "rejected";
  reason?: string;
}

export const workflowService = {
  getWorkflows: async (params?: { status?: string; trigger_type?: string; search?: string }): Promise<WorkflowItem[]> => {
    const response = await apiClient.get<WorkflowItem[]>("/workflows", { params });
    return response.data;
  },

  getWorkflowById: async (id: string): Promise<WorkflowItem> => {
    const response = await apiClient.get<WorkflowItem>(`/workflows/${id}`);
    return response.data;
  },

  createWorkflow: async (payload: Partial<WorkflowItem>): Promise<WorkflowItem> => {
    const response = await apiClient.post<WorkflowItem>("/workflows", payload);
    return response.data;
  },

  updateWorkflow: async (id: string, payload: Partial<WorkflowItem>): Promise<WorkflowItem> => {
    const response = await apiClient.put<WorkflowItem>(`/workflows/${id}`, payload);
    return response.data;
  },

  deleteWorkflow: async (id: string): Promise<void> => {
    await apiClient.delete(`/workflows/${id}`);
  },

  executeWorkflow: async (id: string): Promise<WorkflowExecutionItem> => {
    const response = await apiClient.post<WorkflowExecutionItem>(`/workflows/${id}/execute`);
    return response.data;
  },

  approveWorkflow: async (id: string, payload: WorkflowApprovalDecisionPayload): Promise<WorkflowExecutionItem> => {
    const response = await apiClient.post<WorkflowExecutionItem>(`/workflows/${id}/approve`, payload);
    return response.data;
  },

  getHistory: async (params?: { workflow_id?: string; status?: string }): Promise<WorkflowExecutionItem[]> => {
    const response = await apiClient.get<WorkflowExecutionItem[]>("/workflows/history", { params });
    return response.data;
  },

  getTemplates: async (params?: { category?: string }): Promise<WorkflowTemplateItem[]> => {
    const response = await apiClient.get<WorkflowTemplateItem[]>("/workflows/templates", { params });
    return response.data;
  },

  generateAIWorkflow: async (prompt: string): Promise<Partial<WorkflowItem>> => {
    const response = await apiClient.post<Partial<WorkflowItem>>("/workflows/generate-ai", { prompt });
    return response.data;
  },
};
