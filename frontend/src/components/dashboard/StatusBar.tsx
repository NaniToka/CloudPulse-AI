import { Activity, AlertTriangle, DollarSign, Cpu, Sparkles } from "lucide-react";

const stats = [
  {
    icon: Activity,
    label: "Services",
    items: [
      { label: "Healthy", value: "2,731", color: "text-success" },
      { label: "Degraded", value: "89", color: "text-warning" },
      { label: "Down", value: "27", color: "text-danger" },
    ],
  },
  {
    icon: AlertTriangle,
    label: "Incidents",
    items: [
      { label: "P0", value: "1", color: "text-critical" },
      { label: "P1", value: "2", color: "text-danger" },
      { label: "P2", value: "4", color: "text-warning" },
    ],
  },
  {
    icon: DollarSign,
    label: "Spend MTD",
    items: [
      { label: "$84,230", value: "↑ +3.2%", color: "text-warning" },
    ],
    single: true,
  },
  {
    icon: Cpu,
    label: "Error Rate",
    items: [
      { label: "0.04%", value: "5m avg", color: "text-success" },
    ],
    single: true,
  },
  {
    icon: Sparkles,
    label: "AI Insights",
    items: [
      { label: "6 new", value: "recommendations", color: "text-brand-purple" },
    ],
    single: true,
  },
];

export default function StatusBar() {
  return (
    <div className="glass rounded-xl border border-white/[0.08] px-6 py-4">
      <div className="flex flex-wrap items-center gap-6 lg:gap-0 lg:divide-x lg:divide-white/[0.06]">
        {stats.map((stat) => (
          <div key={stat.label} className="flex items-center gap-4 lg:px-6 first:pl-0 last:pr-0">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-bg-elevated border border-white/[0.06]">
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </div>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/60 mb-1">
                {stat.label}
              </p>
              {stat.single ? (
                <div className="flex items-baseline gap-1.5">
                  <span className={`text-sm font-semibold ${stat.items[0].color}`}>
                    {stat.items[0].label}
                  </span>
                  <span className="text-xs text-muted-foreground">{stat.items[0].value}</span>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  {stat.items.map((item) => (
                    <div key={item.label} className="flex items-center gap-1.5">
                      <span className="text-[11px] font-medium text-muted-foreground">{item.label}</span>
                      <span className={`text-sm font-bold ${item.color}`}>{item.value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
