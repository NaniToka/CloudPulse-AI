/**
 * Prediction Timeline Chart Component
 * Visualizes predicted failure probability trajectory over expected time horizons.
 */

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp } from "lucide-react";
import type { Prediction } from "@/types/prediction";

interface PredictionTimelineChartProps {
  predictions: Prediction[];
  isLoading: boolean;
}

export const PredictionTimelineChart: React.FC<PredictionTimelineChartProps> = ({
  predictions,
  isLoading,
}) => {
  if (isLoading) {
    return <div className="h-64 bg-white/5 rounded-xl animate-pulse" />;
  }

  const chartData = predictions.map((p, idx) => ({
    name: p.service,
    probability: p.failure_probability,
    confidence: Math.round(p.confidence_score * 100),
    expectedTime: p.expected_failure_time
      ? new Date(p.expected_failure_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      : `T+${(idx + 1) * 30}m`,
  }));

  return (
    <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-2xl">
      <CardHeader className="p-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-brand-purple" />
          <CardTitle className="text-sm font-semibold text-foreground">
            Failure Probability Trajectory (Next 4 Hours)
          </CardTitle>
        </div>
        <p className="text-xs text-muted-foreground">Forecasted likelihood per service node</p>
      </CardHeader>

      <CardContent className="p-4 h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="probGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.5} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
            <XAxis dataKey="expectedTime" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} domain={[0, 100]} unit="%" />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="bg-bg-elevated p-3 rounded-lg border border-white/10 text-xs shadow-xl space-y-1">
                      <div className="font-bold text-foreground">{d.name}</div>
                      <div className="text-red-400">Failure Probability: {d.probability}%</div>
                      <div className="text-emerald-400">AI Confidence: {d.confidence}%</div>
                      <div className="text-muted-foreground text-[10px]">Expected: {d.expectedTime}</div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Area type="monotone" dataKey="probability" stroke="#ef4444" strokeWidth={2} fill="url(#probGradient)" />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
