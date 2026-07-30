import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { networkData } from "@/lib/mockData";
import ChartTooltip from "@/components/shared/ChartTooltip";

export default function NetworkChart() {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-foreground text-sm font-semibold">Network Traffic</CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">Last 24 hours · MB/s</p>
          </div>
          <div className="flex gap-3">
            {[{ label: "Inbound", color: "#2563EB" }, { label: "Outbound", color: "#A855F7" }].map((l) => (
              <div key={l.label} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <div className="h-2 w-2 rounded-full" style={{ background: l.color }} />
                {l.label}
              </div>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pb-4">
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={networkData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="net-in" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#2563EB" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#2563EB" stopOpacity={0}    />
              </linearGradient>
              <linearGradient id="net-out" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#A855F7" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#A855F7" stopOpacity={0}    />
              </linearGradient>
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
              tick={{ fill: "rgba(139,154,179,0.6)", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `${v}`}
            />
            <Tooltip
              content={({ active, payload, label }) => (
                <ChartTooltip
                  active={active}
                  payload={payload?.map((p) => ({ name: p.name as string, value: p.value as number, color: p.fill as string }))}
                  label={label}
                  unit=" MB/s"
                />
              )}
              cursor={{ stroke: "rgba(255,255,255,0.06)" }}
            />
            <Area type="monotone" dataKey="inbound"  name="Inbound"  stroke="#2563EB" strokeWidth={1.5} fill="url(#net-in)"  />
            <Area type="monotone" dataKey="outbound" name="Outbound" stroke="#A855F7" strokeWidth={1.5} fill="url(#net-out)" />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
