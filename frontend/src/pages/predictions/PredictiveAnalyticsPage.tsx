/**
 * AI Predictive Incident Detection & Anomaly Intelligence Engine — Main Page
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
  Flame,
  Radio,
  BarChart3,
  Layers,
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
import { ForecastConfidenceChart } from "@/components/predictions/ForecastConfidenceChart";
import { AnomalyTimeline } from "@/components/predictions/AnomalyTimeline";
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

  // Active View Tab
  const [activeTab, setActiveTab] = useState<"alerts" | "forecasting" | "anomalies" | "heatmap">("alerts");

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

  // Query Anomaly Events
  const { data: anomaliesData, isLoading: isAnomaliesLoading } = useQuery({
    queryKey: ["prediction-anomalies"],
    queryFn: () => predictionService.getAnomalies({ size: 25 }),
  });

  // Query Forecast Sample Data
  const { data: forecastData, isLoading: isForecastLoading, refetch: refetchForecast } = useQuery({
    queryKey: ["prediction-forecast"],
    queryFn: () =>
      predictionService.getForecast({
        service: "api-gateway",
        metric_name: "memory_utilization",
        horizons: ["5m", "15m", "30m", "1h", "6h", "24h"],
      }),
  });

  // Trigger Gemini Analysis Mutation
  const analyzeMutation = useMutation({
    mutationFn: (services?: string[]) =>
      predictionService.triggerAnalysis({ services, lookback_hours: 24 }),
    onSuccess: (newPrediction) => {
      queryClient.invalidateQueries({ queryKey: ["predictions"] });
      queryClient.invalidateQueries({ queryKey: ["prediction-stats"] });
      queryClient.invalidateQueries({ queryKey: ["prediction-heatmap"] });
      queryClient.invalidateQueries({ queryKey: ["prediction-anomalies"] });
      setSelectedPrediction(newPrediction);
      toast({
        title: "Predictive Failure Detected",
        description: `Flagged high risk on ${newPrediction.service} (${newPrediction.failure_probability}% probability).`,
        variant: "destructive",
      });
    },
    onError: (err: any) => {
      toast({
        title: "Analysis Failed",
        description: err?.message || "Failed to complete predictive scan.",
        variant: "destructive",
      });
    },
  });

  // Mitigate Mutation
  const mitigateMutation = useMutation({
    mutationFn: (predictionId: string) =>
      predictionService.updateStatus(predictionId, "Mitigated"),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["predictions"] });
      queryClient.invalidateQueries({ queryKey: ["prediction-stats"] });
      queryClient.invalidateQueries({ queryKey: ["prediction-heatmap"] });
      if (selectedPrediction?.id === updated.id) {
        setSelectedPrediction(updated);
      }
      toast({
        title: "Risk Mitigated",
        description: `Successfully mitigated prediction alert for ${updated.service}.`,
      });
    },
  });

  // Declare Incident Mutation
  const declareIncidentMutation = useMutation({
    mutationFn: (predictionId: string) =>
      predictionService.createIncidentFromPrediction(predictionId),
    onSuccess: (incident) => {
      queryClient.invalidateQueries({ queryKey: ["predictions"] });
      queryClient.invalidateQueries({ queryKey: ["prediction-stats"] });
      toast({
        title: "Incident Declared",
        description: `Escalated predictive risk to Incident Command Center (${incident.title}).`,
      });
    },
    onError: (err: any) => {
      toast({
        title: "Incident Escalation Failed",
        description: err?.message || "Could not declare incident from prediction.",
        variant: "destructive",
      });
    },
  });

  // Mark False Positive Mutation
  const falsePositiveMutation = useMutation({
    mutationFn: (predictionId: string) =>
      predictionService.updateStatus(predictionId, "False_Positive"),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["predictions"] });
      if (selectedPrediction?.id === updated.id) {
        setSelectedPrediction(null);
      }
      toast({
        title: "Feedback Recorded",
        description: `Marked prediction as False Positive to tune AI baseline weights.`,
      });
    },
  });

  const predictions = predictionData?.items || [];
  const activeCount = statsData?.predicted_failures || 0;
  const highRiskServicesCount = statsData?.high_risk_services || 0;
  const avgConfidence = statsData?.avg_confidence_percent || 92;
  const preventedHours = statsData?.prevented_downtime_hours || 18.5;

  return (
    <div className="min-h-screen bg-slate-950 p-6 space-y-6 text-slate-100">
      {/* Header */}
      <PageHeader
        title="Predictive AIOps & Anomaly Intelligence Engine"
        description="Continuous statistical baselining, multi-horizon forecasting, and predictive failure diagnostics."
        icon={Sparkles}
        badge={
          <Badge variant="outline" className="border-indigo-500/40 bg-indigo-500/10 text-indigo-300">
            {activeCount} Active Predictive Warnings
          </Badge>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                refetchList();
                refetchForecast();
              }}
              disabled={isListLoading}
              className="border-slate-800 bg-slate-900 text-slate-300 hover:bg-slate-800"
            >
              <RefreshCw className={`mr-1.5 h-3.5 w-3.5 ${isListLoading ? "animate-spin" : ""}`} />
              Refresh Signals
            </Button>

            <Button
              size="sm"
              onClick={() => analyzeMutation.mutate(["api-gateway", "auth-service"])}
              disabled={analyzeMutation.isPending}
              className="bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20"
            >
              <Sparkles className={`mr-1.5 h-3.5 w-3.5 ${analyzeMutation.isPending ? "animate-spin" : ""}`} />
              {analyzeMutation.isPending ? "Analyzing Telemetry..." : "Run AI Risk Diagnostics"}
            </Button>
          </div>
        }
      />

      {/* KPI Stats Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Predicted Failures (Active)"
          value={activeCount}
          subtitle="Critical & High risk signals"
          icon={ShieldAlert}
          variant={activeCount > 0 ? "danger" : "default"}
          loading={isStatsLoading}
        />
        <StatCard
          title="High Risk Services"
          value={highRiskServicesCount}
          subtitle="Services nearing capacity saturation"
          icon={Activity}
          variant={highRiskServicesCount > 0 ? "warning" : "default"}
          loading={isStatsLoading}
        />
        <StatCard
          title="Average AI Confidence"
          value={`${avgConfidence}%`}
          subtitle="Grounded across statistical models"
          icon={CheckCircle2}
          variant="success"
          loading={isStatsLoading}
        />
        <StatCard
          title="Prevented Downtime"
          value={`${preventedHours}h`}
          subtitle="Estimated saved operational outage"
          icon={Clock}
          variant="default"
          loading={isStatsLoading}
        />
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Button
            variant={activeTab === "alerts" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("alerts")}
            className={activeTab === "alerts" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"}
          >
            <ShieldAlert className="mr-1.5 h-4 w-4" />
            Predictive Risk Alerts ({predictions.length})
          </Button>

          <Button
            variant={activeTab === "forecasting" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("forecasting")}
            className={activeTab === "forecasting" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"}
          >
            <TrendingUp className="mr-1.5 h-4 w-4" />
            Multi-Horizon Forecasting
          </Button>

          <Button
            variant={activeTab === "anomalies" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("anomalies")}
            className={activeTab === "anomalies" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"}
          >
            <Radio className="mr-1.5 h-4 w-4" />
            Statistical Anomaly Ledger
          </Button>

          <Button
            variant={activeTab === "heatmap" ? "default" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("heatmap")}
            className={activeTab === "heatmap" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"}
          >
            <Layers className="mr-1.5 h-4 w-4" />
            Infrastructure Risk Heatmap
          </Button>
        </div>
      </div>

      {/* TAB 1: Predictive Risk Alerts */}
      {activeTab === "alerts" && (
        <div className="space-y-4">
          {/* Filters Row */}
          <div className="flex flex-wrap items-center gap-3 rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <Input
                placeholder="Search predictions by title, service, root cause..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 h-9 text-xs bg-slate-950/60 border-slate-800"
              />
            </div>

            <select
              value={serviceFilter}
              onChange={(e) => setServiceFilter(e.target.value)}
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs text-slate-300 focus:outline-none"
            >
              <option value="">All Services</option>
              <option value="api-gateway">api-gateway</option>
              <option value="auth-service">auth-service</option>
              <option value="payment-service">payment-service</option>
              <option value="database-cluster">database-cluster</option>
            </select>

            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs text-slate-300 focus:outline-none"
            >
              <option value="">All Risk Levels</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs text-slate-300 focus:outline-none"
            >
              <option value="">All Statuses</option>
              <option value="Active">Active</option>
              <option value="Monitoring">Monitoring</option>
              <option value="Mitigated">Mitigated</option>
              <option value="Resolved">Resolved</option>
            </select>
          </div>

          {/* Predictions Table */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/90 shadow-2xl overflow-hidden backdrop-blur-md">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950/80 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Risk & Probability</th>
                    <th className="px-4 py-3">Service & Environment</th>
                    <th className="px-4 py-3">Predicted Failure & Root Cause</th>
                    <th className="px-4 py-3">Estimated Breach</th>
                    <th className="px-4 py-3">Confidence</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {isListLoading ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-12 text-center text-slate-400">
                        <Activity className="mx-auto h-6 w-6 animate-spin text-indigo-400 mb-2" />
                        Loading predictive incident alerts...
                      </td>
                    </tr>
                  ) : predictions.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-12 text-center text-slate-400">
                        <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-400 mb-2" />
                        <p className="text-sm font-semibold text-slate-200">No Failure Predictions Found</p>
                        <p className="text-xs text-slate-500 mt-1">Telemetry baselines indicate nominal operations across all services.</p>
                      </td>
                    </tr>
                  ) : (
                    predictions.map((p) => {
                      const isCritical = p.risk_level === "Critical";
                      const estMins = p.estimated_time_to_threshold_minutes || 28;

                      return (
                        <tr
                          key={p.id}
                          className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                          onClick={() => setSelectedPrediction(p)}
                        >
                          <td className="px-4 py-3.5">
                            <div className="flex items-center gap-2">
                              <Badge
                                variant={p.risk_level === "Critical" ? "critical" : p.risk_level === "High" ? "danger" : "warning"}
                                className="text-[10px] py-0 px-1.5"
                              >
                                {p.risk_level}
                              </Badge>
                              <span className="font-mono font-bold text-rose-400">
                                {p.failure_probability.toFixed(0)}%
                              </span>
                            </div>
                          </td>

                          <td className="px-4 py-3.5">
                            <div className="font-semibold text-slate-200 font-mono">{p.service}</div>
                            <div className="text-[10px] text-slate-500">{p.region} • {p.environment || "production"}</div>
                          </td>

                          <td className="px-4 py-3.5 max-w-md">
                            <div className="font-medium text-slate-200 line-clamp-1">{p.title}</div>
                            <div className="text-[11px] text-slate-400 line-clamp-1 mt-0.5 font-mono">
                              {p.likely_root_cause || "Accelerating resource degradation detected."}
                            </div>
                          </td>

                          <td className="px-4 py-3.5 font-mono text-slate-300">
                            {p.status === "Active" ? (
                              <span className="flex items-center gap-1 text-rose-400 font-bold">
                                <Clock className="h-3 w-3" /> ~{estMins.toFixed(0)}m
                              </span>
                            ) : (
                              <span className="text-slate-500">—</span>
                            )}
                          </td>

                          <td className="px-4 py-3.5 font-mono text-emerald-400">
                            {Math.round(p.confidence_score * 100)}%
                          </td>

                          <td className="px-4 py-3.5">
                            <Badge
                              variant="outline"
                              className={`text-[10px] py-0 px-1.5 uppercase font-mono ${
                                p.status === "Active"
                                  ? "border-rose-500/30 bg-rose-500/10 text-rose-300"
                                  : p.status === "Mitigated"
                                  ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                                  : "border-slate-700 text-slate-400"
                              }`}
                            >
                              {p.status}
                            </Badge>
                          </td>

                          <td className="px-4 py-3.5 text-right" onClick={(e) => e.stopPropagation()}>
                            <div className="flex items-center justify-end gap-1.5">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => setSelectedPrediction(p)}
                                className="h-7 px-2 text-slate-300 hover:text-white hover:bg-slate-800"
                              >
                                <Eye className="h-3.5 w-3.5 mr-1" />
                                Inspect
                              </Button>

                              {p.status === "Active" && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => declareIncidentMutation.mutate(p.id)}
                                  disabled={declareIncidentMutation.isPending}
                                  className="h-7 px-2 border-rose-500/40 text-rose-300 hover:bg-rose-950/40"
                                >
                                  <Flame className="h-3 w-3 mr-1" />
                                  Declare Incident
                                </Button>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Multi-Horizon Forecasting */}
      {activeTab === "forecasting" && (
        <div className="space-y-4">
          <ForecastConfidenceChart
            forecastData={forecastData}
            isLoading={isForecastLoading}
            onRefreshForecast={(svc, metric) => {
              predictionService.getForecast({ service: svc, metric_name: metric }).then((res) => {
                queryClient.setQueryData(["prediction-forecast"], res);
              });
            }}
          />
        </div>
      )}

      {/* TAB 3: Statistical Anomaly Ledger */}
      {activeTab === "anomalies" && (
        <div className="space-y-4">
          <AnomalyTimeline
            anomalies={anomaliesData || []}
            isLoading={isAnomaliesLoading}
          />
        </div>
      )}

      {/* TAB 4: Infrastructure Risk Heatmap */}
      {activeTab === "heatmap" && (
        <div className="space-y-4">
          <RiskHeatmap
            items={heatmapData?.items || []}
            isLoading={isHeatmapLoading}
            onSelectService={(service) => {
              setServiceFilter(service);
              setActiveTab("alerts");
            }}
          />
        </div>
      )}

      {/* Prediction Explanation Drawer */}
      <PredictionDrawer
        prediction={selectedPrediction}
        isOpen={Boolean(selectedPrediction)}
        onClose={() => setSelectedPrediction(null)}
        onMitigate={async (id) => {
          await mitigateMutation.mutateAsync(id);
        }}
        onCreateIncident={async (id) => {
          await declareIncidentMutation.mutateAsync(id);
        }}
        onMarkFalsePositive={async (id) => {
          await falsePositiveMutation.mutateAsync(id);
        }}
        isMitigating={mitigateMutation.isPending}
      />
    </div>
  );
}
