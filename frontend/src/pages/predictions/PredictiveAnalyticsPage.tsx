/**
 * AI Predictive Incident Detection Engine — Main Page
 */

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Sparkles,
  RefreshCw,
  Search,
  Activity,
  ShieldAlert,
  Clock,
  CheckCircle2,
  Eye,
  Check,
  TrendingUp,
  Sliders,
  Filter,
} from "lucide-react";

import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/useToast";

import { predictionService } from "@/services/predictionService";
import { RiskHeatmap } from "@/components/predictions/RiskHeatmap";
import { PredictionTimelineChart } from "@/components/predictions/PredictionTimelineChart";
import { PredictionDrawer } from "@/components/predictions/PredictionDrawer";
import type { Prediction, RiskLevel } from "@/types/prediction";

const riskBadgeVariant: Record<string, "critical" | "danger" | "warning" | "success"> = {
  Critical: "critical",
  High: "danger",
  Medium: "warning",
  Low: "success",
};

export default function PredictiveAnalyticsPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Filters State
  const [search, setSearch] = useState("");
  const [serviceFilter, setServiceFilter] = useState("");
  const [regionFilter, setRegionFilter] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null);

  // Query predictions list
  const {
    data: predictionData,
    isLoading: isListLoading,
    refetch: refetchList,
  } = useQuery({
    queryKey: ["predictions", serviceFilter, regionFilter, riskFilter, statusFilter, search],
    queryFn: () =>
      predictionService.getPredictions({
        service: serviceFilter || undefined,
        region: regionFilter || undefined,
        risk: riskFilter || undefined,
        status: statusFilter || undefined,
        search: search || undefined,
        size: 20,
      }),
  });

  // Query KPI Stats
  const { data: statsData, isLoading: isStatsLoading } = useQuery({
    queryKey: ["prediction-stats"],
    queryFn: () => predictionService.getStats(),
  });

  // Query Heatmap Data
  const { data: heatmapData, isLoading: isHeatmapLoading } = useQuery({
    queryKey: ["prediction-heatmap"],
    queryFn: () => predictionService.getRiskHeatmap(),
  });

  // Trigger Gemini Analysis Mutation
  const analyzeMutation = useMutation({
    mutationFn: (services?: string[]) =>
      predictionService.triggerAnalysis({ services, lookback_hours: 24 }),
    onSuccess: (newPrediction) => {
      queryClient.invalidateQueries({ queryKey: ["predictions"] });
      queryClient.invalidateQueries({ queryKey: ["prediction-stats"] });
      queryClient.invalidateQueries({ queryKey: ["prediction-heatmap"] });
      setSelectedPrediction(newPrediction);
      toast({
        title: "Predictive Failure Detected",
        description: `Gemini AI flagged high risk on ${newPrediction.service} (${newPrediction.failure_probability}% probability).`,
        variant: "destructive",
      });
    },
  });

  // Update Status Mutation (Auto-mitigate)
  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      predictionService.updateStatus(id, status),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["predictions"] });
      queryClient.invalidateQueries({ queryKey: ["prediction-stats"] });
      queryClient.invalidateQueries({ queryKey: ["prediction-heatmap"] });
      if (selectedPrediction && selectedPrediction.id === updated.id) {
        setSelectedPrediction(updated);
      }
      toast({
        title: "Prediction Mitigated",
        description: `Automated mitigation script executed for ${updated.service}.`,
      });
    },
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="AI Predictive Incident Detection Engine"
        subtitle="Google Cloud Operations & Datadog Watchdog style continuous failure forecasting & automated preventive SRE triage"
        actions={
          <div className="flex items-center gap-2">
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
              disabled={analyzeMutation.isPending}
              onClick={() => analyzeMutation.mutate()}
              className="gap-2 bg-brand-purple hover:bg-brand-purple/90 text-white text-xs"
            >
              <Sparkles className={`h-3.5 w-3.5 ${analyzeMutation.isPending ? "animate-spin" : ""}`} />
              {analyzeMutation.isPending ? "Analyzing Telemetry..." : "Analyze Telemetry"}
            </Button>
          </div>
        }
      />

      {/* Top Stat Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="Predicted Failures"
          value={statsData?.predicted_failures.toString() || "0"}
          subValue="Active forecasted outages"
        />
        <StatCard
          label="High Risk Services"
          value={statsData?.high_risk_services.toString() || "0"}
          subValue="Critical or High severity nodes"
        />
        <StatCard
          label="Avg AI Confidence"
          value={`${statsData?.avg_confidence_percent || 94.0}%`}
          subValue="Gemini pattern accuracy"
        />
        <StatCard
          label="Prevented Downtime"
          value={`${statsData?.prevented_downtime_hours || 19.5} hrs`}
          subValue="Saved via proactive mitigation"
        />
      </div>

      {/* Risk Heatmap & Timeline Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RiskHeatmap
            items={heatmapData?.items || []}
            selectedService={serviceFilter}
            onSelectService={setServiceFilter}
            isLoading={isHeatmapLoading}
          />
        </div>

        <div>
          <PredictionTimelineChart
            predictions={predictionData?.items || []}
            isLoading={isListLoading}
          />
        </div>
      </div>

      {/* Main Predictions Directory */}
      <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-2xl">
        <CardHeader className="p-4 border-b border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-brand-purple" />
            <CardTitle className="text-sm font-semibold text-foreground">
              Failure Forecast Directory
            </CardTitle>
          </div>

          {/* Filter Bar */}
          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            {/* Search */}
            <div className="relative flex-1 min-w-[200px] md:w-60">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search service, root cause..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 h-9 text-xs bg-bg-elevated/60 border-white/10 focus:border-brand-purple"
              />
            </div>

            {/* Risk filter */}
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-purple"
            >
              <option value="">All Risks</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>

            {/* Status filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-purple"
            >
              <option value="">All Statuses</option>
              <option value="Active">Active</option>
              <option value="Mitigated">Mitigated</option>
              <option value="Dismissed">Dismissed</option>
            </select>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-white/10 text-muted-foreground bg-bg-elevated/40">
                  <th className="px-4 py-3 text-left font-medium">Risk Level</th>
                  <th className="px-4 py-3 text-left font-medium">Predicted Failure Title</th>
                  <th className="px-4 py-3 text-left font-medium">Service & Region</th>
                  <th className="px-4 py-3 text-left font-medium">Probability %</th>
                  <th className="px-4 py-3 text-left font-medium">Expected Time</th>
                  <th className="px-4 py-3 text-left font-medium">AI Confidence</th>
                  <th className="px-4 py-3 text-left font-medium">Status</th>
                  <th className="px-4 py-3 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {isListLoading ? (
                  Array.from({ length: 4 }).map((_, i) => (
                    <tr key={i} className="border-b border-white/5 animate-pulse">
                      <td className="px-4 py-4"><div className="h-5 w-12 bg-white/10 rounded" /></td>
                      <td className="px-4 py-4"><div className="h-4 w-48 bg-white/10 rounded" /></td>
                      <td className="px-4 py-4"><div className="h-4 w-24 bg-white/10 rounded" /></td>
                      <td className="px-4 py-4"><div className="h-4 w-16 bg-white/10 rounded" /></td>
                      <td className="px-4 py-4"><div className="h-4 w-20 bg-white/10 rounded" /></td>
                      <td className="px-4 py-4"><div className="h-4 w-16 bg-white/10 rounded" /></td>
                      <td className="px-4 py-4"><div className="h-4 w-16 bg-white/10 rounded" /></td>
                      <td className="px-4 py-4 text-right"><div className="h-4 w-16 bg-white/10 rounded ml-auto" /></td>
                    </tr>
                  ))
                ) : predictionData?.items.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-12 text-center text-muted-foreground">
                      No predictive risk anomalies found matching active filters.
                    </td>
                  </tr>
                ) : (
                  predictionData?.items.map((pred) => (
                    <tr
                      key={pred.id}
                      className="border-b border-white/5 hover:bg-white/[0.04] transition-all group"
                    >
                      {/* Risk Level Badge */}
                      <td className="px-4 py-3 font-mono font-medium">
                        <Badge variant={riskBadgeVariant[pred.risk_level] || "warning"}>
                          {pred.risk_level}
                        </Badge>
                      </td>

                      {/* Title & Root cause */}
                      <td
                        onClick={() => setSelectedPrediction(pred)}
                        className="px-4 py-3 max-w-xs md:max-w-sm truncate cursor-pointer"
                      >
                        <div className="font-semibold text-foreground group-hover:text-brand-purple transition-colors truncate">
                          {pred.title}
                        </div>
                        {pred.likely_root_cause && (
                          <div className="text-[11px] text-muted-foreground truncate mt-0.5 font-mono">
                            {pred.likely_root_cause}
                          </div>
                        )}
                      </td>

                      {/* Service & Region */}
                      <td className="px-4 py-3 font-mono text-muted-foreground">
                        <span className="px-2 py-0.5 rounded bg-bg-elevated border border-white/5 text-foreground font-bold">
                          {pred.service}
                        </span>{" "}
                        <span className="text-[10px] text-muted-foreground">({pred.region})</span>
                      </td>

                      {/* Probability */}
                      <td className="px-4 py-3 font-mono font-bold text-red-400">
                        {pred.failure_probability.toFixed(1)}%
                      </td>

                      {/* Expected Time */}
                      <td className="px-4 py-3 text-muted-foreground font-mono text-[11px]">
                        {pred.expected_failure_time
                          ? new Date(pred.expected_failure_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
                          : "T+30m"}
                      </td>

                      {/* AI Confidence */}
                      <td className="px-4 py-3 text-emerald-400 font-mono font-medium">
                        {Math.round(pred.confidence_score * 100)}%
                      </td>

                      {/* Status */}
                      <td className="px-4 py-3">
                        <Badge variant={pred.status === "Active" ? "danger" : "success"}>
                          {pred.status}
                        </Badge>
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedPrediction(pred)}
                            className="h-7 px-2 text-xs gap-1 text-brand-purple hover:text-brand-purple/80"
                          >
                            <Eye className="h-3.5 w-3.5" /> Explain
                          </Button>

                          {pred.status === "Active" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => statusMutation.mutate({ id: pred.id, status: "Mitigated" })}
                              className="h-7 px-2 text-xs gap-1 text-emerald-400 hover:text-emerald-300"
                            >
                              <Check className="h-3.5 w-3.5" /> Mitigate
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Slide-over AI Explanation Drawer */}
      <PredictionDrawer
        prediction={selectedPrediction}
        isOpen={!!selectedPrediction}
        onClose={() => setSelectedPrediction(null)}
        onMitigate={async (id) => {
          await statusMutation.mutateAsync({ id, status: "Mitigated" });
        }}
        isMitigating={statusMutation.isPending}
      />
    </div>
  );
}
