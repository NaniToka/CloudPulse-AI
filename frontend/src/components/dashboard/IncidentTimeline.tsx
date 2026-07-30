import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { incidentTimeline } from "@/lib/mockData";
import ChartTooltip from "@/components/shared/ChartTooltip";

const BARS = [
  { key: "p0", label: "P0", color: "#FF2D55" },
  { key: "p1", label: "P1", color: "#EF4444" },
  { key: "p2", label: "P2", color: "#F59E0B" },
  { key: "p3", label: "P3", color: "#3B82F6" },
] as const;

export default function IncidentTimeline() {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-foreground text-sm font-semibold">Incident Timeline</CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">Last 7 days · by severity</p>
          </div>
          <div className="flex gap-3 flex-wrap justify-end">
            {BARS.map((b) => (
              <div key={b.key} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <div className="h-2 w-2 rounded-sm" style={{ background: b.color }} />
                {b.label}
              </div>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pb-4">
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={incidentTimeline} margin={{ top: 4, right: 4, left: -24, bottom: 0 }} barSize={12} barGap={2}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis
              dataKey="day"
              tick={{ fill: "rgba(139,154,179,0.6)", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
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
                />
              )}
              cursor={{ fill: "rgba(255,255,255,0.03)" }}
            />
            {BARS.map((b) => (
              <Bar key={b.key} dataKey={b.key} name={b.label} fill={b.color} radius={[2, 2, 0, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
