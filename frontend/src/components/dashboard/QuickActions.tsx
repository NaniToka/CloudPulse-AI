import { Terminal, MessageSquare, Upload, AlertTriangle, ArrowRight } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";

const actions = [
  {
    icon: Terminal,
    label: "Analyze Logs",
    description: "Search & query recent logs",
    to: "/logs",
    gradient: "from-brand-blue/20 to-transparent",
    iconBg: "bg-brand-blue/20 text-brand-blue",
  },
  {
    icon: MessageSquare,
    label: "Ask AI",
    description: "Chat with your infrastructure",
    to: "/ai",
    gradient: "from-brand-violet/20 to-transparent",
    iconBg: "bg-brand-violet/20 text-brand-purple",
  },
  {
    icon: Upload,
    label: "Upload Logs",
    description: "Import log files for analysis",
    to: "/logs",
    gradient: "from-cyan-500/10 to-transparent",
    iconBg: "bg-cyan-500/20 text-cyan-400",
  },
  {
    icon: AlertTriangle,
    label: "Create Incident",
    description: "Open a new incident ticket",
    to: "/incidents",
    gradient: "from-warning/10 to-transparent",
    iconBg: "bg-warning/20 text-warning",
  },
];

export default function QuickActions() {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {actions.map((action) => (
        <NavLink
          key={action.label}
          to={action.to}
          className={cn(
            "group relative flex flex-col gap-3 overflow-hidden rounded-xl border border-white/[0.08] bg-bg-surface p-4 transition-all duration-200 hover:border-white/15 hover:shadow-glass"
          )}
        >
          {/* Gradient wash */}
          <div className={cn("absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity", action.gradient)} />

          <div className={cn("relative flex h-9 w-9 items-center justify-center rounded-lg", action.iconBg)}>
            <action.icon className="h-4 w-4" />
          </div>

          <div className="relative space-y-0.5">
            <p className="text-sm font-semibold text-foreground">{action.label}</p>
            <p className="text-xs text-muted-foreground leading-snug">{action.description}</p>
          </div>

          <ArrowRight className="relative h-3.5 w-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity self-end" />
        </NavLink>
      ))}
    </div>
  );
}
