import React from "react";
import { TrendingUp, Calendar, CheckCircle2 } from "lucide-react";
import type { ReliabilityForecastResponse } from "@/types/sre";

interface ReliabilityForecastCardProps {
  forecast: ReliabilityForecastResponse | null;
}

export default function ReliabilityForecastCard({ forecast }: ReliabilityForecastCardProps) {
  if (!forecast) return null;

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4 font-mono">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-semibold text-foreground">Predictive Reliability Forecast</h3>
        </div>
        <span className="text-xs text-muted-foreground">Confidence: {(forecast.confidence * 100).toFixed(0)}%</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* 24h Forecast */}
        <div className="p-3.5 rounded-lg border border-white/5 bg-black/30 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-foreground">Next 24 Hours</span>
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300">
              {forecast.forecast_24h.slo_status}
            </span>
          </div>
          <div className="text-xs space-y-1 text-muted-foreground">
            <p>Availability: <strong className="text-foreground">{forecast.forecast_24h.availability}%</strong></p>
            <p>Error Rate: <strong className="text-foreground">{forecast.forecast_24h.error_rate}%</strong></p>
            <p>Latency: <strong className="text-foreground">{forecast.forecast_24h.latency_ms}ms</strong></p>
          </div>
        </div>

        {/* 7d Forecast */}
        <div className="p-3.5 rounded-lg border border-white/5 bg-black/30 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-foreground">Next 7 Days</span>
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300">
              {forecast.forecast_7d.slo_status}
            </span>
          </div>
          <div className="text-xs space-y-1 text-muted-foreground">
            <p>Availability: <strong className="text-foreground">{forecast.forecast_7d.availability}%</strong></p>
            <p>Error Rate: <strong className="text-foreground">{forecast.forecast_7d.error_rate}%</strong></p>
            <p>Latency: <strong className="text-foreground">{forecast.forecast_7d.latency_ms}ms</strong></p>
          </div>
        </div>

        {/* 30d Forecast */}
        <div className="p-3.5 rounded-lg border border-white/5 bg-black/30 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-foreground">Next 30 Days</span>
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-300">
              {forecast.forecast_30d.slo_status}
            </span>
          </div>
          <div className="text-xs space-y-1 text-muted-foreground">
            <p>Availability: <strong className="text-foreground">{forecast.forecast_30d.availability}%</strong></p>
            <p>Error Rate: <strong className="text-foreground">{forecast.forecast_30d.error_rate}%</strong></p>
            <p>Latency: <strong className="text-foreground">{forecast.forecast_30d.latency_ms}ms</strong></p>
          </div>
        </div>
      </div>

      <p className="text-[11px] text-muted-foreground">{forecast.historical_basis}</p>
    </div>
  );
}
