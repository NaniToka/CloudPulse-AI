import React from "react";
import { History, FileText, Trash2, ShieldCheck, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AnalysisListItem } from "@/types/log_analysis";
import { cn } from "@/lib/utils";

interface AnalysisHistoryProps {
  history: AnalysisListItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  isLoading?: boolean;
}

const severityBadges: Record<string, { label: string; badgeVariant: "danger" | "warning" | "info" | "muted" }> = {
  critical: { label: "CRIT", badgeVariant: "danger" },
  high:     { label: "HIGH", badgeVariant: "danger" },
  medium:   { label: "MED",  badgeVariant: "warning" },
  low:      { label: "LOW",  badgeVariant: "info" },
};

export default function AnalysisHistory({
  history,
  selectedId,
  onSelect,
  onDelete,
  isLoading,
}: AnalysisHistoryProps) {
  return (
    <Card className="border-white/[0.08] bg-card/80 backdrop-blur-md">
      <CardHeader className="pb-3 border-b border-white/[0.06]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-brand-blue" />
            <CardTitle className="text-sm font-semibold">Analysis History</CardTitle>
          </div>
          <span className="text-xs text-muted-foreground font-mono">{history.length} records</span>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <div className="max-h-[380px] overflow-y-auto divide-y divide-white/[0.04]">
          {isLoading && (
            <div className="p-6 text-center text-xs text-muted-foreground flex items-center justify-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-brand-blue" />
              <span>Loading log analysis history…</span>
            </div>
          )}

          {!isLoading && history.length === 0 && (
            <div className="p-8 text-center text-xs text-muted-foreground space-y-1">
              <FileText className="w-6 h-6 mx-auto text-muted-foreground/30" />
              <p className="font-medium">No previous log analyses</p>
              <p className="text-[11px] text-muted-foreground/60">Uploaded logs will be saved here.</p>
            </div>
          )}

          {!isLoading &&
            history.map((item) => {
              const isSelected = item.id === selectedId;
              const sevKey = (item.severity || "low").toLowerCase();
              const sevConfig = severityBadges[sevKey] || severityBadges.low;
              const formattedDate = new Date(item.created_at).toLocaleString(undefined, {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              });

              return (
                <div
                  key={item.id}
                  onClick={() => onSelect(item.id)}
                  className={cn(
                    "p-3 transition-colors cursor-pointer flex items-center justify-between gap-2 group",
                    isSelected
                      ? "bg-brand-blue/10 border-l-2 border-brand-blue"
                      : "hover:bg-white/[0.02]"
                  )}
                >
                  <div className="space-y-1 min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <FileText className="w-3.5 h-3.5 text-brand-blue shrink-0" />
                      <span className="text-xs font-semibold truncate text-foreground/90 font-mono">
                        {item.filename}
                      </span>
                      {item.severity && (
                        <Badge variant={sevConfig.badgeVariant} className="text-[9px] px-1.5 py-0 shrink-0">
                          {sevConfig.label}
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                      <span>{formattedDate}</span>
                      <span>&bull;</span>
                      <span className="font-mono text-rose-400/90">{item.error_count + item.critical_count} errs</span>
                      {item.confidence_score != null && (
                        <>
                          <span>&bull;</span>
                          <span className="flex items-center gap-0.5 text-emerald-400 font-mono">
                            <ShieldCheck className="w-3 h-3" />
                            {Math.round(item.confidence_score * 100)}%
                          </span>
                        </>
                      )}
                    </div>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(item.id);
                    }}
                    className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 hover:text-rose-400 hover:bg-rose-500/10 transition-opacity"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                </div>
              );
            })}
        </div>
      </CardContent>
    </Card>
  );
}
