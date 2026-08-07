import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { serverService, ServerItem } from "@/services/serverService";
import { alertService, AlertItem } from "@/services/alertService";
import { notificationService, NotificationItem } from "@/services/notificationService";
import { incidentService } from "@/services/incidentService";
import { costService } from "@/services/costService";

export function useServersQuery(params?: { provider?: string; status?: string; search?: string }) {
  return useQuery<ServerItem[]>({
    queryKey: ["servers", params],
    queryFn: () => serverService.getServers(params),
    staleTime: 15_000,
    refetchInterval: 30_000,
  });
}

export function useAlertsQuery(params?: { status?: string; severity?: string; search?: string }) {
  const queryClient = useQueryClient();

  const query = useQuery<AlertItem[]>({
    queryKey: ["alerts", params],
    queryFn: () => alertService.getAlerts(params),
    staleTime: 10_000,
    refetchInterval: 15_000,
  });

  const acknowledgeMutation = useMutation({
    mutationFn: (id: string) => alertService.acknowledgeAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  const resolveMutation = useMutation({
    mutationFn: (id: string) => alertService.resolveAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  const acknowledgeAllMutation = useMutation({
    mutationFn: () => alertService.acknowledgeAll(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  return {
    ...query,
    acknowledgeAlert: acknowledgeMutation.mutateAsync,
    resolveAlert: resolveMutation.mutateAsync,
    acknowledgeAllAlerts: acknowledgeAllMutation.mutateAsync,
  };
}

export function useNotificationsQuery(params?: { unread_only?: boolean; category?: string }) {
  const queryClient = useQueryClient();

  const query = useQuery<NotificationItem[]>({
    queryKey: ["notifications", params],
    queryFn: () => notificationService.getNotifications(params),
    staleTime: 15_000,
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => notificationService.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: () => notificationService.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  return {
    ...query,
    markRead: markReadMutation.mutateAsync,
    markAllRead: markAllReadMutation.mutateAsync,
  };
}

export function useIncidentsQuery() {
  return useQuery({
    queryKey: ["incidents"],
    queryFn: () => incidentService.getIncidents(),
    staleTime: 15_000,
  });
}

export function useCostSummaryQuery() {
  return useQuery({
    queryKey: ["cost-summary"],
    queryFn: () => costService.getCostSummary(),
    staleTime: 60_000,
  });
}
