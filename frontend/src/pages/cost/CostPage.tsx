import { DollarSign } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import SpendChart from "@/components/dashboard/SpendChart";
import AiWidget from "@/components/dashboard/AiWidget";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { costByService } from "@/lib/mockData";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import ChartTooltip from "@/components/shared/ChartTooltip";

export default function CostPage() {
  const total = costByService.reduce((s, c) => s + c.value, 0);

  return (
    <div className="space-y-6">
      <PageHeader title="Cost Optimizer" subtitle="Cloud spend analysis and optimization recommendations" />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="MTD Spend"       value="$84,230"  icon={<DollarSign className="h-4 w-4" />} trend={{ value: "+3.2% vs last month", direction: "up", positive: false }} />
        <StatCard label="Forecasted"      value="$102,400" subValue="end of month estimate" />
        <StatCard label="Potential Savings" value="$31,850" subValue="AI identified" trend={{ value: "47 recommendations", direction: "up", positive: true }} />
        <StatCard label="Efficiency Score" value="73/100"  subValue="11 critical actions needed" />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2 space-y-4">
          <SpendChart />
          <Card>
            <CardHeader>
              <CardTitle className="text-foreground text-sm font-semibold">Cost by Service</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-6">
                <div className="relative">
                  <ResponsiveContainer width={160} height={160}>
                    <PieChart>
                      <Pie data={costByService} cx="50%" cy="50%" innerRadius={44} outerRadius={68} paddingAngle={3} dataKey="value" stroke="none">
                        {costByService.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                      </Pie>
                      <Tooltip content={({ active, payload }) => (
                        <ChartTooltip active={active} payload={payload?.map((p) => ({ name: (p.payload as any).name, value: p.value as number, color: (p.payload as any).fill }))} formatter={(v) => `$${v.toLocaleString()}`} />
                      )} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <p className="text-[10px] text-muted-foreground">Total</p>
                    <p className="text-sm font-bold gradient-text">${(total / 1000).toFixed(0)}k</p>
                  </div>
                </div>
                <div className="flex-1 space-y-2.5">
                  {costByService.map((item) => (
                    <div key={item.name} className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full shrink-0" style={{ background: item.fill }} />
                        <span className="text-muted-foreground">{item.name}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-muted-foreground">{((item.value / total) * 100).toFixed(0)}%</span>
                        <span className="font-medium text-foreground tabular-nums">${item.value.toLocaleString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <div><AiWidget /></div>
      </div>
    </div>
  );
}
