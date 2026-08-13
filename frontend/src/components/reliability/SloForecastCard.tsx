import React from 'react';
import { SloForecastItem } from '../../types/reliability';
import { TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react';

interface SloForecastCardProps {
  forecasts: SloForecastItem[];
}

export const SloForecastCard: React.FC<SloForecastCardProps> = ({ forecasts }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-indigo-400" />
          <h3 className="text-base font-bold text-white">SLO & Error Budget Forecasting (7-Day, 30-Day & Month-End)</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Deterministic Trend Projections</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {forecasts.map((fc, idx) => (
          <div key={idx} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono font-bold text-white text-sm">{fc.service || 'Platform Service'}</span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-extrabold ${
                  fc.forecast_status === 'INSUFFICIENT_DATA'
                    ? 'bg-slate-700 text-slate-300 border border-slate-600'
                    : fc.is_compliant_projected
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                }`}
              >
                {fc.forecast_status}
              </span>
            </div>

            {fc.forecast_status === 'INSUFFICIENT_DATA' ? (
              <div className="text-xs text-slate-400 space-y-1">
                <p>{fc.message || 'Insufficient historical telemetry data to calculate forecast.'}</p>
                <div className="text-[11px] text-amber-400 font-mono">Confidence: INSUFFICIENT_DATA</div>
              </div>
            ) : (
              <div className="text-xs text-slate-300 space-y-1.5">
                <div className="flex justify-between">
                  <span className="text-slate-400">Target SLO:</span>
                  <span className="font-mono text-white">{fc.target_slo}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">7-Day Projected SLO:</span>
                  <span className="font-mono text-indigo-300">{fc.projected_7_day_slo_pct}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Month-End Projected SLO:</span>
                  <span className="font-mono font-bold text-emerald-400">{fc.projected_month_end_slo_pct}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Projected Exhaustion Date:</span>
                  <span className="font-mono text-amber-300">{fc.projected_exhaustion_date}</span>
                </div>
                <div className="flex justify-between text-[11px] border-t border-slate-700/50 pt-1.5 text-slate-400">
                  <span>Confidence Score:</span>
                  <span className="font-bold text-indigo-400">{fc.confidence_pct}%</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
