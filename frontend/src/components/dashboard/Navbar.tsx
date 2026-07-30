import { Search, Bell, Globe, Command } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useAuthStore } from "@/store/authStore";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useLogout } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

export default function Navbar({ sidebarCollapsed }: { sidebarCollapsed: boolean }) {
  const user = useAuthStore((s) => s.user);
  const { mutate: logout } = useLogout();

  const initials = user
    ? `${user.first_name?.[0] ?? ""}${user.last_name?.[0] ?? ""}`.toUpperCase() || "CP"
    : "CP";

  return (
    <TooltipProvider>
      <header className="flex h-16 shrink-0 items-center justify-between gap-4 border-b border-white/[0.06] px-6 bg-bg-void/95 backdrop-blur-sm">
        {/* Left — Command palette trigger */}
        <div className={cn(
          "flex items-center gap-4 transition-all",
          sidebarCollapsed ? "flex-1" : "w-full max-w-md"
        )}>
          <button className="flex h-10 w-full max-w-md items-center gap-3 rounded-lg border border-white/10 bg-bg-elevated px-3.5 text-sm text-muted-foreground transition-colors hover:border-white/20 hover:bg-bg-overlay">
            <Search className="h-4 w-4 shrink-0" />
            <span className="flex-1 text-left">Search or run a command…</span>
            <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border border-white/10 bg-bg-surface px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
              <Command className="h-2.5 w-2.5" />K
            </kbd>
          </button>
        </div>

        {/* Center — Status indicator (optional) */}
        <div className="hidden lg:flex items-center gap-2">
          <div className="h-1.5 w-1.5 rounded-full bg-success animate-pulse-glow" />
          <span className="text-xs text-muted-foreground">All systems operational</span>
        </div>

        {/* Right — Region + Notifications + Profile */}
        <div className="flex items-center gap-3">
          {/* Region selector */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="flex h-9 items-center gap-2 rounded-md border border-white/10 bg-bg-elevated px-3 text-xs text-foreground transition-colors hover:bg-bg-overlay">
                <Globe className="h-3.5 w-3.5 text-muted-foreground" />
                <span className="hidden sm:inline">us-east-1</span>
              </button>
            </TooltipTrigger>
            <TooltipContent>Change region</TooltipContent>
          </Tooltip>

          {/* Notifications */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="relative flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-bg-overlay hover:text-foreground">
                <Bell className="h-4 w-4" />
                <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-warning text-[9px] font-bold text-white">
                  7
                </span>
              </button>
            </TooltipTrigger>
            <TooltipContent>7 new notifications</TooltipContent>
          </Tooltip>

          {/* Profile dropdown */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => logout()}
                className="flex h-9 w-9 items-center justify-center"
              >
                <Avatar className="h-8 w-8 ring-1 ring-white/10">
                  <AvatarImage src={user?.avatar_url ?? undefined} />
                  <AvatarFallback>{initials}</AvatarFallback>
                </Avatar>
              </button>
            </TooltipTrigger>
            <TooltipContent>Logout</TooltipContent>
          </Tooltip>
        </div>
      </header>
    </TooltipProvider>
  );
}
