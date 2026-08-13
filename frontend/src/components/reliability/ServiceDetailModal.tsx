import React, { useEffect, useState } from 'react';
import { ServiceDetailView, ServiceReliabilityProfile } from '../../types/reliability';
import { reliabilityService } from '../../services/reliabilityService';
import { X, Server, Activity, ShieldCheck, Flame, PieChart, Network, AlertTriangle, RefreshCw, DollarSign, ShieldAlert } from 'lucide-react';

interface ServiceDetailModalProps {
  service: ServiceReliabilityProfile | null;
  onClose: () => void;
}

export const ServiceDetailModal: React.FC<ServiceDetailModalProps> = ({ service, onClose }) => {
  const [detail, setDetail] = useState<ServiceDetailView | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!service) return;

    const fetchDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await reliabilityService.getServiceDetail(service.service_id);
        setDetail(data);
      } catch (err: any) {
        console.error('Failed to fetch service detail:', err);
        setError(err?.message || 'Failed to load service detail.');
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [service]);

  if (!service) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl space-y-6 p-6 relative">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-indigo-500/15 border border-indigo-500/30 rounded-xl text-indigo-400">
              <Server className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-extrabold text-white font-mono">{service.service_name}</h2>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-800 text-slate-300 border border-slate-700">
                  {service.provider} ({service.region})
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">Service Reliability Engineering Profile & Comprehensive Telemetry Detail</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400 space-y-3">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-indigo-400" />
            <p className="text-sm font-semibold">Loading Service Telemetry & Reliability Signals...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-rose-950/40 border border-rose-500/40 rounded-xl text-center space-y-2 text-rose-300">
            <AlertTriangle className="w-8 h-8 mx-auto text-rose-400" />
            <p className="text-xs font-semibold">{error}</p>
          </div>
        ) : detail ? (
          <div className="space-y-6">
            {/* Key Metrics Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
                <div className="text-slate-400 text-[10px] uppercase font-bold">Availability</div>
                <div className="text-lg font-bold font-mono text-emerald-400 mt-1">{detail.profile.availability_pct}%</div>
                <div className="text-[10px] text-slate-500">Target: {detail.profile.slo_target}%</div>
              </div>

              <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
                <div className="text-slate-400 text-[10px] uppercase font-bold">P95 / P99 Latency</div>
                <div className="text-lg font-bold font-mono text-white mt-1">
                  {detail.profile.latency_p95_ms}ms <span className="text-xs text-slate-500">/ {detail.profile.latency_p99_ms}ms</span>
                </div>
                <div className="text-[10px] text-slate-500">P95 Response Time</div>
              </div>

              <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
                <div className="text-slate-400 text-[10px] uppercase font-bold">Error Budget</div>
                <div className="text-lg font-bold font-mono text-indigo-300 mt-1">{detail.profile.error_budget_remaining_pct}%</div>
                <div className="text-[10px] text-slate-500">{detail.profile.error_budget_remaining_sec}s Remaining</div>
              </div>

              <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700">
                <div className="text-slate-400 text-[10px] uppercase font-bold">Burn Rate</div>
                <div className="text-lg font-bold font-mono text-amber-400 mt-1">{detail.profile.burn_rate}x</div>
                <div className="text-[10px] text-slate-500">Risk Score: {detail.profile.risk_score}</div>
              </div>
            </div>

            {/* Cross-Domain Telemetry Summary Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-xl space-y-1">
                <div className="flex items-center gap-1.5 text-slate-400 font-bold uppercase text-[10px]">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Active Anomalies & Risks
                </div>
                <div className="text-base font-bold text-white mt-1">{detail.anomalies_count} Active Anomalies</div>
                <div className="text-slate-400 text-[11px]">Capacity Risk: <strong className="text-amber-300">{detail.capacity_risk}</strong></div>
              </div>

              <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-xl space-y-1">
                <div className="flex items-center gap-1.5 text-slate-400 font-bold uppercase text-[10px]">
                  <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" /> Security Posture
                </div>
                <div className="text-base font-bold text-emerald-400 mt-1">{detail.security_risk_score} pts</div>
                <div className="text-slate-400 text-[11px]">CIS Benchmark Compliance</div>
              </div>

              <div className="p-4 bg-slate-800/50 border border-slate-700 rounded-xl space-y-1">
                <div className="flex items-center gap-1.5 text-slate-400 font-bold uppercase text-[10px]">
                  <DollarSign className="w-3.5 h-3.5 text-indigo-400" /> Estimated Cost Impact
                </div>
                <div className="text-base font-bold text-white mt-1">${detail.cost_impact_monthly.toLocaleString()}/mo</div>
                <div className="text-slate-400 text-[11px]">Cloud Infrastructure Cost</div>
              </div>
            </div>

            {/* Multi-Window Burn Rates */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Multi-Window Burn Rates</h4>
              <div className="grid grid-cols-2 sm:grid-cols-6 gap-2">
                {Object.entries(detail.multi_window_burn_rates).map(([win, winData]) => (
                  <div key={win} className="p-2.5 bg-slate-800/60 border border-slate-700 rounded-lg text-center">
                    <div className="text-[10px] text-slate-400 uppercase font-bold">{win}</div>
                    <div className="text-sm font-mono font-bold text-amber-400 mt-0.5">{winData.burn_rate_x}x</div>
                    <div className="text-[9px] font-bold text-slate-400 mt-0.5">{winData.severity}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">SRE Recommendations for {service.service_name}</h4>
              <div className="space-y-2">
                {detail.recommendations.map((rec) => (
                  <div key={rec.id} className="p-3 bg-slate-800/50 border border-slate-700 rounded-lg space-y-1 text-xs">
                    <div className="flex justify-between font-semibold">
                      <span className="text-indigo-300">{rec.category}</span>
                      <span className="text-amber-400 uppercase text-[10px]">{rec.priority}</span>
                    </div>
                    <p className="text-slate-200 font-medium">{rec.recommended_action}</p>
                    <div className="text-[11px] text-emerald-400">Impact: {rec.expected_reliability_impact}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
