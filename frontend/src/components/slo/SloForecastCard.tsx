import React from 'react';
import { SloForecast } from '../../types/slo';
import { TrendingUp, Calendar, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

interface SloForecastCardProps {
  forecasts: SloForecast[];
}

export const SloForecastCard: React.FC<SloForecastCardProps> = ({ forecasts }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-emerald-400" />
          <h3 className="text-base font-semibold text-white">Reliability Forecasting & Month-End Projections</h3>
        </div>
        <span className="text-xs text-slate-400 font-semibold">Model Confidence: 94.5%</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {forecasts.map((fc) => {
          const isCompliant = fc.is_compliant_projected;

          return (
            <div
              key={fc.service}
              className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/60 space-y-3 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-bold text-white text-xs">{fc.service}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      isCompliant
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                    }`}
                  >
                    {isCompliant ? 'PROJECTED COMPLIANT' : 'PROJECTED BREACH'}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                  <div className="p-2 bg-slate-900/60 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">Current Availability</div>
                    <div className="font-bold text-white font-mono mt-0.5">{fc.current_availability_pct}%</div>
                  </div>

                  <div className="p-2 bg-slate-900/60 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">Projected Month-End</div>
                    <div className={`font-bold font-mono mt-0.5 ${isCompliant ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {fc.projected_month_end_slo_pct}%
                    </div>
                  </div>
                </div>

                <div className="text-[11px] text-slate-300 space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Projected Budget Consumption:</span>
                    <span className="font-bold text-white">{fc.projected_budget_consumed_pct}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Projected Exhaustion Date:</span>
                    <span className="font-bold text-amber-400">{fc.projected_exhaustion_date}</span>
                  </div>
                </div>
              </div>

              <div className="text-[10px] text-slate-500 border-t border-slate-700/50 pt-2 flex justify-between">
                <span>Target SLO: {fc.target_slo}%</span>
                <span>Confidence: {fc.confidence_pct}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
