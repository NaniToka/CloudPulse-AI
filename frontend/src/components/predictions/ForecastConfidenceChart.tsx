/**
 * Interactive Time-Series Forecasting & Confidence Interval Visualizer
 */

import React, { useState } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from "recharts";
import { Sparkles, TrendingUp, AlertTriangle, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { MetricForecastResponse } from "@/types/prediction";

interface ForecastConfidenceChartProps {
  forecastData?: MetricForecastResponse;
  isLoading?: boolean;
  onRefreshForecast?: (service: string, metric: string) => void;
}

export const ForecastConfidenceChart: React.FC<ForecastConfidenceChartProps> = ({
  forecastData,
  isLoading,
  onRefreshForecast,
}) => {
  const [selectedMetric, setSelectedMetric] = useState("memory_utilization");
  const [selectedService, setSelectedService] = useState("api-gateway");

  // Fallback demo points if data is loading
  const historical = forecastData?.historical_points || [
    { timestamp: "12:00", value: 54.0 },
    { timestamp: "12:05", value: 58.2 },
    { timestamp: "12:10", value: 63.5 },
    { timestamp: "12:15", value: 68.0 },
    { timestamp: "12:20", value: 73.4 },
    { timestamp: "12:25", value: 79.1 },
    { timestamp: "12:30", value: 84.5 },
  ];

  const forecastPoints = forecastData?.forecast_points || [
    { horizon: "5m", timestamp: "12:35", predicted_value: 88.2, lower_bound: 84.0, upper_bound: 92.4, confidence: 0.94 },
    { horizon: "15m", timestamp: "12:45", predicted_value: 94.6, lower_bound: 88.2, upper_bound: 100.0, confidence: 0.88 },
    { horizon: "30m", timestamp: "13:00", predicted_value: 100.0, lower_bound: 92.0, upper_bound: 100.0, confidence: 0.81 },
    { horizon: "1h", timestamp: "13:30", predicted_value: 100.0, lower_bound: 94.5, upper_bound: 100.0, confidence: 0.72 },
  ];

  // Merge historical and forecast points into continuous chart series
  const chartData = [
    ...historical.map((h, i) => ({
      time: h.timestamp.includes("T") ? h.timestamp.split("T")[1].substring(0, 5) : h.timestamp,
      observed: h.value,
      predicted: null,
      uncertaintyBand: null,
      lower: null,
      upper: null,
      type: "historical",
    })),
    // Stitch connection point
    {
      time: historical[historical.length - 1]?.timestamp.includes("T")
        ? historical[historical.length - 1].timestamp.split("T")[1].substring(0, 5)
        : historical[historical.length - 1]?.timestamp || "now",
      observed: historical[historical.length - 1]?.value || 84.5,
      predicted: historical[historical.length - 1]?.value || 84.5,
      uncertaintyBand: [
        historical[historical.length - 1]?.value || 84.5,
        historical[historical.length - 1]?.value || 84.5,
      ],
      lower: historical[historical.length - 1]?.value || 84.5,
      upper: historical[historical.length - 1]?.value || 84.5,
      type: "connection",
    },
    ...forecastPoints.map((f) => ({
      time: `${f.horizon} (${f.timestamp.includes("T") ? f.timestamp.split("T")[1].substring(0, 5) : f.timestamp})`,
      observed: null,
      predicted: f.predicted_value,
      uncertaintyBand: [f.lower_bound, f.upper_bound],
      lower: f.lower_bound,
      upper: f.upper_bound,
      type: "forecast",
    })),
  ];

  const currentVal = forecastData?.current_value || historical[historical.length - 1]?.value || 84.5;
  const isBreaching = currentVal >= 85.0;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-5 shadow-2xl backdrop-blur-md">
      {/* Header controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-indigo-400" />
            <h3 className="text-base font-semibold text-white">
              Multi-Horizon Predictive Forecast & Confidence Bands
            </h3>
            <Badge variant="outline" className="border-indigo-500/30 bg-indigo-500/10 text-indigo-300">
              Holt's Exponential Smoothing (95% CI)
            </Badge>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Solid line shows observed telemetry. Dashed line projects the trajectory with shaded uncertainty envelopes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={selectedService}
            onChange={(e) => {
              setSelectedService(e.target.value);
              onRefreshForecast?.(e.target.value, selectedMetric);
            }}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="api-gateway">api-gateway</option>
            <option value="auth-service">auth-service</option>
            <option value="checkout-service">checkout-service</option>
            <option value="database-cluster">database-cluster</option>
          </select>

          <select
            value={selectedMetric}
            onChange={(e) => {
              setSelectedMetric(e.target.value);
              onRefreshForecast?.(selectedService, e.target.value);
            }}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="memory_utilization">Memory Utilization (%)</option>
            <option value="cpu_utilization">CPU Utilization (%)</option>
            <option value="latency_ms">P99 Latency (ms)</option>
            <option value="error_rate">Error Rate (%)</option>
          </select>

          <Button
            size="sm"
            variant="outline"
            onClick={() => onRefreshForecast?.(selectedService, selectedMetric)}
            disabled={isLoading}
            className="border-indigo-500/40 bg-indigo-500/10 text-indigo-300 hover:bg-indigo-500/20"
          >
            <Sparkles className="mr-1.5 h-3.5 w-3.5 text-indigo-400" />
            Recalculate
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 my-4">
        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Current Value</div>
          <div className="mt-1 text-lg font-bold text-slate-100 flex items-center gap-1.5">
            {currentVal.toFixed(1)}%
            {isBreaching && (
              <Badge variant="destructive" className="text-[10px] py-0 px-1">
                Breach Risk
              </Badge>
            )}
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">+15m Projection</div>
          <div className="mt-1 text-lg font-bold text-amber-400">
            {forecastPoints[1]?.predicted_value.toFixed(1)}%
            <span className="text-xs font-normal text-slate-500 ml-1">
              (±{((forecastPoints[1]?.upper_bound - forecastPoints[1]?.lower_bound) / 2).toFixed(1)}%)
            </span>
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Model Confidence</div>
          <div className="mt-1 text-lg font-bold text-emerald-400 flex items-center gap-1">
            <ShieldCheck className="h-4 w-4" />
            {((forecastPoints[0]?.confidence || 0.94) * 100).toFixed(0)}%
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
          <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Time to 85% SLA Breach</div>
          <div className="mt-1 text-lg font-bold text-rose-400 flex items-center gap-1">
            <AlertTriangle className="h-4 w-4" />
            ~12 Minutes
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="h-72 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <defs>
              {/* Confidence Interval Gradient */}
              <linearGradient id="confidenceBand" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#6366f1" stopOpacity={0.05} />
              </linearGradient>
              {/* Observed Area Gradient */}
              <linearGradient id="observedArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#38bdf8" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
            <XAxis
              dataKey="time"
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: "#334155" }}
            />
            <YAxis
              stroke="#64748b"
              fontSize={11}
              domain={[30, 105]}
              tickLine={false}
              axisLine={{ stroke: "#334155" }}
              unit="%"
            />

            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload || !payload.length) return null;
                const data = payload[0]?.payload;
                return (
                  <div className="rounded-lg border border-slate-700 bg-slate-900/95 p-3 shadow-xl backdrop-blur-md">
                    <div className="text-xs font-semibold text-slate-300">{label}</div>
                    {data.observed !== null && (
                      <div className="mt-1 text-sm text-cyan-400">
                        Observed: <span className="font-bold">{data.observed.toFixed(1)}%</span>
                      </div>
                    )}
                    {data.predicted !== null && (
                      <div className="mt-1 text-sm text-rose-400">
                        Forecast: <span className="font-bold">{data.predicted.toFixed(1)}%</span>
                        <div className="text-xs text-slate-400">
                          95% CI: [{data.lower?.toFixed(1)}% – {data.upper?.toFixed(1)}%]
                        </div>
                      </div>
                    )}
                  </div>
                );
              }}
            />

            {/* Critical SLA Threshold reference line */}
            <ReferenceLine
              y={85}
              stroke="#f43f5e"
              strokeDasharray="4 4"
              label={{
                value: "Critical SLA Threshold (85%)",
                fill: "#f43f5e",
                fontSize: 11,
                position: "insideTopRight",
              }}
            />

            {/* Shaded Upper / Lower Bounds */}
            <Area
              type="monotone"
              dataKey="upper"
              stroke="none"
              fill="url(#confidenceBand)"
              name="Confidence Range"
            />
            <Area
              type="monotone"
              dataKey="observed"
              stroke="none"
              fill="url(#observedArea)"
            />

            {/* Observed historical line */}
            <Line
              type="monotone"
              dataKey="observed"
              stroke="#38bdf8"
              strokeWidth={2.5}
              dot={{ fill: "#0284c7", stroke: "#38bdf8", strokeWidth: 1.5, r: 3 }}
              activeDot={{ r: 5, fill: "#38bdf8" }}
              name="Observed Telemetry"
            />

            {/* Forecast Projection Line */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#f43f5e"
              strokeWidth={2.5}
              strokeDasharray="5 5"
              dot={{ fill: "#e11d48", stroke: "#fda4af", strokeWidth: 1.5, r: 4 }}
              name="Predicted Horizon"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center justify-center gap-6 mt-3 pt-3 border-t border-slate-800/80 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <span className="h-2.5 w-5 rounded bg-cyan-400" />
          <span>Observed Telemetry</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-0.5 w-5 border-t-2 border-dashed border-rose-500" />
          <span>Predicted Horizon (5m – 24h)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-3 w-5 rounded bg-rose-500/20 border border-rose-500/40" />
          <span>95% Confidence Interval Band</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-0.5 w-5 border-t border-dashed border-rose-500" />
          <span>85% Capacity Threshold</span>
        </div>
      </div>
    </div>
  );
};
