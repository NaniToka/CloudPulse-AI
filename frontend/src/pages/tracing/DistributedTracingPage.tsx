/**
 * Distributed Tracing Platform — Main Trace Explorer Page
 */

import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  Activity,
  RefreshCw,
  Search,
  Sparkles,
  Clock,
  Eye,
  Filter,
  Server,
  ShieldCheck,
  AlertTriangle,
  Globe,
} from "lucide-react";

import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/useToast";

import { traceService } from "@/services/traceService";
import { ServiceTopologyMap } from "@/components/tracing/ServiceTopologyMap";
import { TraceTimelineWaterfall } from "@/components/tracing/TraceTimelineWaterfall";
import { TraceAIDrawer } from "@/components/tracing/TraceAIDrawer";
import type { Trace, TraceAIAnalysis } from "@/types/trace";

export default function DistributedTracingPage() {
  const { toast } = useToast();

  // Filters State
  const [search, setSearch] = useState("");
  const [serviceFilter, setServiceFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [minDuration, setMinDuration] = useState("");

  const [selectedTrace, setSelectedTrace] = useState<Trace | null>(null);
  const [analysisData, setAnalysisData] = useState<TraceAIAnalysis | null>(null);
  const [isAnalysisOpen, setIsAnalysisOpen] = useState(false);

  // Query Traces List
  const {
    data: traceData,
    isLoading: isTracesLoading,
    refetch: refetchTraces,
  } = useQuery({
    queryKey: ["traces", serviceFilter, statusFilter, minDuration, search],
    queryFn: () =>
      traceService.getTraces({
        service: serviceFilter || undefined,
        status: statusFilter || undefined,
        min_duration_ms: minDuration ? parseFloat(minDuration) : undefined,
        search: search || undefined,
        size: 20,
      }),
  });

  // Query Service Map
  const { data: serviceMapData, isLoading: isMapLoading } = useQuery({
    queryKey: ["service-map"],
    queryFn: () => traceService.getServiceMap(),
  });

  // Trigger Gemini AI Trace Analysis Mutation
  const analyzeMutation = useMutation({
    mutationFn: (traceId: string) => traceService.analyzeTrace(traceId),
    onSuccess: (res) => {
      setAnalysisData(res);
      setIsAnalysisOpen(true);
      toast({
        title: "AI Trace Analysis Complete",
        description: `Bottleneck identified: ${res.slowest_service}`,
      });
    },
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Distributed Tracing Platform"
        subtitle="Google Cloud Trace & Datadog APM style OpenTelemetry end-to-end request flow diagnostics"
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refetchTraces()}
              className="gap-2 text-xs"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Refresh Traces
            </Button>
          </div>
        }
      />

      {/* Top KPI Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="Total Traces"
          value={traceData?.total.toString() || "1,240"}
          subValue="Active sample buffer"
        />
        <StatCard
          label="P99 Request Latency"
          value="654.5 ms"
          subValue="Cross-service bottleneck peak"
        />
        <StatCard
          label="Trace Error Rate"
          value="1.8%"
          subValue="Failed span ratio"
        />
        <StatCard
          label="Active Microservices"
          value={serviceMapData?.nodes.length.toString() || "9"}
          subValue="Tracked OpenTelemetry nodes"
        />
      </div>

      {/* Service Topology Graph */}
      <ServiceTopologyMap
        nodes={serviceMapData?.nodes || []}
        edges={serviceMapData?.edges || []}
        isLoading={isMapLoading}
      />

      {/* Trace Explorer & Waterfall Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Trace List */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-2xl">
            <CardHeader className="p-4 border-b border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <Activity className="h-4 w-4 text-brand-purple" />
                <CardTitle className="text-sm font-semibold text-foreground">
                  Distributed Trace Directory
                </CardTitle>
              </div>

              {/* Filter Bar */}
              <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
                <div className="relative flex-1 min-w-[180px] md:w-52">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Search trace ID, endpoint..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="pl-9 h-9 text-xs bg-bg-elevated/60 border-white/10"
                  />
                </div>

                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none"
                >
                  <option value="">All Statuses</option>
                  <option value="ok">OK (200)</option>
                  <option value="error">ERROR (5xx)</option>
                </select>
              </div>
            </CardHeader>

            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-white/10 text-muted-foreground bg-bg-elevated/40 font-mono">
                      <th className="px-4 py-3 text-left font-medium">Status</th>
                      <th className="px-4 py-3 text-left font-medium">Trace ID & Endpoint</th>
                      <th className="px-4 py-3 text-left font-medium">Root Service</th>
                      <th className="px-4 py-3 text-left font-medium">Spans</th>
                      <th className="px-4 py-3 text-left font-medium">Duration</th>
                      <th className="px-4 py-3 text-right font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isTracesLoading ? (
                      Array.from({ length: 4 }).map((_, i) => (
                        <tr key={i} className="border-b border-white/5 animate-pulse">
                          <td className="px-4 py-4"><div className="h-5 w-12 bg-white/10 rounded" /></td>
                          <td className="px-4 py-4"><div className="h-4 w-48 bg-white/10 rounded" /></td>
                          <td className="px-4 py-4"><div className="h-4 w-24 bg-white/10 rounded" /></td>
                          <td className="px-4 py-4"><div className="h-4 w-12 bg-white/10 rounded" /></td>
                          <td className="px-4 py-4"><div className="h-4 w-16 bg-white/10 rounded" /></td>
                          <td className="px-4 py-4 text-right"><div className="h-4 w-16 bg-white/10 rounded ml-auto" /></td>
                        </tr>
                      ))
                    ) : (
                      traceData?.items.map((tr) => {
                        const isSelected = selectedTrace?.trace_id === tr.trace_id;
                        return (
                          <tr
                            key={tr.id}
                            onClick={() => setSelectedTrace(tr)}
                            className={`border-b border-white/5 hover:bg-white/[0.04] transition-all cursor-pointer ${
                              isSelected ? "bg-white/[0.06] border-l-2 border-l-brand-purple" : ""
                            }`}
                          >
                            <td className="px-4 py-3 font-mono font-medium">
                              <Badge variant={tr.status === "ok" ? "success" : "danger"}>
                                {tr.http_status}
                              </Badge>
                            </td>

                            <td className="px-4 py-3">
                              <div className="font-bold text-foreground font-mono truncate max-w-xs">
                                {tr.name}
                              </div>
                              <div className="text-[10px] text-muted-foreground font-mono">
                                {tr.trace_id}
                              </div>
                            </td>

                            <td className="px-4 py-3 font-mono text-muted-foreground">
                              {tr.root_service}
                            </td>

                            <td className="px-4 py-3 font-mono text-foreground font-bold">
                              {tr.span_count}
                            </td>

                            <td className="px-4 py-3 font-mono text-foreground font-bold">
                              {tr.duration_ms} ms
                            </td>

                            <td className="px-4 py-3 text-right">
                              <Button
                                size="sm"
                                variant="ghost"
                                disabled={analyzeMutation.isPending}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  analyzeMutation.mutate(tr.trace_id);
                                }}
                                className="h-7 px-2 text-xs gap-1 text-brand-purple hover:text-brand-purple/80"
                              >
                                <Sparkles className="h-3.5 w-3.5" /> AI Analyze
                              </Button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Span Waterfall Tree */}
        <div className="lg:col-span-1 space-y-4">
          <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-2xl p-4 space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="text-xs font-bold text-foreground flex items-center gap-1.5 font-mono">
                <Clock className="h-4 w-4 text-brand-purple" /> Span Waterfall Tree
              </h3>
            </div>

            <TraceTimelineWaterfall trace={selectedTrace} />
          </Card>
        </div>
      </div>

      {/* Slide-over AI Trace Analysis Drawer */}
      <TraceAIDrawer
        analysis={analysisData}
        isOpen={isAnalysisOpen}
        onClose={() => setIsAnalysisOpen(false)}
        isLoading={analyzeMutation.isPending}
      />
    </div>
  );
}
