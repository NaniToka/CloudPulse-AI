import { ReactNode } from "react";
import { RefreshCw, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  onRefresh?: () => void;
  isRefreshing?: boolean;
  showDemoBadge?: boolean;
  className?: string;
}

export default function PageHeader({
  title,
  subtitle,
  actions,
  onRefresh,
  isRefreshing,
  showDemoBadge = true,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn("flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between pb-2 border-b border-white/[0.06] mb-6", className)}>
      <div className="space-y-1">
        <div className="flex items-center gap-2.5 flex-wrap">
          <h1 className="text-xl font-bold tracking-tight text-foreground">{title}</h1>
          {showDemoBadge && (
            <span className="inline-flex items-center gap-1 rounded-full border border-brand-purple/30 bg-brand-purple/10 px-2.5 py-0.5 text-[10px] font-semibold text-brand-purple">
              <Sparkles className="h-2.5 w-2.5 animate-pulse" />
              Demo Data
            </span>
          )}
        </div>
        {subtitle && <p className="text-xs text-muted-foreground leading-relaxed">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-2.5 flex-wrap shrink-0">
        {onRefresh && (
          <Button
            onClick={onRefresh}
            variant="outline"
            size="sm"
            disabled={isRefreshing}
            className="gap-2 bg-bg-elevated border-white/10 text-xs text-foreground hover:bg-bg-overlay transition-colors"
          >
            <RefreshCw className={cn("h-3.5 w-3.5 text-muted-foreground", isRefreshing && "animate-spin text-brand-purple")} />
            <span>{isRefreshing ? "Refreshing…" : "Refresh"}</span>
          </Button>
        )}
        {actions}
      </div>
    </div>
  );
}
