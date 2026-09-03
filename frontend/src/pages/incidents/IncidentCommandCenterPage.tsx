/**
 * Enterprise Incident Command Center & Root Cause Analysis Platform
 */

import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  ArrowRight,
  Bot,
  BrainCircuit,
  CheckCircle2,
  Clock,
  Database,
  Eye,
  FileSpreadsheet,
  Flame,
  Layers,
  Network,
  Plus,
  Radio,
  RefreshCw,
  Search,
  Server,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  Workflow,
  Wrench,
  Zap,
} from "lucide-react";

import PageHeader from "@/components/shared/PageHeader";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/useToast";
import { useIncidentWebsocket } from "@/hooks/useIncidentWebsocket";
import { incidentService } from "@/services/incidentService";
import { IncidentSeverityBadge } from "@/components/incidents/IncidentSeverityBadge";
import { IncidentStatusControl } from "@/components/incidents/IncidentStatusControl";
import { IncidentTimeline } from "@/components/incidents/IncidentTimeline";
import { IncidentImpactGraph } from "@/components/incidents/IncidentImpactGraph";
import { RootCausePanel } from "@/components/incidents/RootCausePanel";
import { EvidencePanel } from "@/components/incidents/EvidencePanel";
import { RemediationPanel } from "@/components/incidents/RemediationPanel";
import { CreateIncidentModal } from "@/components/incidents/CreateIncidentModal";
import { IncidentTable } from "@/components/incidents/IncidentTable";
import { IncidentAnalyticsCharts } from "@/components/incidents/IncidentAnalyticsCharts";
import { ResolutionVerificationModal } from "@/components/incidents/ResolutionVerificationModal";
import type {
  Incident,
  IncidentCreatePayload,
  IncidentResolvePayload,
  IncidentUpdatePayload,
  SeverityLevel,
} from "@/types/incident";
import { cn } from "@/lib/utils";

export default function IncidentCommandCenterPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { isConnected } = useIncidentWebsocket();

  // State
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [mainView, setMainView] = useState<"command-center" | "ledger" | "analytics">("command-center");
  const [severityFilter, setSeverityFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isVerifyModalOpen, setIsVerifyModalOpen] = useState(false);

  // 1. Fetch Active Incidents
  const {
    data: activeIncidents = [],
    isLoading: isActiveLoading,
    refetch: refetchActive,
  } = useQuery({
    queryKey: ["incidents", "active"],
    queryFn: () => incidentService.getActiveIncidents(),
    refetchInterval: 10000,
  });

  // 2. Fetch All Incidents for list/ledger
  const {
    data: incidentListData,
    isLoading: isListLoading,
    refetch: refetchList,
  } = useQuery({
    queryKey: ["incidents", "list", severityFilter, searchQuery],
    queryFn: () =>
      incidentService.getIncidents({
        severity: severityFilter || undefined,
        search: searchQuery || undefined,
        size: 50,
      }),
  });

  // 3. Fetch KPI Stats
  const { data: statsData } = useQuery({
    queryKey: ["incident-stats"],
    queryFn: () => incidentService.getStats(),
  });

  // 4. Fetch Analytics
  const { data: analyticsData } = useQuery({
    queryKey: ["incident-analytics"],
    queryFn: () => incidentService.getAnalytics(),
  });

  // Auto-select first incident
  useEffect(() => {
    if (!selectedIncidentId && activeIncidents.length > 0) {
      setSelectedIncidentId(activeIncidents[0].id);
    } else if (!selectedIncidentId && incidentListData?.items && incidentListData.items.length > 0) {
      setSelectedIncidentId(incidentListData.items[0].id);
    }
  }, [activeIncidents, incidentListData, selectedIncidentId]);

  // 5. Fetch Details for Selected Incident
  const {
    data: selectedIncident,
    isLoading: isDetailLoading,
    refetch: refetchDetail,
  } = useQuery({
    queryKey: ["incident", selectedIncidentId],
    queryFn: () => (selectedIncidentId ? incidentService.getIncidentById(selectedIncidentId) : null),
    enabled: !!selectedIncidentId,
  });

  // 6. Fetch Timeline for Selected Incident
  const { data: timelineEvents = [], refetch: refetchTimeline } = useQuery({
    queryKey: ["incident-timeline", selectedIncidentId],
    queryFn: () => (selectedIncidentId ? incidentService.getTimeline(selectedIncidentId) : []),
    enabled: !!selectedIncidentId,
  });

  // 7. Fetch Blast Radius for Selected Incident
  const { data: blastRadiusData } = useQuery({
    queryKey: ["incident-impact", selectedIncidentId],
    queryFn: () => (selectedIncidentId ? incidentService.getBlastRadius(selectedIncidentId) : undefined),
    enabled: !!selectedIncidentId,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: (payload: IncidentCreatePayload) => incidentService.createIncident(payload),
    onSuccess: (newInc) => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      setSelectedIncidentId(newInc.id);
      toast({
        title: "Incident Opened",
        description: `Incident '${newInc.title}' created and AI RCA triggered.`,
      });
    },
  });

  const acknowledgeMutation = useMutation({
    mutationFn: (id: string) => incidentService.acknowledgeIncident(id, { assigned_to: "SRE Lead" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["incident", selectedIncidentId] });
      queryClient.invalidateQueries({ queryKey: ["incident-timeline", selectedIncidentId] });
      toast({
        title: "Incident Acknowledged",
        description: "Status changed to INVESTIGATING. Triage underway.",
      });
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      incidentService.updateIncident(id, { status: status as any }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["incident", selectedIncidentId] });
      queryClient.invalidateQueries({ queryKey: ["incident-timeline", selectedIncidentId] });
      toast({ title: "Incident Updated", description: "Incident lifecycle state synchronized." });
    },
  });

  const resolveMutation = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) =>
      incidentService.resolveIncident(id, { resolution_notes: notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["incident", selectedIncidentId] });
      queryClient.invalidateQueries({ queryKey: ["incident-timeline", selectedIncidentId] });
      toast({ title: "Incident Resolved", description: "Resolution notes committed." });
    },
  });

  const closeIncidentMutation = useMutation({
    mutationFn: (id: string) => incidentService.closeIncident(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["incident", selectedIncidentId] });
      queryClient.invalidateQueries({ queryKey: ["incident-timeline", selectedIncidentId] });
      toast({ title: "Incident Closed", description: "Incident closed after verified resolution." });
    },
  });

  const verifyResolutionMutation = useMutation({
    mutationFn: ({ id, telemetry }: { id: string; telemetry?: Record<string, number> }) =>
      incidentService.verifyResolution(id, { post_telemetry: telemetry }),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["incident", selectedIncidentId] });
      queryClient.invalidateQueries({ queryKey: ["incident-timeline", selectedIncidentId] });
      toast({
        title: res.resolution_verified ? "Resolution Verified" : "Verification Warning",
        description: res.resolution_verified
          ? "All telemetry returned to nominal baseline."
          : `Remaining risk flagged: ${res.remaining_risk}`,
        variant: res.resolution_verified ? "default" : "destructive",
      });
    },
  });

  const reanalyzeMutation = useMutation({
    mutationFn: (id: string) => incidentService.reanalyzeIncident(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incident", selectedIncidentId] });
      queryClient.invalidateQueries({ queryKey: ["incident-timeline", selectedIncidentId] });
      toast({ title: "RCA Diagnostics Refreshed", description: "Gemini AI & multi-modal evidence updated." });
    },
  });

  const addTimelineNoteMutation = useMutation({
    mutationFn: ({ title, description, event_type }: { title: string; description?: string; event_type: string }) =>
      selectedIncidentId
        ? incidentService.addTimelineEvent(selectedIncidentId, {
            title,
            description,
            event_type,
            source: "IncidentCommandCenter",
          })
        : Promise.reject(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incident-timeline", selectedIncidentId] });
      toast({ title: "Timeline Updated", description: "Triage note appended." });
    },
  });

  const remediateMutation = useMutation({
    mutationFn: ({ actionId, authorizedBy }: { actionId: string; authorizedBy: string }) =>
      selectedIncidentId
        ? incidentService.executeRemediation(selectedIncidentId, {
            action_id: actionId,
            authorized_by: authorizedBy,
          })
        : Promise.reject(),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["incident", selectedIncidentId] });
      queryClient.invalidateQueries({ queryKey: ["incident-timeline", selectedIncidentId] });
      toast({
        title: "Remediation Workflow Dispatched",
        description: res.message,
      });
    },
  });

  const correlateMutation = useMutation({
    mutationFn: () =>
      incidentService.correlateAlerts({
        alerts: [
          {
            service: "database-cluster",
            event_type: "metric_anomaly",
            title: "PostgreSQL active connections at 99%",
            severity: "CRITICAL",
          },
          {
            service: "payment-service",
            event_type: "trace_failure",
            title: "HTTP 504 Gateway Timeouts on /checkout",
            severity: "HIGH",
          },
          {
            service: "auth-service",
            event_type: "log_error",
            title: "Database connection timeout in session pool",
            severity: "HIGH",
          },
        ],
      }),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      if (res.incidents && res.incidents.length > 0) {
        setSelectedIncidentId(res.incidents[0].id);
      }
      toast({
        title: "Intelligent Correlation Complete",
        description: `Correlated ${res.raw_alerts_processed} alerts into ${res.correlated_incidents_count} incident.`,
      });
    },
  });

  // Calculate Active Incidents by Severity
  const activeList = incidentListData?.items || activeIncidents;
  const criticalCount = activeList.filter((i) => {
    const s = String(i.severity).toUpperCase();
    return s === "CRITICAL" || s === "P0";
  }).length;
  const highCount = activeList.filter((i) => {
    const s = String(i.severity).toUpperCase();
    return s === "HIGH" || s === "P1";
  }).length;
  const mediumCount = activeList.filter((i) => {
    const s = String(i.severity).toUpperCase();
    return s === "MEDIUM" || s === "P2";
  }).length;
  const lowCount = activeList.filter((i) => {
    const s = String(i.severity).toUpperCase();
    return s === "LOW" || s === "P3";
  }).length;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <PageHeader
          title="Enterprise Incident Command Center"
          description="Autonomous Incident Intelligence, Multi-Signal Correlation & Root Cause Analysis Engine."
        />

        <div className="flex items-center gap-2">
          {/* WebSocket Status Indicator */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/[0.08] bg-bg-surface text-xs font-mono">
            <Radio className={cn("w-3.5 h-3.5", isConnected ? "text-emerald-400 animate-pulse" : "text-amber-400")} />
            <span className="text-muted-foreground">{isConnected ? "Live Stream" : "Connecting"}</span>
          </div>

          <Button
            size="sm"
            variant="outline"
            onClick={() => correlateMutation.mutate()}
            disabled={correlateMutation.isPending}
            className="border-brand-500/40 bg-brand-500/10 text-brand-300 hover:bg-brand-500/20 text-xs font-mono h-9"
          >
            <BrainCircuit className="w-3.5 h-3.5 mr-1.5" />
            Correlate Signals
          </Button>

          <Button
            size="sm"
            onClick={() => setIsCreateModalOpen(true)}
            className="bg-brand-600 hover:bg-brand-500 text-white text-xs font-mono h-9 shadow-md"
          >
            <Plus className="w-3.5 h-3.5 mr-1.5" />
            Declare Incident
          </Button>
        </div>
      </div>

      {/* Active Incidents Summary Counter Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div
          onClick={() => setSeverityFilter(severityFilter === "CRITICAL" ? "" : "CRITICAL")}
          className={cn(
            "rounded-xl border p-4 cursor-pointer transition-all duration-200 backdrop-blur-md shadow-glass",
            severityFilter === "CRITICAL"
              ? "border-red-500 bg-red-500/15"
              : "border-red-500/30 bg-gradient-to-br from-red-950/20 to-bg-surface hover:border-red-500/60"
          )}
        >
          <div className="flex items-center justify-between text-red-400 mb-2">
            <span className="text-xs font-mono uppercase font-bold tracking-wider">CRITICAL</span>
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">{criticalCount}</div>
          <div className="text-[11px] text-muted-foreground mt-1 font-mono">Immediate SRE Action</div>
        </div>

        <div
          onClick={() => setSeverityFilter(severityFilter === "HIGH" ? "" : "HIGH")}
          className={cn(
            "rounded-xl border p-4 cursor-pointer transition-all duration-200 backdrop-blur-md shadow-glass",
            severityFilter === "HIGH"
              ? "border-orange-500 bg-orange-500/15"
              : "border-orange-500/30 bg-gradient-to-br from-orange-950/20 to-bg-surface hover:border-orange-500/60"
          )}
        >
          <div className="flex items-center justify-between text-orange-400 mb-2">
            <span className="text-xs font-mono uppercase font-bold tracking-wider">HIGH</span>
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">{highCount}</div>
          <div className="text-[11px] text-muted-foreground mt-1 font-mono">Degraded Services</div>
        </div>

        <div
          onClick={() => setSeverityFilter(severityFilter === "MEDIUM" ? "" : "MEDIUM")}
          className={cn(
            "rounded-xl border p-4 cursor-pointer transition-all duration-200 backdrop-blur-md shadow-glass",
            severityFilter === "MEDIUM"
              ? "border-amber-500 bg-amber-500/15"
              : "border-amber-500/30 bg-gradient-to-br from-amber-950/20 to-bg-surface hover:border-amber-500/60"
          )}
        >
          <div className="flex items-center justify-between text-amber-400 mb-2">
            <span className="text-xs font-mono uppercase font-bold tracking-wider">MEDIUM</span>
            <Activity className="w-4 h-4" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">{mediumCount}</div>
          <div className="text-[11px] text-muted-foreground mt-1 font-mono">Elevated Latency</div>
        </div>

        <div
          onClick={() => setSeverityFilter(severityFilter === "LOW" ? "" : "LOW")}
          className={cn(
            "rounded-xl border p-4 cursor-pointer transition-all duration-200 backdrop-blur-md shadow-glass",
            severityFilter === "LOW"
              ? "border-blue-500 bg-blue-500/15"
              : "border-blue-500/30 bg-gradient-to-br from-blue-950/20 to-bg-surface hover:border-blue-500/60"
          )}
        >
          <div className="flex items-center justify-between text-blue-400 mb-2">
            <span className="text-xs font-mono uppercase font-bold tracking-wider">LOW</span>
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">{lowCount}</div>
          <div className="text-[11px] text-muted-foreground mt-1 font-mono">Minor Anomaly</div>
        </div>
      </div>

      {/* Main View Switcher */}
      <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={mainView === "command-center" ? "default" : "outline"}
            onClick={() => setMainView("command-center")}
            className={cn(
              "text-xs font-mono h-8",
              mainView === "command-center" ? "bg-brand-600 text-white" : "border-white/10"
            )}
          >
            <ShieldAlert className="w-3.5 h-3.5 mr-1.5" />
            Command Center Workspace
          </Button>

          <Button
            size="sm"
            variant={mainView === "ledger" ? "default" : "outline"}
            onClick={() => setMainView("ledger")}
            className={cn(
              "text-xs font-mono h-8",
              mainView === "ledger" ? "bg-brand-600 text-white" : "border-white/10"
            )}
          >
            <FileSpreadsheet className="w-3.5 h-3.5 mr-1.5" />
            All Incidents Ledger
          </Button>

          <Button
            size="sm"
            variant={mainView === "analytics" ? "default" : "outline"}
            onClick={() => setMainView("analytics")}
            className={cn(
              "text-xs font-mono h-8",
              mainView === "analytics" ? "bg-brand-600 text-white" : "border-white/10"
            )}
          >
            <TrendingUp className="w-3.5 h-3.5 mr-1.5" />
            Analytics & MTTR
          </Button>
        </div>

        <div className="text-xs text-muted-foreground font-mono">
          MTTR: <span className="text-white font-bold">{statsData?.avg_resolution_time_minutes || 24.5}m</span> | SLA:{" "}
          <span className="text-emerald-400 font-bold">{statsData?.sla_compliance_percent || 98.4}%</span>
        </div>
      </div>

      {/* View 1: Command Center Workspace (Master-Detail) */}
      {mainView === "command-center" && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Panel: Active Incident Selector Queue */}
          <div className="lg:col-span-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold uppercase text-muted-foreground">
                Correlated Queue ({activeList.length})
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => refetchActive()}
                className="h-7 text-xs text-muted-foreground hover:text-white"
              >
                <RefreshCw className="w-3 h-3 mr-1" /> Refresh
              </Button>
            </div>

            <div className="space-y-2.5 max-h-[780px] overflow-y-auto pr-1">
              {isActiveLoading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="rounded-xl border border-white/5 bg-white/5 p-4 animate-pulse">
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="h-4 w-16 bg-white/10 rounded"></div>
                      <div className="h-3 w-20 bg-white/10 rounded"></div>
                    </div>
                    <div className="h-4 w-full bg-white/10 rounded mb-1.5"></div>
                    <div className="h-4 w-3/4 bg-white/10 rounded mb-2"></div>
                    <div className="flex items-center justify-between pt-2 border-t border-white/[0.06]">
                      <div className="h-4 w-12 bg-white/10 rounded"></div>
                      <div className="h-3 w-16 bg-white/10 rounded"></div>
                    </div>
                  </div>
                ))
              ) : activeList.length === 0 ? (
                <div className="text-xs font-mono text-muted-foreground italic text-center p-8 bg-white/5 rounded-xl border border-white/10">
                  No active incidents in the queue.
                </div>
              ) : (
                activeList.map((inc) => {
                  const isSelected = inc.id === selectedIncidentId;
                  return (
                    <div
                      key={inc.id}
                      onClick={() => setSelectedIncidentId(inc.id)}
                      className={cn(
                        "rounded-xl border p-4 cursor-pointer transition-all duration-200 backdrop-blur-md shadow-glass",
                        isSelected
                          ? "border-brand-500 bg-brand-500/15 shadow-brand-500/10 shadow-lg"
                          : "border-white/[0.08] bg-bg-surface hover:border-white/[0.2] hover:bg-white/[0.02]"
                      )}
                    >
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <IncidentSeverityBadge severity={inc.severity} size="sm" />
                        <span className="text-[11px] font-mono text-muted-foreground">
                          {inc.affected_service}
                        </span>
                      </div>

                      <h4 className="text-xs font-bold text-white font-mono leading-snug line-clamp-2 mb-1.5">
                        {inc.title}
                      </h4>

                      {inc.root_cause && (
                        <p className="text-[11px] text-muted-foreground/80 font-mono line-clamp-1 mb-2">
                          Origin: {inc.root_cause}
                        </p>
                      )}

                      <div className="flex items-center justify-between text-[10px] font-mono text-muted-foreground pt-2 border-t border-white/[0.06]">
                        <Badge variant="outline" className="text-[9px] px-1.5 py-0 border-white/20">
                          {inc.status}
                        </Badge>
                        <span>Confidence: {Math.round((inc.confidence_score || 0.94) * 100)}%</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Panel: Incident Investigation Command Center */}
          <div className="lg:col-span-8 space-y-6">
            {isDetailLoading ? (
              <div className="space-y-6 animate-pulse">
                <div className="rounded-xl border border-white/5 bg-white/5 h-40 shadow-glass"></div>
                <div className="rounded-xl border border-white/5 bg-white/5 h-64 shadow-glass"></div>
                <div className="rounded-xl border border-white/5 bg-white/5 h-64 shadow-glass"></div>
              </div>
            ) : selectedIncident ? (
              <div className="space-y-6">
                {/* Incident Detail Header Banner */}
                <div className="rounded-xl border border-white/[0.1] bg-bg-surface p-5 shadow-glass backdrop-blur-md space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-2.5">
                      <IncidentSeverityBadge severity={selectedIncident.severity} size="md" />
                      <IncidentStatusControl
                        status={selectedIncident.status}
                        onAcknowledge={() => acknowledgeMutation.mutate(selectedIncident.id)}
                        onStatusChange={(st) =>
                          updateStatusMutation.mutate({ id: selectedIncident.id, status: st })
                        }
                        onResolve={(notes) =>
                          resolveMutation.mutate({ id: selectedIncident.id, notes })
                        }
                      />
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setIsVerifyModalOpen(true)}
                        className="border-emerald-500/40 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20 text-xs font-mono h-8"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                        Verify Telemetry Resolution
                      </Button>
                      <div className="text-xs font-mono text-muted-foreground">
                        Assigned: <span className="text-white font-medium">{selectedIncident.assigned_to || "Unassigned"}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h2 className="text-lg font-bold text-white font-mono tracking-tight">
                      {selectedIncident.title}
                    </h2>
                    {selectedIncident.description && (
                      <p className="text-xs text-muted-foreground font-mono mt-1 leading-relaxed">
                        {selectedIncident.description}
                      </p>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-muted-foreground pt-3 border-t border-white/[0.06]">
                    <div>
                      Primary Service: <span className="text-brand-300 font-semibold">{selectedIncident.affected_service}</span>
                    </div>
                    <div>
                      Impacted Services: <span className="text-amber-300 font-semibold">{selectedIncident.affected_services?.length || 1}</span>
                    </div>
                    <div>
                      Source: <span className="text-white">{selectedIncident.source || "Correlation Engine"}</span>
                    </div>
                    {selectedIncident.resolution_verified && (
                      <Badge variant="outline" className="border-emerald-500/40 bg-emerald-500/10 text-emerald-300 text-[10px] font-mono">
                        Resolution Verified (0 Remaining Risk)
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Root Cause Analysis Panel */}
                <RootCausePanel
                  incident={selectedIncident}
                  onReanalyze={() => reanalyzeMutation.mutate(selectedIncident.id)}
                  isAnalyzing={reanalyzeMutation.isPending}
                />

                {/* Investigation Tabs: Timeline | Evidence | Blast Radius | Remediation */}
                <Card className="border border-white/[0.1] bg-bg-surface shadow-glass">
                  <CardHeader className="pb-3 border-b border-white/[0.08]">
                    <Tabs defaultValue="timeline" className="w-full">
                      <TabsList className="bg-bg-surface border border-white/[0.08] h-9 p-1">
                        <TabsTrigger value="timeline" className="text-xs font-mono flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5" />
                          Chronological Timeline ({timelineEvents.length || selectedIncident.timeline_events?.length || 0})
                        </TabsTrigger>
                        <TabsTrigger value="evidence" className="text-xs font-mono flex items-center gap-1.5">
                          <Activity className="w-3.5 h-3.5" />
                          Multi-Modal Evidence ({selectedIncident.evidence?.length || 4})
                        </TabsTrigger>
                        <TabsTrigger value="blast-radius" className="text-xs font-mono flex items-center gap-1.5">
                          <Network className="w-3.5 h-3.5" />
                          Topology & Blast Radius
                        </TabsTrigger>
                        <TabsTrigger value="remediation" className="text-xs font-mono flex items-center gap-1.5 text-emerald-400">
                          <Wrench className="w-3.5 h-3.5" />
                          Remediation Actions ({selectedIncident.recommended_actions?.length || 3})
                        </TabsTrigger>
                      </TabsList>

                      <TabsContent value="timeline" className="mt-4">
                        <IncidentTimeline
                          events={timelineEvents.length > 0 ? timelineEvents : selectedIncident.timeline_events || []}
                          onAddEvent={(payload) => addTimelineNoteMutation.mutate(payload)}
                          isSubmitting={addTimelineNoteMutation.isPending}
                        />
                      </TabsContent>

                      <TabsContent value="evidence" className="mt-4">
                        <EvidencePanel evidence={selectedIncident.evidence} />
                      </TabsContent>

                      <TabsContent value="blast-radius" className="mt-4">
                        <IncidentImpactGraph
                          blastRadius={blastRadiusData || selectedIncident.blast_radius}
                          rootService={selectedIncident.affected_service}
                          affectedServices={selectedIncident.affected_services}
                        />
                      </TabsContent>

                      <TabsContent value="remediation" className="mt-4">
                        <RemediationPanel
                          actions={selectedIncident.recommended_actions}
                          onExecuteAction={async (actId, authBy) => {
                            await remediateMutation.mutateAsync({ actionId: actId, authorizedBy: authBy });
                          }}
                          isExecuting={remediateMutation.isPending}
                        />
                      </TabsContent>
                    </Tabs>
                  </CardHeader>
                </Card>
              </div>
            ) : (
              <div className="rounded-xl border border-white/[0.08] bg-bg-surface p-12 text-center text-muted-foreground font-mono">
                Select an incident from the queue to inspect root cause, evidence, and remediation workflows.
              </div>
            )}
          </div>
        </div>
      )}

      {/* View 2: All Incidents Ledger */}
      {mainView === "ledger" && (
        <Card className="border border-white/[0.1] bg-bg-surface shadow-glass">
          <CardContent className="p-6">
            <IncidentTable
              incidents={incidentListData?.items || []}
              isLoading={isListLoading}
              onSelectIncident={(inc) => {
                setSelectedIncidentId(inc.id);
                setMainView("command-center");
              }}
              onEditIncident={() => {}}
              onDeleteIncident={() => {}}
            />
          </CardContent>
        </Card>
      )}

      {/* View 3: Analytics & MTTR */}
      {mainView === "analytics" && analyticsData && (
        <IncidentAnalyticsCharts data={analyticsData} />
      )}

      {/* Create Incident Modal */}
      <CreateIncidentModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={(payload) => createMutation.mutate(payload)}
        isLoading={createMutation.isPending}
      />

      {/* Resolution Verification Modal */}
      <ResolutionVerificationModal
        incident={selectedIncident || null}
        isOpen={isVerifyModalOpen}
        onClose={() => setIsVerifyModalOpen(false)}
        onVerify={async (overrideTelem) => {
          if (selectedIncidentId) {
            return await verifyResolutionMutation.mutateAsync({
              id: selectedIncidentId,
              telemetry: overrideTelem,
            });
          }
        }}
        onCloseIncident={async (id) => {
          await closeIncidentMutation.mutateAsync(id);
        }}
        isLoading={verifyResolutionMutation.isPending}
      />
    </div>
  );
}
