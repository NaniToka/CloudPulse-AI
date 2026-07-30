import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { spendData } from "@/lib/mockData";

const SERIES = [
  { key: "compute", label: "Compute", color: "#2563EB" },
  { key: "managed", label: "Managed DB", color: "#7C3AED" },
  { key: "storage", label: "Storage", color: "#A855F7" },
  { key: "network", label: "Network", color: "#06B6D4" },
] as const;

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const total = payload.reduce((s: number, p: any) => s + (p.value ?? 0), 0);
  return (
    <div className="glass rounded-lg border border-white/10 p-3 text-xs shadow-lg min-w-[160px]">
      <p className="font-semibold text-foreground mb-2">{label}</p>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex justify-between gap-4 py-0.5">
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <span className="h-1.5 w-1.5 rounded-full" style={{ background: p.fill }} />
            {p.name}
          </span>
          <span className="font-medium text-foreground">${p.value.toLocaleString()}</span>
        </div>
      ))}
      <div className="mt-2 border-t border-white/10 pt-2 flex justify-between font-semibold text-foreground">
        <span>Total</span>
        <span>${total.toLocaleString()}</span>
      </div>
    </div>
  );
}

// Show every 6th label to avoid crowding
const tickFormatter = (_: string, index: number) =>
  index % 6 === 0 ? spendData[index]?.date ?? "" : "";

export default function SpendChart() {
  const displayed = spendData.slice(-30);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Daily Cloud Spend</CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">Last 30 days • USD</p>
          </div>
          <div className="flex gap-3">
            {SERIES.map((s) => (
              <div key={s.key} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <div className="h-2 w-2 rounded-full" style={{ background: s.color }} />
                {s.label}
              </div>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pb-6">
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={displayed} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <defs>
              {SERIES.map((s) => (
                <linearGradient key={s.key} id={`grad-${s.key}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={s.color} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={s.color} stopOpacity={0} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fill: "rgba(139,154,179,0.7)", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v, i) => (i % 6 === 0 ? v : "")}
            />
            <YAxis
              tick={{ fill: "rgba(139,154,179,0.7)", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: "rgba(255,255,255,0.08)" }} />
            {SERIES.map((s) => (
              <Area
                key={s.key}
                type="monotone"
                dataKey={s.key}
                name={s.label}
                stackId="1"
                stroke={s.color}
                strokeWidth={1.5}
                fill={`url(#grad-${s.key})`}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
