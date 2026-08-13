import React, { useEffect, useState } from 'react';
import {
  DependencyImpactItem,
  ErrorBudgetOverview,
  ReliabilityIncidentItem,
  ReliabilityOverview,
  ReliabilityRecommendationItem,
  ReliabilityRiskItem,
  ServiceReliabilityProfile,
  SloForecastItem,
} from '../../types/reliability';
import { reliabilityService, ReliabilityFilterParams } from '../../services/reliabilityService';
import { ReliabilityHeader } from '../../components/reliability/ReliabilityHeader';
import { ReliabilityOverviewMetrics } from '../../components/reliability/ReliabilityOverviewMetrics';
import { ServiceReliabilityTable } from '../../components/reliability/ServiceReliabilityTable';
import { SloComplianceChart } from '../../components/reliability/SloComplianceChart';
import { ErrorBudgetPanel } from '../../components/reliability/ErrorBudgetPanel';
import { MultiWindowBurnRateGrid } from '../../components/reliability/MultiWindowBurnRateGrid';
import { TopReliabilityRisksPanel } from '../../components/reliability/TopReliabilityRisksPanel';
import { SloForecastCard } from '../../components/reliability/SloForecastCard';
import { DependencyImpactVisualizer } from '../../components/reliability/DependencyImpactVisualizer';
import { IncidentCorrelationStream } from '../../components/reliability/IncidentCorrelationStream';
import { ReliabilityRecommendationsMatrix } from '../../components/reliability/ReliabilityRecommendationsMatrix';
import { ServiceDetailModal } from '../../components/reliability/ServiceDetailModal';
import { AlertCircle, RefreshCw, Sparkles, Bot } from 'lucide-react';

export const ServiceReliabilityPage: React.FC = () => {
  const [overview, setOverview] = useState<ReliabilityOverview | null>(null);
  const [services, setServices] = useState<ServiceReliabilityProfile[]>([]);
  const [errorBudgets, setErrorBudgets] = useState<ErrorBudgetOverview[]>([]);
  const [burnRates, setBurnRates] = useState<any[]>([]);
  const [risks, setRisks] = useState<ReliabilityRiskItem[]>([]);
  const [forecasts, setForecasts] = useState<SloForecastItem[]>([]);
  const [dependencies, setDependencies] = useState<DependencyImpactItem[]>([]);
  const [incidents, setIncidents] = useState<ReliabilityIncidentItem[]>([]);
  const [recommendations, setRecommendations] = useState<ReliabilityRecommendationItem[]>([]);
  const [aiAnalysis, setAiAnalysis] = useState<any | null>(null);

  const [selectedService, setSelectedService] = useState<ServiceReliabilityProfile | null>(null);

  const [filters, setFilters] = useState<ReliabilityFilterParams>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReliabilityData = async (currentFilters?: ReliabilityFilterParams) => {
    setLoading(true);
    setError(null);
    try {
      const activeFilters = currentFilters || filters;
      const [
        ovData,
        svcsData,
        ebData,
        brData,
        riskData,
        fcData,
        depData,
        incData,
        recData,
      ] = await Promise.all([
        reliabilityService.getOverview(),
        reliabilityService.getServices(activeFilters),
        reliabilityService.getErrorBudgets(),
        reliabilityService.getBurnRates(),
        reliabilityService.getRisks(),
        reliabilityService.getForecasts(),
        reliabilityService.getDependencies(),
        reliabilityService.getIncidents(),
        reliabilityService.getRecommendations(),
      ]);

      setOverview(ovData);
      setServices(svcsData);
      setErrorBudgets(ebData);
      setBurnRates(brData);
      setRisks(riskData);
      setForecasts(fcData);
      setDependencies(depData);
      setIncidents(incData);
      setRecommendations(recData);
    } catch (err: any) {
      console.error('Failed to fetch reliability data:', err);
      setError(err?.message || 'Failed to load Service Reliability Engineering data.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await reliabilityService.analyzeReliability();
      setAiAnalysis(res);
    } catch (err: any) {
      console.error('Failed to analyze reliability:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    fetchReliabilityData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFilterChange = (newFilters: ReliabilityFilterParams) => {
    setFilters(newFilters);
    fetchReliabilityData(newFilters);
  };

  if (loading && !overview) {
    return (
      <div className="p-12 text-center text-slate-400 space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-indigo-400" />
        <p className="text-sm font-semibold">Loading Service Reliability Center & SLO Intelligence 2.0...</p>
      </div>
    );
  }

  if (error && !overview) {
    return (
      <div className="p-8 max-w-xl mx-auto my-12 bg-rose-950/40 border border-rose-500/40 rounded-xl text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
        <div>
          <h3 className="text-lg font-bold text-white">Failed to Load Service Reliability Center</h3>
          <p className="text-xs text-rose-200 mt-1">{error}</p>
        </div>
        <button
          onClick={() => fetchReliabilityData()}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold rounded-lg transition-colors"
        >
          Retry Load
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Header & Filters */}
      <ReliabilityHeader
        filters={filters}
        onFilterChange={handleFilterChange}
        onRefresh={() => fetchReliabilityData()}
        onAnalyze={handleAnalyze}
        loading={loading}
        analyzing={analyzing}
      />

      {/* Reliability Overview Metrics */}
      <ReliabilityOverviewMetrics overview={overview} />

      {/* AI / Local Reliability Analysis Card */}
      {aiAnalysis && (
        <div className="bg-slate-900/80 border border-indigo-500/30 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-indigo-400 animate-pulse" />
              <h3 className="text-base font-bold text-white">SRE Reliability Intelligence Brief</h3>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 ${
                aiAnalysis.is_ai_powered
                  ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
                  : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              {aiAnalysis.badge}
            </span>
          </div>

          <p className="text-xs text-slate-200 leading-relaxed">{aiAnalysis.executive_summary}</p>
        </div>
      )}

      {/* Service Reliability Table */}
      <ServiceReliabilityTable
        services={services}
        onSelectService={(svc) => setSelectedService(svc)}
      />

      {/* SLO Compliance Chart & Error Budget Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SloComplianceChart services={services} />
        <ErrorBudgetPanel budgets={errorBudgets} />
      </div>

      {/* Multi-Window Burn Rate Grid */}
      <MultiWindowBurnRateGrid burnRatesData={burnRates} />

      {/* Top Reliability Risks & SLO Forecast */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopReliabilityRisksPanel risks={risks} />
        <SloForecastCard forecasts={forecasts} />
      </div>

      {/* Dependency Impact Visualizer */}
      <DependencyImpactVisualizer dependencies={dependencies} />

      {/* Incident Correlation Stream */}
      <IncidentCorrelationStream incidents={incidents} />

      {/* Actionable Reliability Recommendations Matrix */}
      <ReliabilityRecommendationsMatrix recommendations={recommendations} />

      {/* Interactive Service Detail Modal View */}
      {selectedService && (
        <ServiceDetailModal
          service={selectedService}
          onClose={() => setSelectedService(null)}
        />
      )}
    </div>
  );
};
