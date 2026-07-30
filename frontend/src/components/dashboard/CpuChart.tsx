import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cpuData } from "@/lib/mockData";
import ChartTooltip from "@/components/shared/ChartTooltip";

const LINES = [
  { key: "web",    label: "Web",    color: "#2563EB" },
  { key: "api",    label: "API",    color: "#7C3AED" },
  { key: "db",     label: "DB",     color: "#A855F7" },
  { key: "worker", label: "Worker", color: "#06B6D4" },
] as const;

export default function CpuChart() {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-foreground text-sm font-semibold">CPU Usage</CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">Last 24 hours · % utilization</p>
          </div>
          <div className="flex gap-3 flex-wrap justify-end">
            {LINES.map((l) => (
              <div key={l.key} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <div className="h-2 w-2 rounded-full" style={{ background: l.color }} />
                {l.label}
              </div>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pb-4">
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={cpuData} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fill: "rgba(139,154,179,0.6)", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              interval={5}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: "rgba(139,154,179,0.6)", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `${v}%`}
            />
            <ReferenceLine y={80} stroke="rgba(239,68,68,0.3)" strokeDasharray="4 4" />
            <Tooltip
              content={({ active, payload, label }) => (
                <ChartTooltip
                  active={active}
                  payload={payload?.map((p) => ({ name: p.name as string, value: p.value as number, color: p.stroke as string }))}
                  label={label}
                  unit="%"
                />
              )}
              cursor={{ stroke: "rgba(255,255,255,0.06)" }}
            />
            {LINES.map((l) => (
              <Line
                key={l.key}
                type="monotone"
                dataKey={l.key}
                name={l.label}
                stroke={l.color}
                strokeWidth={1.5}
                dot={false}
                activeDot={{ r: 3, strokeWidth: 0 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
