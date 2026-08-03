import React from "react";
import {
  Zap,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Shield,
  Layers,
  ArrowUpRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { RecommendationItem } from "@/types/cost";
import { cn } from "@/lib/utils";

interface OptimizationOpportunitiesProps {
  recommendations: RecommendationItem[];
  onStatusChange: (id: string, newStatus: "active" | "dismissed" | "applied") => Promise<void>;
}

const typeBadges: Record<string, { label: string; color: string }> = {
  idle_resource:     { label: "IDLE RESOURCE",      color: "bg-rose-500/10 text-rose-400 border-rose-500/20" },
  wasted_resource:   { label: "WASTED RESOURCE",    color: "bg-orange-500/10 text-orange-400 border-orange-500/20" },
  rightsizing:       { label: "RIGHTSIZING",        color: "bg-amber-500/10 text-amber-400 border-amber-500/20" },
  reserved_instance: { label: "COMMITTED DISCOUNT", color: "bg-purple-500/10 text-purple-400 border-purple-500/20" },
  auto_scaling:      { label: "AUTO SCALING",       color: "bg-sky-500/10 text-sky-400 border-sky-500/20" },
};

const badgeRisk: Record<string, string> = {
  low: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  high: "bg-rose-500/10 text-rose-400 border-rose-500/20",
};

export default function OptimizationOpportunities({
  recommendations,
  onStatusChange,
}: OptimizationOpportunitiesProps) {
  return (
    <Card className="border-white/[0.08] bg-card/80 backdrop-blur-md">
      <CardHeader className="pb-3 border-b border-white/[0.06]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-emerald-400" />
            <CardTitle className="text-sm font-semibold">Optimization Opportunities</CardTitle>
          </div>
          <span className="text-xs text-muted-foreground font-mono">{recommendations.length} active</span>
        </div>
      </CardHeader>

      <CardContent className="p-4 space-y-4">
        {recommendations.length === 0 && (
          <div className="py-12 text-center text-xs text-muted-foreground space-y-1">
            <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-400/40" />
            <p className="font-medium text-sm text-foreground">No Active Optimization Recommendations</p>
            <p className="text-xs text-muted-foreground/80">Your cloud infrastructure is currently optimized.</p>
          </div>
        )}

        {recommendations.map((rec) => {
          const typeCfg = typeBadges[rec.recommendation_type] || typeBadges.rightsizing;
          const riskColor = badgeRisk[rec.risk_level] || badgeRisk.low;

          return (
            <div
              key={rec.id}
              className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] hover:border-white/[0.12] transition-colors space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className={cn("text-[10px] font-mono px-2 py-0.5", typeCfg.color)}>
                    {typeCfg.label}
                  </Badge>
                  <span className="text-xs font-mono text-brand-blue/90">{rec.service}</span>
                </div>

                <div className="flex items-center gap-3 font-mono text-xs">
                  <span className="text-muted-foreground">Current: ${rec.current_cost.toLocaleString()}</span>
                  <span className="font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    Save ${rec.estimated_savings.toLocaleString()}/mo
                  </span>
                </div>
              </div>

              <div className="space-y-1">
                <h4 className="text-sm font-semibold text-foreground">{rec.title}</h4>
                <p className="text-xs text-muted-foreground leading-relaxed">{rec.description}</p>
              </div>

              {rec.ai_summary && (
                <div className="p-2.5 rounded bg-brand-blue/5 border border-brand-blue/10 text-xs text-brand-blue/90 italic">
                  &ldquo;{rec.ai_summary}&rdquo;
                </div>
              )}

              <div className="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-white/[0.04]">
                <div className="flex items-center gap-3 text-[11px] text-muted-foreground font-mono">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" /> Effort: <span className="capitalize text-foreground">{rec.effort_level}</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <Shield className="w-3 h-3" /> Risk:{" "}
                    <Badge variant="outline" className={cn("text-[9px] px-1.5 py-0 capitalize", riskColor)}>
                      {rec.risk_level}
                    </Badge>
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onStatusChange(rec.id, "dismissed")}
                    className="h-7 text-xs text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10"
                  >
                    Dismiss
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => onStatusChange(rec.id, "applied")}
                    className="h-7 text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20"
                  >
                    Apply Fix
                  </Button>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
