import {
  TrendingDown,
  TrendingUp,
  Activity,
  AlertTriangle,
  DollarSign,
  Bot,
} from "lucide-react";
import { MetricCard, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { healthBreakdown } from "@/lib/mockData";

// ── Health Donut ─────────────────────────────────────────────────────────────
function HealthDonut({ value }: { value: number }) {
  const r = 36;
  const circ = 2 * Math.PI * r;
  const dash = (value / 100) * circ;

  return (
    <div className="relative flex h-[96px] w-[96px] items-center justify-center">
      <svg className="absolute inset-0 -rotate-90" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
        <circle
          cx="48" cy="48" r={r} fill="none"
          stroke="url(#healthGrad)" strokeWidth="8"
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
        />
        <defs>
          <linearGradient id="healthGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#2563EB" />
            <stop offset="100%" stopColor="#A855F7" />
          </linearGradient>
        </defs>
      </svg>
      <span className="text-xl font-bold gradient-text">{value}%</span>
    </div>
  );
}

// ── Mini sparkline ────────────────────────────────────────────────────────────
function Sparkline({ data, color = "#2563EB" }: { data: number[]; color?: string }) {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const W = 80, H = 24;
  const step = W / (data.length - 1);
  const points = data
    .map((v, i) => `${i * step},${H - ((v - min) / range) * H}`)
    .join(" ");

  return (
    <svg width={W} height={H} className="overflow-visible">
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

// ── Card 1: System Health ─────────────────────────────────────────────────────
function HealthCard() {
  return (
    <MetricCard>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>System Health</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4">
          <HealthDonut value={98.4} />
          <div className="space-y-2 flex-1">
            {healthBreakdown.map((item) => (
              <div key={item.name} className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">{item.name}</span>
                <span className={cn(
                  "text-xs font-semibold tabular-nums",
                  item.status === "healthy" ? "text-success" : "text-warning"
                )}>
                  {item.value}%
                </span>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-md bg-bg-overlay px-3 py-1.5 text-xs text-muted-foreground">
          Infrastructure Health Score
        </div>
      </CardContent>
    </MetricCard>
  );
}

// ── Card 2: Active Alerts ─────────────────────────────────────────────────────
function AlertsCard() {
  const spark = [12, 18, 15, 24, 19, 22, 31, 28, 25, 30, 47];
  return (
    <MetricCard>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Active Alerts</CardTitle>
          <AlertTriangle className="h-4 w-4 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-end justify-between">
          <span className="text-5xl font-bold gradient-text">47</span>
          <Sparkline data={spark} color="#EF4444" />
        </div>
        <div className="space-y-1.5">
          {[
            { label: "Critical", count: 6, color: "bg-critical" },
            { label: "High", count: 12, color: "bg-danger" },
            { label: "Medium", count: 29, color: "bg-warning" },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2">
              <div className={cn("h-1.5 w-1.5 rounded-full shrink-0", item.color)} />
              <span className="flex-1 text-xs text-muted-foreground">{item.label}</span>
              <span className="text-xs font-semibold text-foreground tabular-nums">{item.count}</span>
              <div className="h-1 w-20 rounded-full bg-bg-overlay overflow-hidden">
                <div
                  className={cn("h-full rounded-full", item.color)}
                  style={{ width: `${(item.count / 47) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
        <p className="flex items-center gap-1 text-xs text-success">
          <TrendingDown className="h-3 w-3" />
          ↓ 12 fewer than yesterday
        </p>
      </CardContent>
    </MetricCard>
  );
}

// ── Card 3: Cloud Spend ───────────────────────────────────────────────────────
function SpendCard() {
  const spark = [74, 76, 75, 80, 78, 82, 79, 83, 81, 84];
  return (
    <MetricCard>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Cloud Spend MTD</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-end justify-between">
          <div>
            <span className="text-4xl font-bold gradient-text">$84,230</span>
            <div className="flex items-center gap-1.5 mt-1">
              <TrendingUp className="h-3.5 w-3.5 text-warning" />
              <span className="text-xs text-warning font-medium">+3.2% vs last month</span>
            </div>
          </div>
          <Sparkline data={spark} color="#F59E0B" />
        </div>
        {/* Budget bar */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Budget: $120,000</span>
            <span className="text-warning font-medium">70%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-bg-overlay overflow-hidden">
            <div
              className="h-full rounded-full bg-brand-gradient-h transition-all"
              style={{ width: "70%" }}
            />
          </div>
        </div>
        <p className="text-xs text-muted-foreground">
          Forecasted EOMonth: <span className="text-foreground font-medium">$102,400</span>
        </p>
      </CardContent>
    </MetricCard>
  );
}

// ── Card 4: AI Activity ───────────────────────────────────────────────────────
function AiCard() {
  return (
    <MetricCard>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>AI Activity</CardTitle>
          <Bot className="h-4 w-4 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <span className="text-5xl font-bold gradient-text">1,247</span>
          <p className="text-sm text-muted-foreground mt-1">automated resolutions this month</p>
        </div>
        <div className="rounded-lg bg-brand-violet/10 border border-brand-violet/20 px-3 py-2.5 space-y-1">
          <p className="text-xs text-muted-foreground">Engineer time saved</p>
          <p className="text-lg font-bold text-brand-purple">~847 hours</p>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center">
          {[
            { label: "Incidents", value: "312" },
            { label: "Alerts", value: "718" },
            { label: "Cost ops", value: "217" },
          ].map((s) => (
            <div key={s.label} className="rounded-md bg-bg-overlay px-2 py-2">
              <p className="text-sm font-bold text-foreground">{s.value}</p>
              <p className="text-[10px] text-muted-foreground">{s.label}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </MetricCard>
  );
}

export default function KpiCards() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <HealthCard />
      <AlertsCard />
      <SpendCard />
      <AiCard />
    </div>
  );
}
