import React, { useEffect, useState } from 'react';
import {
  BurnRate,
  CorrelatedIncident,
  ErrorBudget,
  ServiceReliability,
  SliMetrics,
  SloForecast,
  SloObjective,
  SloOverview,
  SloRecommendation,
  SloViolation,
} from '../../types/slo';
import { sloService } from '../../services/sloService';
import { DemoTelemetryBanner } from '../../components/slo/DemoTelemetryBanner';
import { ReliabilityOverviewHeader } from '../../components/slo/ReliabilityOverviewHeader';
import { ServiceReliabilityTable } from '../../components/slo/ServiceReliabilityTable';
import { SloPerformanceChart } from '../../components/slo/SloPerformanceChart';
import { ErrorBudgetPanel } from '../../components/slo/ErrorBudgetPanel';
import { BurnRateMatrix } from '../../components/slo/BurnRateMatrix';
import { SloViolationsTable } from '../../components/slo/SloViolationsTable';
import { SloForecastCard } from '../../components/slo/SloForecastCard';
import { ReliabilityRecommendationsPanel } from '../../components/slo/ReliabilityRecommendationsPanel';
import { SloModal } from '../../components/slo/SloModal';
import { Activity, RefreshCw, Plus, Sparkles, Filter } from 'lucide-react';

export const SloIntelligencePage: React.FC = () => {
  const [overview, setOverview] = useState<SloOverview | null>(null);
  const [services, setServices] = useState<ServiceReliability[]>([]);
  const [budgets, setBudgets] = useState<ErrorBudget[]>([]);
  const [burnRates, setBurnRates] = useState<BurnRate[]>([]);
  const [violations, setViolations] = useState<SloViolation[]>([]);
  const [forecasts, setForecasts] = useState<SloForecast[]>([]);
  const [recommendations, setRecommendations] = useState<SloRecommendation[]>([]);
  const [selectedService, setSelectedService] = useState<string>('ALL');
  const [loading, setLoading] = useState<boolean>(true);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const fetchData = async (svc?: string) => {
    setLoading(true);
    const filterSvc = svc && svc !== 'ALL' ? svc : undefined;
    try {
      const [ovData, svcData, ebData, brData, vData, fcData] = await Promise.all([
        sloService.getOverview(),
        sloService.getServices(filterSvc),
        sloService.getErrorBudgets(filterSvc),
        sloService.getBurnRates(filterSvc),
        sloService.getViolations(filterSvc),
        sloService.getForecasts(filterSvc),
      ]);

      setOverview(ovData);
      setServices(svcData);
      setBudgets(ebData);
      setBurnRates(brData);
      setViolations(vData);
      setForecasts(fcData);
    } catch (err) {
      console.error('Failed to load SLO data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await sloService.analyzeSlos();
      setOverview(res.overview);
      setRecommendations(res.recommendations);
    } catch (err) {
      console.error('Failed to analyze SLOs:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    fetchData();
    handleAnalyze();
  }, []);

  const handleCreateSlo = async (payload: Partial<SloObjective>) => {
    await sloService.createObjective(payload);
    fetchData(selectedService);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Action Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400">
            <Activity className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              SLO, SLA & Error Budget Intelligence Center
            </h1>
            <p className="text-xs text-slate-400">
              Real-time service reliability scoring, SLI tracking, error budget consumption, and burn-rate intelligence.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-indigo-950/40 transition-colors"
          >
            <Plus className="w-4 h-4" /> Create SLO
          </button>

          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition-colors"
          >
            <Sparkles className={`w-3.5 h-3.5 text-indigo-400 ${analyzing ? 'animate-spin' : ''}`} />
            Analyze
          </button>

          <button
            onClick={() => fetchData(selectedService)}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Demo Telemetry Banner */}
      <DemoTelemetryBanner
        modeIndicator={overview?.mode_indicator || 'LOCAL FIXTURE TELEMETRY MODE'}
        totalServices={overview?.total_services || 7}
      />

      {/* Overview Cards Header */}
      <ReliabilityOverviewHeader overview={overview} />

      {/* Service Reliability Table */}
      <ServiceReliabilityTable
        services={services}
        onSelectService={(svc) => {
          setSelectedService(svc);
          fetchData(svc);
        }}
      />

      {/* Performance Chart & Error Budget Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SloPerformanceChart selectedService={selectedService} />
        <ErrorBudgetPanel budgets={budgets} />
      </div>

      {/* Burn Rate Matrix */}
      <BurnRateMatrix burnRates={burnRates} />

      {/* Violations Table */}
      <SloViolationsTable violations={violations} />

      {/* Forecast Cards */}
      <SloForecastCard forecasts={forecasts} />

      {/* Recommendations Panel */}
      {recommendations.length > 0 && (
        <ReliabilityRecommendationsPanel recommendations={recommendations} />
      )}

      {/* Create SLO Modal */}
      <SloModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateSlo}
      />
    </div>
  );
};
