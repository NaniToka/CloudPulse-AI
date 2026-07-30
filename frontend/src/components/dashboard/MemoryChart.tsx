import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { memoryData } from "@/lib/mockData";
import ChartTooltip from "@/components/shared/ChartTooltip";

const AREAS = [
  { key: "used",   label: "Used",   color: "#7C3AED" },
  { key: "cached", label: "Cached", color: "#2563EB" },
  { key: "free",   label: "Free",   color: "#10B981" },
] as const;

export default function MemoryChart() {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-foreground text-sm font-semibold">Memory Usage</CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">Last 24 hours · % of total RAM</p>
          </div>
          <div className="flex gap-3 flex-wrap justify-end">
            {AREAS.map((a) => (
              <div key={a.key} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <div className="h-2 w-2 rounded-full" style={{ background: a.color }} />
                {a.label}
              </div>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pb-4">
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={memoryData} margin={{ top: 4, right: 4, left: -24, bottom: 0 }} stackOffset="expand">
            <defs>
              {AREAS.map((a) => (
                <linearGradient key={a.key} id={`mem-${a.key}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={a.color} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={a.color} stopOpacity={0}   />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fill: "rgba(139,154,179,0.6)", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              interval={5}
            />
            <YAxis
              tickFormatter={(v) => `${Math.round(v * 100)}%`}
              tick={{ fill: "rgba(139,154,179,0.6)", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              content={({ active, payload, label }) => (
                <ChartTooltip
                  active={active}
                  payload={payload?.map((p) => ({ name: p.name as string, value: p.value as number, color: p.fill as string }))}
                  label={label}
                  unit="%"
                />
              )}
              cursor={{ stroke: "rgba(255,255,255,0.06)" }}
            />
            {AREAS.map((a) => (
              <Area
                key={a.key}
                type="monotone"
                dataKey={a.key}
                name={a.label}
                stackId="1"
                stroke={a.color}
                strokeWidth={1.5}
                fill={`url(#mem-${a.key})`}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
