import React from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import ChartTooltip from "@/components/shared/ChartTooltip";
import type { ServiceCostItem } from "@/types/cost";

interface CostByServiceChartProps {
  services: ServiceCostItem[];
}

export default function CostByServiceChart({ services }: CostByServiceChartProps) {
  const total = services.reduce((acc, s) => acc + s.cost, 0);

  return (
    <Card className="border-white/[0.08] bg-card/80 backdrop-blur-md">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold">Cost by Service</CardTitle>
        <p className="text-xs text-muted-foreground">Monthly spending distribution</p>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col md:flex-row items-center gap-6">
          <div className="relative shrink-0 mx-auto">
            <ResponsiveContainer width={170} height={170}>
              <PieChart>
                <Pie
                  data={services}
                  cx="50%"
                  cy="50%"
                  innerRadius={48}
                  outerRadius={72}
                  paddingAngle={3}
                  dataKey="cost"
                  stroke="none"
                >
                  {services.map((entry, i) => (
                    <Cell key={i} fill={entry.fill || "#3b82f6"} />
                  ))}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => (
                    <ChartTooltip
                      active={active}
                      payload={payload?.map((p) => ({
                        name: (p.payload as any).service,
                        value: p.value as number,
                        color: (p.payload as any).fill || "#3b82f6",
                      }))}
                      formatter={(v) => `$${v.toLocaleString()}`}
                    />
                  )}
                />
              </PieChart>
            </ResponsiveContainer>

            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-[10px] text-muted-foreground uppercase">Total</span>
              <span className="text-sm font-bold font-mono text-foreground">${(total / 1000).toFixed(1)}k</span>
            </div>
          </div>

          <div className="flex-1 space-y-2.5 w-full">
            {services.map((item) => (
              <div key={item.service} className="flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className="h-2.5 w-2.5 rounded-full shrink-0"
                    style={{ background: item.fill || "#3b82f6" }}
                  />
                  <span className="text-slate-300 font-sans truncate">{item.service}</span>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-muted-foreground">{item.percentage}%</span>
                  <span className="font-semibold text-foreground">${item.cost.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
