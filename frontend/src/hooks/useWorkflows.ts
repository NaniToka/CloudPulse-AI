import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  workflowService,
  WorkflowItem,
  WorkflowExecutionItem,
  WorkflowTemplateItem,
  WorkflowApprovalDecisionPayload,
} from "@/services/workflowService";

export function useWorkflows(params?: { status?: string; trigger_type?: string; search?: string }) {
  return useQuery<WorkflowItem[]>({
    queryKey: ["workflows", params],
    queryFn: () => workflowService.getWorkflows(params),
    staleTime: 15_000,
  });
}

export function useWorkflowDetails(id?: string) {
  return useQuery<WorkflowItem>({
    queryKey: ["workflow-detail", id],
    queryFn: () => workflowService.getWorkflowById(id!),
    enabled: Boolean(id),
    staleTime: 10_000,
  });
}

export function useWorkflowHistory(params?: { workflow_id?: string; status?: string }) {
  return useQuery<WorkflowExecutionItem[]>({
    queryKey: ["workflow-history", params],
    queryFn: () => workflowService.getHistory(params),
    staleTime: 10_000,
    refetchInterval: 15_000,
  });
}

export function useWorkflowTemplates(params?: { category?: string }) {
  return useQuery<WorkflowTemplateItem[]>({
    queryKey: ["workflow-templates", params],
    queryFn: () => workflowService.getTemplates(params),
    staleTime: 60_000,
  });
}

export function useWorkflowMutations() {
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (payload: Partial<WorkflowItem>) => workflowService.createWorkflow(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<WorkflowItem> }) =>
      workflowService.updateWorkflow(id, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
      queryClient.invalidateQueries({ queryKey: ["workflow-detail", variables.id] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => workflowService.deleteWorkflow(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
    },
  });

  const executeMutation = useMutation({
    mutationFn: (id: string) => workflowService.executeWorkflow(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-history"] });
    },
  });

  const approveMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: WorkflowApprovalDecisionPayload }) =>
      workflowService.approveWorkflow(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-history"] });
    },
  });

  const generateAIMutation = useMutation({
    mutationFn: (prompt: string) => workflowService.generateAIWorkflow(prompt),
  });

  return {
    createWorkflow: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    updateWorkflow: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    deleteWorkflow: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
    executeWorkflow: executeMutation.mutateAsync,
    isExecuting: executeMutation.isPending,
    approveWorkflow: approveMutation.mutateAsync,
    isApproving: approveMutation.isPending,
    generateAIWorkflow: generateAIMutation.mutateAsync,
    isGeneratingAI: generateAIMutation.isPending,
  };
}
