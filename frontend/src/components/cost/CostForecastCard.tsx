import React from "react";
import { TrendingUp, Calendar, Target, ShieldCheck } from "lucide-react";
import type { CostForecastResponse } from "@/types/cost";

interface CostForecastCardProps {
  forecast: CostForecastResponse | null;
}

export default function CostForecastCard({ forecast }: CostForecastCardProps) {
  if (!forecast) return null;

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-semibold text-foreground">FinOps Predictive Spend Forecast</h3>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-mono text-emerald-300">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Confidence: {Math.round(forecast.confidence * 100)}%</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-3.5 rounded-lg bg-black/30 border border-white/5 space-y-1">
          <span className="text-[11px] text-muted-foreground font-mono">7-Day Projected Spend</span>
          <p className="text-lg font-bold font-mono text-foreground">${forecast.forecast_7_day.toLocaleString()}</p>
          <p className="text-[10px] text-muted-foreground">Rolling 7-day linear projection</p>
        </div>

        <div className="p-3.5 rounded-lg bg-black/30 border border-white/5 space-y-1">
          <span className="text-[11px] text-muted-foreground font-mono">30-Day Projected Spend</span>
          <p className="text-lg font-bold font-mono text-foreground">${forecast.forecast_30_day.toLocaleString()}</p>
          <p className="text-[10px] text-muted-foreground">Monthly rolling horizon</p>
        </div>

        <div className="p-3.5 rounded-lg bg-black/30 border border-white/5 space-y-1">
          <span className="text-[11px] text-muted-foreground font-mono">Month-End Estimate</span>
          <p className="text-lg font-bold font-mono text-brand-blue">${forecast.projected_month_end.toLocaleString()}</p>
          <p className="text-[10px] text-muted-foreground">Projected close for active period</p>
        </div>
      </div>

      <div className="text-[11px] text-muted-foreground font-mono bg-black/20 p-2.5 rounded border border-white/5">
        <span className="text-foreground font-semibold">Basis:</span> {forecast.historical_basis} (Trend: {forecast.trend_direction.toUpperCase()})
      </div>
    </div>
  );
}
