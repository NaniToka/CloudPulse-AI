import { Bell, Globe, Command, Search, Menu, LogOut, User, Settings } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useAuthStore } from "@/store/authStore";
import { useLogout } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";
import { NavLink } from "react-router-dom";

interface NavbarProps {
  sidebarCollapsed: boolean;
  onMobileMenuOpen?: () => void;
}

export default function Navbar({ sidebarCollapsed, onMobileMenuOpen }: NavbarProps) {
  const user = useAuthStore((s) => s.user);
  const { mutate: logout } = useLogout();

  const initials = user
    ? `${user.first_name?.[0] ?? ""}${user.last_name?.[0] ?? ""}`.toUpperCase() || "CP"
    : "CP";

  return (
    <TooltipProvider>
      <header className="flex h-16 shrink-0 items-center justify-between gap-3 border-b border-white/[0.06] px-4 sm:px-6 bg-bg-void/95 backdrop-blur-sm">

        {/* Mobile menu button */}
        <button
          className="lg:hidden flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-bg-overlay hover:text-foreground transition-colors"
          onClick={onMobileMenuOpen}
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Search bar */}
        <div className="flex flex-1 max-w-md items-center">
          <button className="flex h-9 w-full items-center gap-2.5 rounded-lg border border-white/10 bg-bg-elevated px-3 text-sm text-muted-foreground transition-colors hover:border-white/20 hover:bg-bg-overlay">
            <Search className="h-3.5 w-3.5 shrink-0" />
            <span className="flex-1 text-left truncate">Search or run a command…</span>
            <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border border-white/10 bg-bg-surface px-1.5 font-mono text-[10px] text-muted-foreground shrink-0">
              <Command className="h-2.5 w-2.5" />K
            </kbd>
          </button>
        </div>

        {/* Status */}
        <div className="hidden lg:flex items-center gap-2 shrink-0">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-success" />
          </span>
          <span className="text-xs text-muted-foreground whitespace-nowrap">All systems operational</span>
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-2 shrink-0">
          {/* Region */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="hidden sm:flex h-8 items-center gap-1.5 rounded-md border border-white/10 bg-bg-elevated px-2.5 text-xs text-foreground transition-colors hover:bg-bg-overlay">
                <Globe className="h-3 w-3 text-muted-foreground" />
                us-east-1
              </button>
            </TooltipTrigger>
            <TooltipContent>Active region</TooltipContent>
          </Tooltip>

          {/* Notifications */}
          <Tooltip>
            <TooltipTrigger asChild>
              <NavLink
                to="/notifications"
                className="relative flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-bg-overlay hover:text-foreground"
              >
                <Bell className="h-4 w-4" />
                <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-warning text-[9px] font-bold text-white">
                  7
                </span>
              </NavLink>
            </TooltipTrigger>
            <TooltipContent>7 unread notifications</TooltipContent>
          </Tooltip>

          {/* Profile dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2 rounded-md p-1 hover:bg-bg-overlay transition-colors">
                <Avatar className="h-7 w-7 ring-1 ring-white/10">
                  <AvatarImage src={user?.avatar_url ?? undefined} />
                  <AvatarFallback className="text-xs">{initials}</AvatarFallback>
                </Avatar>
                <span className="hidden sm:block text-sm text-foreground max-w-[100px] truncate">
                  {user?.first_name ?? "Guest"}
                </span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>
                <div>
                  <p className="text-foreground font-medium">{user?.first_name} {user?.last_name}</p>
                  <p className="text-muted-foreground font-normal text-[11px] mt-0.5">{user?.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <NavLink to="/settings" className="gap-2">
                  <User className="h-3.5 w-3.5" /> Profile
                </NavLink>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <NavLink to="/settings" className="gap-2">
                  <Settings className="h-3.5 w-3.5" /> Settings
                </NavLink>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-danger focus:text-danger gap-2"
                onClick={() => logout()}
              >
                <LogOut className="h-3.5 w-3.5" /> Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>
    </TooltipProvider>
  );
}
