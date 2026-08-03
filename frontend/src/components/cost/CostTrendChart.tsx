import React from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import ChartTooltip from "@/components/shared/ChartTooltip";
import type { DailyCostItem } from "@/types/cost";

interface CostTrendChartProps {
  data: DailyCostItem[];
}

export default function CostTrendChart({ data }: CostTrendChartProps) {
  return (
    <Card className="border-white/[0.08] bg-card/80 backdrop-blur-md">
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-sm font-semibold">Daily Spend Trend (30 Days)</CardTitle>
          <p className="text-xs text-muted-foreground">Infrastructure cost tracking over time</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[220px] w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
              <XAxis
                dataKey="date"
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(val) => `$${val}`}
              />
              <Tooltip
                content={({ active, payload }) => (
                  <ChartTooltip
                    active={active}
                    payload={payload?.map((p) => ({
                      name: "Daily Spend",
                      value: p.value as number,
                      color: "#3b82f6",
                    }))}
                    formatter={(v) => `$${v.toLocaleString()}`}
                  />
                )}
              />
              <Area
                type="monotone"
                dataKey="cost"
                stroke="#3b82f6"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#costGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
