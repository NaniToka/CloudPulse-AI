import React, { useEffect, useState } from "react";
import { Activity, RefreshCw, Sparkles, Info, ShieldAlert } from "lucide-react";
import { sreService } from "@/services/sreService";
import type {
  SreOverviewResponse,
  ServiceReliabilityItem,
  SloItem,
  BurnRateItem,
  ReliabilityRiskItem,
  IncidentImpactItem,
  DependencyImpactItem,
  ReliabilityForecastResponse,
  SreRecommendationItem,
  SreAnalyzeResponse,
} from "@/types/sre";

import SreOverviewCards from "@/components/sre/SreOverviewCards";
import ServiceReliabilityTable from "@/components/sre/ServiceReliabilityTable";
import SloOverviewPanel from "@/components/sre/SloOverviewPanel";
import BurnRateMatrix from "@/components/sre/BurnRateMatrix";
import ReliabilityRiskPanel from "@/components/sre/ReliabilityRiskPanel";
import IncidentImpactPanel from "@/components/sre/IncidentImpactPanel";
import DependencyImpactPanel from "@/components/sre/DependencyImpactPanel";
import ReliabilityForecastCard from "@/components/sre/ReliabilityForecastCard";
import SreRecommendationPanel from "@/components/sre/SreRecommendationPanel";

export default function SrePage() {
  const [overview, setOverview] = useState<SreOverviewResponse | null>(null);
  const [services, setServices] = useState<ServiceReliabilityItem[]>([]);
  const [slos, setSlos] = useState<SloItem[]>([]);
  const [burnRates, setBurnRates] = useState<BurnRateItem[]>([]);
  const [risks, setRisks] = useState<ReliabilityRiskItem[]>([]);
  const [incidents, setIncidents] = useState<IncidentImpactItem[]>([]);
  const [dependencies, setDependencies] = useState<DependencyImpactItem[]>([]);
  const [forecast, setForecast] = useState<ReliabilityForecastResponse | null>(null);
  const [recommendations, setRecommendations] = useState<SreRecommendationItem[]>([]);
  const [aiAnalysis, setAiAnalysis] = useState<SreAnalyzeResponse | null>(null);

  const [sortBy, setSortBy] = useState("worst_reliability");
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async (sort = sortBy) => {
    try {
      setLoading(true);
      setError(null);
      const [
        ovRes,
        svcRes,
        sloRes,
        burnRes,
        riskRes,
        incRes,
        depRes,
        fcRes,
        recRes,
      ] = await Promise.all([
        sreService.getOverview(),
        sreService.getServices(sort),
        sreService.getSlos(),
        sreService.getBurnRates(),
        sreService.getRisks(),
        sreService.getIncidents(),
        sreService.getDependencies(),
        sreService.getForecast(),
        sreService.getRecommendations(),
      ]);

      setOverview(ovRes);
      setServices(svcRes.services);
      setSlos(sloRes.slos);
      setBurnRates(burnRes);
      setRisks(riskRes.risks);
      setIncidents(incRes.incidents);
      setDependencies(depRes.dependencies);
      setForecast(fcRes);
      setRecommendations(recRes.recommendations);
    } catch (err: any) {
      console.error("Failed to load SRE telemetry:", err);
      setError(err?.message || "Failed to load SRE reliability telemetry.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(sortBy);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSortChange = (newSort: string) => {
    setSortBy(newSort);
    loadData(newSort);
  };

  const handleTriggerAnalysis = async () => {
    try {
      setAnalyzing(true);
      const result = await sreService.triggerAnalysis();
      setAiAnalysis(result);
      if (result.sre_recommendations && result.sre_recommendations.length > 0) {
        setRecommendations(result.sre_recommendations);
      }
    } catch (err: any) {
      console.error("SRE Analysis failed:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <Activity className="w-7 h-7 text-brand-blue" />
            <h1 className="text-2xl font-bold font-mono tracking-tight text-foreground">
              Enterprise SRE & Reliability Intelligence Center
            </h1>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Real-time SLI/SLO compliance, error budget burn rates, risk detection, and AI reliability recovery
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => loadData(sortBy)}
            disabled={loading}
            className="px-3.5 py-2 rounded-lg border border-white/10 bg-black/40 text-xs font-mono text-foreground flex items-center gap-2 hover:bg-white/5 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>

          <button
            onClick={handleTriggerAnalysis}
            disabled={analyzing}
            className="px-4 py-2 rounded-lg bg-brand-blue text-white font-semibold text-xs flex items-center gap-2 hover:bg-brand-blue/80 transition-all disabled:opacity-50 shadow-lg shadow-brand-blue/20"
          >
            <Sparkles className="w-4 h-4" />
            {analyzing ? "Analyzing Telemetry..." : "Run AI SRE Analysis"}
          </button>
        </div>
      </div>

      {/* Fixture Notification Banner */}
      <div className="p-3.5 rounded-xl border border-blue-500/20 bg-blue-500/10 backdrop-blur-md flex items-center gap-3 text-xs font-mono text-blue-200">
        <Info className="w-4 h-4 text-blue-400 shrink-0" />
        <span>
          {overview?.data_source || "Demo Data — No Production Telemetry Connected"} | {overview?.environment || "Local Development"}
        </span>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-xs text-rose-300">
          {error}
        </div>
      )}

      {/* AI Analysis Executive Summary Banner */}
      {aiAnalysis && (
        <div className="p-5 rounded-xl border border-amber-500/30 bg-amber-500/10 backdrop-blur-md space-y-3 font-mono">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <h3 className="text-sm font-semibold text-foreground">SRE AI Executive Intelligence Summary</h3>
            </div>
            <span className="text-[11px] text-amber-300 font-bold">Engine: {aiAnalysis.analysis_engine}</span>
          </div>

          <p className="text-xs text-slate-200 leading-relaxed">{aiAnalysis.executive_summary}</p>

          {aiAnalysis.critical_services.length > 0 && (
            <div className="pt-2 border-t border-amber-500/20 text-xs text-rose-300 space-y-1">
              <span className="font-bold">Critical Services Requiring Immediate Attention:</span>
              <ul className="list-disc list-inside space-y-0.5 text-slate-300">
                {aiAnalysis.critical_services.map((cs, idx) => (
                  <li key={idx}>{cs}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* KPI Overview Cards */}
      <SreOverviewCards overview={overview} />

      {/* Service Reliability Scorecard Table */}
      <ServiceReliabilityTable
        services={services}
        sortBy={sortBy}
        onSortChange={handleSortChange}
      />

      {/* SLOs & Burn Rate Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SloOverviewPanel slos={slos} />
        <BurnRateMatrix burnRates={burnRates} />
      </div>

      {/* Reliability Risks & Incident Impact */}
      <ReliabilityRiskPanel risks={risks} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <IncidentImpactPanel incidents={incidents} />
        <DependencyImpactPanel dependencies={dependencies} />
      </div>

      {/* Predictive Forecast & AI Recommendations */}
      <ReliabilityForecastCard forecast={forecast} />

      <SreRecommendationPanel
        recommendations={recommendations}
        onTriggerAnalysis={handleTriggerAnalysis}
        isAnalyzing={analyzing}
      />
    </div>
  );
}
