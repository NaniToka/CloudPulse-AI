import React, { useEffect, useState } from 'react';
import { CommandCenterOverview, IntelligenceInsight } from '../../types/commandCenter';
import { commandCenterService, FilterParams } from '../../services/commandCenterService';
import { CommandCenterHeader } from '../../components/commandCenter/CommandCenterHeader';
import { ExecutiveHealthMetrics } from '../../components/commandCenter/ExecutiveHealthMetrics';
import { AiExecutiveBrief } from '../../components/commandCenter/AiExecutiveBrief';
import { CriticalAttentionGrid } from '../../components/commandCenter/CriticalAttentionGrid';
import { TopRisksRanking } from '../../components/commandCenter/TopRisksRanking';
import { TopOpportunitiesPanel } from '../../components/commandCenter/TopOpportunitiesPanel';
import { UnifiedServiceHealthGrid } from '../../components/commandCenter/UnifiedServiceHealthGrid';
import { CloudProviderHealthCard } from '../../components/commandCenter/CloudProviderHealthCard';
import { SecurityAndFinOpsSummary } from '../../components/commandCenter/SecurityAndFinOpsSummary';
import { CrossDomainTimelineStream } from '../../components/commandCenter/CrossDomainTimelineStream';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const CommandCenterPage: React.FC = () => {
  const [overview, setOverview] = useState<CommandCenterOverview | null>(null);
  const [filters, setFilters] = useState<FilterParams>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOverview = async (currentFilters?: FilterParams) => {
    setLoading(true);
    setError(null);
    try {
      const data = await commandCenterService.getOverview(currentFilters || filters);
      setOverview(data);
    } catch (err: any) {
      console.error('Failed to fetch Command Center Overview:', err);
      setError(err?.message || 'Failed to load enterprise command center intelligence.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await commandCenterService.analyzeCommandCenter();
      setOverview(res.overview);
    } catch (err: any) {
      console.error('Failed to analyze Command Center:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  useEffect(() => {
    fetchOverview();
    handleAnalyze();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleFilterChange = (newFilters: FilterParams) => {
    setFilters(newFilters);
    fetchOverview(newFilters);
  };

  if (loading && !overview) {
    return (
      <div className="p-12 text-center text-slate-400 space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-indigo-400" />
        <p className="text-sm font-semibold">Loading Enterprise Executive Intelligence Command Center...</p>
      </div>
    );
  }

  if (error && !overview) {
    return (
      <div className="p-8 max-w-xl mx-auto my-12 bg-rose-950/40 border border-rose-500/40 rounded-xl text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
        <div>
          <h3 className="text-lg font-bold text-white">Failed to Load Command Center</h3>
          <p className="text-xs text-rose-200 mt-1">{error}</p>
        </div>
        <button
          onClick={() => fetchOverview()}
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
      <CommandCenterHeader
        filters={filters}
        onFilterChange={handleFilterChange}
        onRefresh={() => fetchOverview()}
        onAnalyze={handleAnalyze}
        loading={loading}
        analyzing={analyzing}
      />

      {/* Executive Health Metrics */}
      <ExecutiveHealthMetrics
        health={overview?.health || null}
        risk={overview?.risk || null}
        activeIncidentsCount={overview?.active_incidents_count || 2}
        monthlySpend={overview?.monthly_spend || 42500.0}
        potentialSavings={overview?.potential_savings || 3450.0}
      />

      {/* AI Executive Brief */}
      <AiExecutiveBrief brief={overview?.brief || null} />

      {/* Critical Attention Grid */}
      <CriticalAttentionGrid insights={overview?.insights || []} />

      {/* Top 5 Risks & Top Opportunities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <TopRisksRanking risks={overview?.top_risks || []} />
        <TopOpportunitiesPanel opportunities={overview?.opportunities || []} />
      </div>

      {/* Unified Service Health */}
      <UnifiedServiceHealthGrid />

      {/* Cloud Provider & Kubernetes Health */}
      <CloudProviderHealthCard />

      {/* Security & FinOps Summary */}
      <SecurityAndFinOpsSummary />

      {/* Cross-Domain Operational Timeline Stream */}
      <CrossDomainTimelineStream timeline={overview?.timeline || []} />
    </div>
  );
};
