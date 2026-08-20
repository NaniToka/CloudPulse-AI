import React, { useState, useMemo } from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, Calendar, Zap, DollarSign } from "lucide-react";
import type { DailyCostItem } from "@/types/cost";

interface CostTrendChartProps {
  data: DailyCostItem[];
}

export default function CostTrendChart({ data }: CostTrendChartProps) {
  const [timeRange, setTimeRange] = useState<"7D" | "14D" | "30D">("30D");

  const filteredData = useMemo(() => {
    if (!data || data.length === 0) return [];
    if (timeRange === "7D") return data.slice(-7);
    if (timeRange === "14D") return data.slice(-14);
    return data;
  }, [data, timeRange]);

  const stats = useMemo(() => {
    if (filteredData.length === 0) return { avg: 0, peak: 0, total: 0 };
    const costs = filteredData.map((d) => d.cost);
    const total = costs.reduce((a, b) => a + b, 0);
    const peak = Math.max(...costs);
    const avg = Math.round(total / costs.length);
    return { avg, peak, total };
  }, [filteredData]);

  return (
    <Card className="border-slate-800/80 bg-slate-900/70 backdrop-blur-xl shadow-2xl relative overflow-hidden">
      {/* Accent Line */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-500" />

      <CardHeader className="pb-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <TrendingUp className="w-4 h-4" />
            </div>
            <CardTitle className="text-sm font-bold text-slate-100">Daily Spend Trend</CardTitle>
          </div>
          <p className="text-xs text-slate-400 mt-1">Infrastructure cost tracking over time</p>
        </div>

        {/* Time Range Switcher & Quick Stats */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 text-xs">
            <span className="text-slate-400">Avg: <strong className="text-slate-200">${stats.avg.toLocaleString()}/d</strong></span>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400">Peak: <strong className="text-blue-400">${stats.peak.toLocaleString()}</strong></span>
          </div>

          <div className="flex items-center bg-slate-950/80 p-0.5 rounded-lg border border-slate-800">
            {(["7D", "14D", "30D"] as const).map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-2.5 py-1 text-[11px] font-bold rounded-md transition-all ${
                  timeRange === range
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="h-[220px] w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={filteredData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
              <defs>
                <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.45} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" vertical={false} />
              <XAxis
                dataKey="date"
                stroke="#64748b"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                dy={5}
              />
              <YAxis
                stroke="#64748b"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                tickFormatter={(val) => `$${val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}`}
              />
              <Tooltip
                cursor={{ stroke: "rgba(59, 130, 246, 0.4)", strokeWidth: 1.5, strokeDasharray: "4 4" }}
                content={({ active, payload, label }) => {
                  if (!active || !payload || !payload.length) return null;
                  const val = payload[0].value as number;
                  const diffFromAvg = val - stats.avg;
                  const pctDiff = stats.avg ? ((diffFromAvg / stats.avg) * 100).toFixed(1) : 0;
                  return (
                    <div className="bg-slate-950/95 border border-slate-800 p-3 rounded-xl shadow-2xl backdrop-blur-md text-xs space-y-1 font-sans min-w-[170px]">
                      <div className="text-[11px] font-bold text-slate-400 border-b border-slate-800/80 pb-1 flex items-center justify-between">
                        <span>{label}</span>
                        <span className="font-mono text-blue-400">Daily Metric</span>
                      </div>
                      <div className="flex items-baseline justify-between pt-1">
                        <span className="text-slate-300 font-medium">Daily Spend:</span>
                        <span className="font-mono font-extrabold text-blue-400 text-sm">${val.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-slate-400">
                        <span>Vs. Period Avg (${stats.avg.toLocaleString()}):</span>
                        <span className={Number(pctDiff) >= 0 ? "text-amber-400 font-bold" : "text-emerald-400 font-bold"}>
                          {Number(pctDiff) >= 0 ? `+${pctDiff}%` : `${pctDiff}%`}
                        </span>
                      </div>
                    </div>
                  );
                }}
              />
              <ReferenceLine y={stats.avg} stroke="rgba(245, 158, 11, 0.4)" strokeDasharray="3 3" />
              <Area
                type="monotone"
                dataKey="cost"
                stroke="#3b82f6"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#costGradient)"
                activeDot={{ r: 6, stroke: "#60a5fa", strokeWidth: 2, fill: "#1e3a8a" }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
