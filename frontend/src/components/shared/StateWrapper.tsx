import { ReactNode } from "react";
import { AlertTriangle, RefreshCw, Inbox, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface StateWrapperProps {
  isLoading?: boolean;
  isError?: boolean;
  error?: Error | unknown;
  isEmpty?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyAction?: ReactNode;
  onRetry?: () => void;
  loadingMessage?: string;
  children: ReactNode;
  className?: string;
}

export default function StateWrapper({
  isLoading,
  isError,
  error,
  isEmpty,
  emptyTitle = "No Data Found",
  emptyDescription = "There are no records matching your current filter criteria.",
  emptyAction,
  onRetry,
  loadingMessage = "Loading telemetry data…",
  children,
  className,
}: StateWrapperProps) {
  if (isLoading) {
    return (
      <div className={cn("flex flex-col items-center justify-center min-h-[250px] p-8 text-center glass rounded-xl border border-white/[0.06] space-y-3", className)}>
        <Loader2 className="h-8 w-8 text-brand-purple animate-spin" />
        <p className="text-sm font-medium text-muted-foreground animate-pulse">{loadingMessage}</p>
      </div>
    );
  }

  if (isError) {
    const errorMessage =
      error instanceof Error
        ? error.message
        : typeof error === "string"
        ? error
        : "Failed to communicate with CloudPulse AI backend services.";

    return (
      <div className={cn("flex flex-col items-center justify-center min-h-[250px] p-8 text-center glass rounded-xl border border-danger/20 bg-danger/5 space-y-4", className)}>
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-danger/10 text-danger border border-danger/30">
          <AlertTriangle className="h-6 w-6" />
        </div>
        <div className="space-y-1 max-w-md">
          <h3 className="text-base font-semibold text-foreground">API Error Encountered</h3>
          <p className="text-xs text-muted-foreground font-mono leading-relaxed bg-bg-void/50 p-2.5 rounded-lg border border-white/5 break-words">
            {errorMessage}
          </p>
        </div>
        {onRetry && (
          <Button
            onClick={onRetry}
            size="sm"
            variant="outline"
            className="gap-2 bg-bg-elevated border-white/10 hover:bg-bg-overlay text-foreground"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Retry API Request
          </Button>
        )}
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div className={cn("flex flex-col items-center justify-center min-h-[250px] p-8 text-center glass rounded-xl border border-white/[0.06] space-y-4", className)}>
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-bg-elevated text-muted-foreground border border-white/10">
          <Inbox className="h-6 w-6" />
        </div>
        <div className="space-y-1 max-w-sm">
          <h3 className="text-sm font-semibold text-foreground">{emptyTitle}</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">{emptyDescription}</p>
        </div>
        {emptyAction && <div>{emptyAction}</div>}
      </div>
    );
  }

  return <>{children}</>;
}
