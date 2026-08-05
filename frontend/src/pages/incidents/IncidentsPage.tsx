/**
 * AI Incident Management Center — Main Page
 */

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, RefreshCw, Radio, BarChart2, ShieldAlert } from "lucide-react";

import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/useToast";

import { incidentService } from "@/services/incidentService";
import { useIncidentWebsocket } from "@/hooks/useIncidentWebsocket";
import { IncidentTable } from "@/components/incidents/IncidentTable";
import { CreateIncidentModal } from "@/components/incidents/CreateIncidentModal";
import { EditIncidentModal } from "@/components/incidents/EditIncidentModal";
import { IncidentDetailsModal } from "@/components/incidents/IncidentDetailsModal";
import { IncidentAnalyticsCharts } from "@/components/incidents/IncidentAnalyticsCharts";
import type { Incident, IncidentCreatePayload, IncidentUpdatePayload, IncidentStatus } from "@/types/incident";

export default function IncidentsPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // State
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [serviceFilter, setServiceFilter] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortDir, setSortDir] = useState("desc");

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingIncident, setEditingIncident] = useState<Incident | null>(null);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);

  // WebSocket Hook
  const { isConnected } = useIncidentWebsocket();

  // React Query — List Incidents
  const {
    data: incidentListData,
    isLoading: isListLoading,
    refetch: refetchList,
  } = useQuery({
    queryKey: ["incidents", page, search, severityFilter, statusFilter, serviceFilter, sortBy, sortDir],
    queryFn: () =>
      incidentService.getIncidents({
        page,
        size: 10,
        search: search || undefined,
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
        service: serviceFilter || undefined,
        sort_by: sortBy,
        sort_dir: sortDir,
      }),
  });

  // React Query — KPI Stats
  const { data: statsData } = useQuery({
    queryKey: ["incident-stats"],
    queryFn: () => incidentService.getStats(),
  });

  // React Query — Analytics
  const { data: analyticsData, isLoading: isAnalyticsLoading } = useQuery({
    queryKey: ["incident-analytics"],
    queryFn: () => incidentService.getAnalytics(),
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: (payload: IncidentCreatePayload) => incidentService.createIncident(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["incident-stats"] });
      queryClient.invalidateQueries({ queryKey: ["incident-analytics"] });
      toast({
        title: "Incident Created",
        description: "New incident opened and Gemini AI analysis triggered successfully.",
      });
    },
    onError: (err: any) => {
      toast({
        title: "Failed to create incident",
        description: err?.response?.data?.detail || "An unexpected error occurred.",
        variant: "destructive",
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: IncidentUpdatePayload }) =>
      incidentService.updateIncident(id, payload),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["incident-stats"] });
      queryClient.invalidateQueries({ queryKey: ["incident-analytics"] });
      if (selectedIncident && selectedIncident.id === updated.id) {
        setSelectedIncident(updated);
      }
      toast({
        title: "Incident Updated",
        description: `Incident details saved.`,
      });
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: IncidentStatus }) =>
      incidentService.updateIncident(id, { status }),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["incident-stats"] });
      queryClient.invalidateQueries({ queryKey: ["incident-analytics"] });
      if (selectedIncident && selectedIncident.id === updated.id) {
        setSelectedIncident(updated);
      }
      toast({
        title: `Status Updated`,
        description: `Incident status set to '${updated.status}'.`,
      });
    },
  });

  const resolveMutation = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) =>
      incidentService.resolveIncident(id, { resolution_notes: notes }),
    onSuccess: (resolved) => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["incident-stats"] });
      queryClient.invalidateQueries({ queryKey: ["incident-analytics"] });
      if (selectedIncident && selectedIncident.id === resolved.id) {
        setSelectedIncident(resolved);
      }
      toast({
        title: "Incident Resolved",
        description: "Resolution notes saved and incident marked resolved.",
      });
    },
  });

  const reanalyzeMutation = useMutation({
    mutationFn: (id: string) => incidentService.reanalyzeIncident(id),
    onSuccess: async (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      const updated = await incidentService.getIncidentById(id);
      setSelectedIncident(updated);
      toast({
        title: "AI Re-analysis Complete",
        description: "Fresh Gemini diagnostics generated for incident.",
      });
    },
  });

  const handleSortChange = (field: string) => {
    if (sortBy === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortDir("desc");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <PageHeader
        title="Incident Management System"
        subtitle="PagerDuty & Datadog style enterprise incident response, Gemini AI root-cause diagnostics, and real-time SRE triage"
        actions={
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-bg-surface border border-white/10 text-xs">
              <Radio className={`h-3 w-3 ${isConnected ? "text-emerald-400 animate-pulse" : "text-amber-400"}`} />
              <span className="text-muted-foreground">
                WS: <span className={isConnected ? "text-emerald-400 font-medium" : "text-amber-400"}>{isConnected ? "Live" : "Connecting"}</span>
              </span>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => refetchList()}
              className="gap-2 text-xs"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Refresh
            </Button>

            <Button
              size="sm"
              onClick={() => setIsCreateModalOpen(true)}
              className="gap-2 bg-brand-purple hover:bg-brand-purple/90 text-white text-xs"
            >
              <Plus className="h-3.5 w-3.5" /> Create Incident
            </Button>
          </div>
        }
      />

      {/* Top KPI Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="Open Incidents"
          value={statsData?.open_incidents.toString() || "0"}
          subValue="Active triage queue"
        />
        <StatCard
          label="Critical Incidents"
          value={statsData?.critical_incidents.toString() || "0"}
          subValue="P0 / P1 severe outages"
        />
        <StatCard
          label="Avg Resolution Time"
          value={`${statsData?.avg_resolution_time_minutes || 24.5}m`}
          subValue="Mean Time To Resolve (MTTR)"
        />
        <StatCard
          label="SLA Compliance"
          value={`${statsData?.sla_compliance_percent || 98.4}%`}
          subValue="Target resolution window"
        />
      </div>

      {/* Main Tabs: Live Directory vs Analytics */}
      <Tabs defaultValue="directory" className="w-full space-y-4">
        <TabsList className="bg-bg-surface border border-white/10 p-1">
          <TabsTrigger value="directory" className="gap-2 text-xs">
            <ShieldAlert className="h-3.5 w-3.5" /> Active Directory & Triage
          </TabsTrigger>
          <TabsTrigger value="analytics" className="gap-2 text-xs">
            <BarChart2 className="h-3.5 w-3.5" /> Incident Analytics & Trends
          </TabsTrigger>
        </TabsList>

        {/* Directory Tab */}
        <TabsContent value="directory" className="space-y-4">
          <IncidentTable
            incidents={incidentListData?.items || []}
            total={incidentListData?.total || 0}
            page={incidentListData?.page || 1}
            pages={incidentListData?.pages || 1}
            isLoading={isListLoading}
            search={search}
            onSearchChange={setSearch}
            severityFilter={severityFilter}
            onSeverityFilterChange={setSeverityFilter}
            statusFilter={statusFilter}
            onStatusFilterChange={setStatusFilter}
            serviceFilter={serviceFilter}
            onServiceFilterChange={setServiceFilter}
            sortBy={sortBy}
            sortDir={sortDir}
            onSortChange={handleSortChange}
            onPageChange={setPage}
            onSelectIncident={(inc) => setSelectedIncident(inc)}
            onEditIncident={(inc) => setEditingIncident(inc)}
            onQuickResolve={(inc) => setSelectedIncident(inc)}
          />
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <IncidentAnalyticsCharts analytics={analyticsData} isLoading={isAnalyticsLoading} />
        </TabsContent>
      </Tabs>

      {/* Create Modal */}
      <CreateIncidentModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={async (payload) => {
          await createMutation.mutateAsync(payload);
        }}
        isSubmitting={createMutation.isPending}
      />

      {/* Edit Modal */}
      <EditIncidentModal
        incident={editingIncident}
        isOpen={!!editingIncident}
        onClose={() => setEditingIncident(null)}
        onSubmit={async (id, payload) => {
          await updateMutation.mutateAsync({ id, payload });
        }}
        isSubmitting={updateMutation.isPending}
      />

      {/* Details & Resolution Modal */}
      <IncidentDetailsModal
        incident={selectedIncident}
        isOpen={!!selectedIncident}
        onClose={() => setSelectedIncident(null)}
        onResolve={async (id, notes) => {
          await resolveMutation.mutateAsync({ id, notes });
        }}
        onReanalyze={async (id) => {
          await reanalyzeMutation.mutateAsync(id);
        }}
        onUpdateStatus={async (id, status) => {
          await updateStatusMutation.mutateAsync({ id, status });
        }}
        isResolving={resolveMutation.isPending}
        isAnalyzing={reanalyzeMutation.isPending}
      />
    </div>
  );
}
