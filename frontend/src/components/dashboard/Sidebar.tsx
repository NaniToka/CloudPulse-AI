import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Server,
  DollarSign,
  Terminal,
  AlertTriangle,
  MessageSquare,
  Settings,
  Bell,
  ChevronLeft,
  Zap,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/store/authStore";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";

interface SidebarProps {
  collapsed: boolean;
  onCollapse: (v: boolean) => void;
}

const navGroups = [
  {
    label: "Overview",
    items: [
      { icon: LayoutDashboard, label: "Dashboard", to: "/dashboard" },
    ],
  },
  {
    label: "Infrastructure",
    items: [
      { icon: Server, label: "Infrastructure", to: "/infrastructure" },
      { icon: DollarSign, label: "Cost Optimizer", to: "/cost" },
      { icon: Terminal, label: "Log Analyzer", to: "/logs" },
    ],
  },
  {
    label: "Operations",
    items: [
      { icon: AlertTriangle, label: "Incident Center", to: "/incidents", badge: 3 },
      { icon: MessageSquare, label: "AI Assistant", to: "/ai" },
    ],
  },
  {
    label: "Management",
    items: [
      { icon: Settings, label: "Settings", to: "/settings" },
      { icon: Bell, label: "Notifications", to: "/notifications", badge: 7 },
    ],
  },
];

function NavItem({
  icon: Icon,
  label,
  to,
  badge,
  collapsed,
}: {
  icon: React.ElementType;
  label: string;
  to: string;
  badge?: number;
  collapsed: boolean;
}) {
  const location = useLocation();
  const isActive = location.pathname === to || location.pathname.startsWith(to + "/");

  const content = (
    <NavLink
      to={to}
      className={cn(
        "relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all duration-150 group",
        isActive
          ? "bg-brand-gradient text-white shadow-glow-blue"
          : "text-muted-foreground hover:text-foreground hover:bg-bg-overlay"
      )}
    >
      {/* Active left accent */}
      {isActive && (
        <div className="absolute left-0 inset-y-1 w-[2px] rounded-full bg-white/60" />
      )}

      <Icon
        className={cn(
          "shrink-0 transition-colors",
          collapsed ? "h-5 w-5" : "h-4 w-4",
          isActive ? "text-white" : "text-muted-foreground group-hover:text-foreground"
        )}
      />

      {!collapsed && (
        <span className="flex-1 truncate font-medium">{label}</span>
      )}

      {!collapsed && badge && badge > 0 ? (
        <span className={cn(
          "flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[10px] font-bold",
          isActive ? "bg-white/25 text-white" : "bg-brand-gradient text-white"
        )}>
          {badge}
        </span>
      ) : null}
    </NavLink>
  );

  if (collapsed) {
    return (
      <Tooltip delayDuration={0}>
        <TooltipTrigger asChild>{content}</TooltipTrigger>
        <TooltipContent side="right">
          <div className="flex items-center gap-2">
            {label}
            {badge ? (
              <span className="flex h-4 min-w-4 items-center justify-center rounded-full bg-brand-gradient px-1 text-[10px] font-bold text-white">
                {badge}
              </span>
            ) : null}
          </div>
        </TooltipContent>
      </Tooltip>
    );
  }

  return content;
}

export default function Sidebar({ collapsed, onCollapse }: SidebarProps) {
  const user = useAuthStore((s) => s.user);

  const initials = user
    ? `${user.first_name?.[0] ?? ""}${user.last_name?.[0] ?? ""}`.toUpperCase() || "CP"
    : "CP";

  return (
    <TooltipProvider>
      <aside
        className={cn(
          "relative flex flex-col h-full border-r border-white/[0.06] bg-bg-void transition-all duration-200 ease-out shrink-0",
          collapsed ? "w-[68px]" : "w-[240px]"
        )}
      >
        {/* Logo */}
        <div className={cn("flex h-16 items-center border-b border-white/[0.06] shrink-0",
          collapsed ? "justify-center px-4" : "px-5 gap-3")}>
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-gradient shadow-glow-blue">
            <Zap className="h-4 w-4 text-white" />
          </div>
          {!collapsed && (
            <span className="font-bold text-base gradient-text tracking-tight">
              CloudPulse AI
            </span>
          )}
        </div>

        {/* Nav */}
        <ScrollArea className="flex-1 py-4">
          <nav className="space-y-5 px-3">
            {navGroups.map((group) => (
              <div key={group.label} className="space-y-1">
                {!collapsed && (
                  <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground/50">
                    {group.label}
                  </p>
                )}
                {group.items.map((item) => (
                  <NavItem key={item.to} {...item} collapsed={collapsed} />
                ))}
              </div>
            ))}
          </nav>
        </ScrollArea>

        <Separator />

        {/* User footer */}
        <div className={cn(
          "flex items-center gap-3 p-3 shrink-0",
          collapsed ? "justify-center" : ""
        )}>
          <Tooltip delayDuration={0}>
            <TooltipTrigger asChild>
              <NavLink to="/profile">
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
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-muted-foreground truncate">{user?.role}</p>
            </div>
          )}
        </div>

        {/* Collapse toggle */}
        <Tooltip delayDuration={0}>
          <TooltipTrigger asChild>
            <button
              onClick={() => onCollapse(!collapsed)}
              className={cn(
                "absolute -right-3 top-20 flex h-6 w-6 items-center justify-center rounded-full border border-white/10 bg-bg-elevated text-muted-foreground shadow-md hover:text-foreground hover:bg-bg-overlay transition-all",
              )}
            >
              <ChevronLeft
                className={cn("h-3 w-3 transition-transform duration-200", collapsed && "rotate-180")}
              />
            </button>
          </TooltipTrigger>
          <TooltipContent side="right">
            {collapsed ? "Expand sidebar" : "Collapse sidebar"}
          </TooltipContent>
        </Tooltip>
      </aside>
    </TooltipProvider>
  );
}
