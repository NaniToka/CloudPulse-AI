import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Server,
  DollarSign,
  Terminal,
  AlertTriangle,
  Bell,
  MessageSquare,
  Settings,
  ChevronLeft,
  Zap,
  ChevronDown,
  Activity,
  HardDrive,
  Sparkles,
  Radio,
  GitCommit,
  Bot,
  BookOpen,
  ShieldCheck,
  Building2,
  Cpu,
  Cloud,
  Box,
  Network,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useAuthStore } from "@/store/authStore";

interface SidebarProps {
  collapsed: boolean;
  onCollapse: (v: boolean) => void;
  mobileOpen?: boolean;
  onMobileClose?: () => void;
}

const navGroups = [
  {
    label: "Overview",
    items: [
      { icon: LayoutDashboard, label: "Dashboard",       to: "/dashboard"      },
      { icon: Activity,        label: "Telemetry",       to: "/telemetry"      },
      { icon: Cpu,             label: "AIOps Agent",     to: "/aiops"          },
      { icon: Bot,             label: "RAG AI Chat",     to: "/chat"           },
      { icon: Radio,           label: "Live Monitoring", to: "/monitoring"     },
      { icon: Activity,        label: "AI Copilot",      to: "/ai"             },
    ],
  },
  {
    label: "Infrastructure",
    items: [
      { icon: Radio,      label: "Digital Twin",   to: "/twin"           },
      { icon: Box,        label: "Kubernetes K8s", to: "/k8s"            },
      { icon: Cloud,      label: "Multi-Cloud",    to: "/cloud"          },
      { icon: Server,     label: "Infrastructure", to: "/infrastructure" },
      { icon: HardDrive,  label: "Servers",        to: "/servers"        },
      { icon: Terminal,   label: "Logs",           to: "/logs"           },
      { icon: DollarSign, label: "Cost Optimizer",   to: "/cost"           },
      { icon: ShieldCheck,label: "FinOps Governance", to: "/finops/governance"},
    ],
  },
  {
    label: "Operations",
    items: [
      { icon: Zap,           label: "Workflows",            to: "/workflows"            },
      { icon: ShieldCheck,   label: "AI Security Center",   to: "/security",  badge: 4  },
      { icon: ShieldCheck,   label: "Governance Center",    to: "/governance"           },
      { icon: Activity,      label: "SRE Center",           to: "/sre"                  },
      { icon: Network,       label: "Service Dependencies", to: "/dependencies"         },
      { icon: GitCommit,     label: "Trace Explorer",       to: "/tracing"              },
      { icon: BookOpen,      label: "AI Runbooks",          to: "/runbooks"             },
      { icon: Sparkles,      label: "Predictive AI",        to: "/predictions", badge: 4  },
      { icon: AlertTriangle, label: "Incidents",            to: "/incidents",   badge: 3  },
      { icon: Bell,          label: "Alerts",               to: "/alerts",      badge: 47 },
    ],
  },
  {
    label: "System",
    items: [
      { icon: Building2,     label: "Organization",  to: "/organization"  },
      { icon: Settings,      label: "Settings",      to: "/settings"      },
      { icon: MessageSquare, label: "Notifications",  to: "/notifications", badge: 7 },
    ],
  },
];

function NavItem({
  icon: Icon,
  label,
  to,
  badge,
  collapsed,
  onClick,
}: {
  icon: React.ElementType;
  label: string;
  to: string;
  badge?: number;
  collapsed: boolean;
  onClick?: () => void;
}) {
  const location = useLocation();
  const isActive = location.pathname === to || location.pathname.startsWith(to + "/");

  const inner = (
    <NavLink
      to={to}
      onClick={onClick}
      className={cn(
        "relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all duration-150 group select-none",
        isActive
          ? "bg-brand-gradient text-white shadow-glow-blue"
          : "text-muted-foreground hover:text-foreground hover:bg-white/[0.05]"
      )}
    >
      {isActive && (
        <div className="absolute left-0 inset-y-2 w-[2px] rounded-full bg-white/60" />
      )}
      <Icon
        className={cn(
          "shrink-0",
          collapsed ? "h-[18px] w-[18px]" : "h-4 w-4",
          isActive ? "text-white" : "text-muted-foreground group-hover:text-foreground"
        )}
      />
      {!collapsed && <span className="flex-1 truncate font-medium">{label}</span>}
      {!collapsed && badge && badge > 0 ? (
        <span className={cn(
          "flex h-[18px] min-w-[18px] items-center justify-center rounded-full px-1 text-[10px] font-bold",
          isActive ? "bg-white/25 text-white" : "bg-brand-gradient text-white"
        )}>
          {badge > 99 ? "99+" : badge}
        </span>
      ) : null}
    </NavLink>
  );

  if (collapsed) {
    return (
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>{inner}</TooltipTrigger>
        <TooltipContent side="right" className="flex items-center gap-2">
          {label}
          {badge ? (
            <span className="flex h-4 min-w-4 items-center justify-center rounded-full bg-brand-gradient px-1 text-[10px] font-bold text-white">
              {badge > 99 ? "99+" : badge}
            </span>
          ) : null}
        </TooltipContent>
      </Tooltip>
    );
  }

  return inner;
}

export default function Sidebar({ collapsed, onCollapse, mobileOpen, onMobileClose }: SidebarProps) {
  const user = useAuthStore((s) => s.user);
  const initials = user
    ? `${user.first_name?.[0] ?? ""}${user.last_name?.[0] ?? ""}`.toUpperCase() || "CP"
    : "CP";

  const sidebarContent = (
    <TooltipProvider>
      <aside
        className={cn(
          "relative flex flex-col h-full border-r border-white/[0.06] bg-bg-void transition-all duration-200 ease-out shrink-0",
          collapsed ? "w-[68px]" : "w-[240px]"
        )}
      >
        {/* ── Logo ─────────────────────────────────────────────────── */}
        <div className={cn(
          "flex h-16 shrink-0 items-center border-b border-white/[0.06]",
          collapsed ? "justify-center px-4" : "px-5 gap-3"
        )}>
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-gradient shadow-glow-blue">
            <Zap className="h-4 w-4 text-white" />
          </div>
          {!collapsed && (
            <span className="font-bold text-base gradient-text tracking-tight truncate">
              CloudPulse AI
            </span>
          )}
        </div>

        {/* ── Org switcher ─────────────────────────────────────────── */}
        {!collapsed && (
          <button className="mx-3 mt-3 flex items-center gap-2.5 rounded-lg border border-white/[0.06] bg-bg-surface px-3 py-2 text-left transition-colors hover:bg-bg-elevated">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-brand-violet/20 text-[10px] font-bold text-brand-purple">
              AC
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-foreground truncate">Acme Corp</p>
              <p className="text-[10px] text-muted-foreground">Pro Plan</p>
            </div>
            <ChevronDown className="h-3 w-3 text-muted-foreground shrink-0" />
          </button>
        )}

        {/* ── Nav groups ───────────────────────────────────────────── */}
        <ScrollArea className="flex-1 py-4">
          <nav className="space-y-5 px-3">
            {navGroups.map((group) => (
              <div key={group.label} className="space-y-0.5">
                {!collapsed && (
                  <p className="px-3 pb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/40">
                    {group.label}
                  </p>
                )}
                {group.items.map((item) => (
                  <NavItem
                    key={item.to}
                    {...item}
                    collapsed={collapsed}
                    onClick={onMobileClose}
                  />
                ))}
              </div>
            ))}
          </nav>
        </ScrollArea>

        <Separator />

        {/* ── User footer ──────────────────────────────────────────── */}
        <div className={cn(
          "flex items-center gap-3 p-3 shrink-0",
          collapsed ? "justify-center" : ""
        )}>
          <Tooltip delayDuration={0}>
            <TooltipTrigger asChild>
              <NavLink to="/settings">
                <Avatar className="h-8 w-8 shrink-0 ring-1 ring-white/10">
                  <AvatarImage src={user?.avatar_url ?? undefined} />
                  <AvatarFallback>{initials}</AvatarFallback>
                </Avatar>
              </NavLink>
            </TooltipTrigger>
            {collapsed && (
              <TooltipContent side="right">
                {user?.first_name} {user?.last_name}
              </TooltipContent>
            )}
          </Tooltip>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">
                {user?.first_name ?? "Guest"} {user?.last_name ?? ""}
              </p>
              <p className="text-xs text-muted-foreground capitalize truncate">
                {user?.role ?? "member"}
              </p>
            </div>
          )}
        </div>

        {/* ── Collapse toggle ───────────────────────────────────────── */}
        <Tooltip delayDuration={0}>
          <TooltipTrigger asChild>
            <button
              onClick={() => onCollapse(!collapsed)}
              className="absolute -right-3 top-[72px] flex h-6 w-6 items-center justify-center rounded-full border border-white/10 bg-bg-elevated text-muted-foreground shadow-md hover:text-foreground hover:bg-bg-overlay transition-all z-10"
            >
              <ChevronLeft
                className={cn("h-3 w-3 transition-transform duration-200", collapsed && "rotate-180")}
              />
            </button>
          </TooltipTrigger>
          <TooltipContent side="right">
            {collapsed ? "Expand" : "Collapse"}
          </TooltipContent>
        </Tooltip>
      </aside>
    </TooltipProvider>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden lg:flex">{sidebarContent}</div>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onMobileClose}
          />
          <div className="relative z-10 flex">
            <TooltipProvider>
              <aside className="flex flex-col h-full w-[240px] border-r border-white/[0.06] bg-bg-void">
                <div className="flex h-16 shrink-0 items-center border-b border-white/[0.06] px-5 gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-gradient shadow-glow-blue">
                    <Zap className="h-4 w-4 text-white" />
                  </div>
                  <span className="font-bold text-base gradient-text tracking-tight">CloudPulse AI</span>
                </div>
                <ScrollArea className="flex-1 py-4">
                  <nav className="space-y-5 px-3">
                    {navGroups.map((group) => (
                      <div key={group.label} className="space-y-0.5">
                        <p className="px-3 pb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/40">
                          {group.label}
                        </p>
                        {group.items.map((item) => (
                          <NavItem
                            key={item.to}
                            {...item}
                            collapsed={false}
                            onClick={onMobileClose}
                          />
                        ))}
                      </div>
                    ))}
                  </nav>
                </ScrollArea>
              </aside>
            </TooltipProvider>
          </div>
        </div>
      )}
    </>
  );
}
