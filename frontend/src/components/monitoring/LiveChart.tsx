/**
 * LiveChart Component — High performance memoized streaming chart for Recharts sliding window.
 */

import React, { memo } from "react";
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
import type { MetricPoint } from "@/types/metric";

interface LiveChartProps {
  title: string;
  data: MetricPoint[];
  dataKey: keyof MetricPoint;
  strokeColor?: string;
  fillGradientId: string;
  unit?: string;
  icon?: React.ElementType;
}

export const LiveChart: React.FC<LiveChartProps> = memo(({
  title,
  data,
  dataKey,
  strokeColor = "#3b82f6",
  fillGradientId,
  unit = "",
  icon: Icon,
}) => {
  const chartPoints = data.map((p) => ({
    time: p.timestamp ? new Date(p.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "",
    val: p[dataKey],
  }));

  return (
    <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-xl">
      <CardHeader className="p-4 border-b border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {Icon && <Icon className="h-4 w-4 text-brand-purple" />}
          <CardTitle className="text-xs font-semibold text-foreground">{title}</CardTitle>
        </div>
        <span className="text-[10px] text-muted-foreground font-mono">
          Last 300 data points
        </span>
      </CardHeader>

      <CardContent className="p-4 h-[200px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartPoints} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id={fillGradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={strokeColor} stopOpacity={0.4} />
                <stop offset="95%" stopColor={strokeColor} stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
            <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} interval="preserveEnd" />
            <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} unit={unit} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const d = payload[0].payload;
                  return (
                    <div className="bg-bg-elevated p-2 rounded border border-white/10 text-xs shadow-xl font-mono">
                      <div className="text-muted-foreground text-[10px]">{d.time}</div>
                      <div className="font-bold text-foreground" style={{ color: strokeColor }}>
                        {d.val} {unit}
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Area
              type="monotone"
              dataKey="val"
              stroke={strokeColor}
              strokeWidth={2}
              fill={`url(#${fillGradientId})`}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
});

LiveChart.displayName = "LiveChart";
