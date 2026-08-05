/**
 * Infrastructure Risk Heatmap Component
 * Displays a color-coded service grid indicating predictive risk levels across regions.
 */

import React from "react";
import { ShieldAlert, Server, Globe, Activity, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ServiceRiskItem } from "@/types/prediction";

interface RiskHeatmapProps {
  items: ServiceRiskItem[];
  selectedService: string;
  onSelectService: (service: string) => void;
  isLoading: boolean;
}

const riskBorderMap: Record<string, string> = {
  Critical: "border-red-500/50 bg-red-950/20 text-red-400 hover:bg-red-950/40",
  High: "border-orange-500/50 bg-orange-950/20 text-orange-400 hover:bg-orange-950/40",
  Medium: "border-amber-500/50 bg-amber-950/20 text-amber-400 hover:bg-amber-950/40",
  Low: "border-emerald-500/50 bg-emerald-950/20 text-emerald-400 hover:bg-emerald-950/40",
};

const riskBadgeVariant: Record<string, "critical" | "danger" | "warning" | "success"> = {
  Critical: "critical",
  High: "danger",
  Medium: "warning",
  Low: "success",
};

export const RiskHeatmap: React.FC<RiskHeatmapProps> = ({
  items,
  selectedService,
  onSelectService,
  isLoading,
}) => {
  return (
    <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-2xl">
      <CardHeader className="p-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-brand-purple animate-pulse" />
          <CardTitle className="text-sm font-semibold text-foreground">
            Infrastructure Risk Heatmap
          </CardTitle>
        </div>
        <p className="text-xs text-muted-foreground">
          Click service node to isolate failure predictions
        </p>
      </CardHeader>

      <CardContent className="p-4">
        {isLoading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 animate-pulse">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-24 rounded-lg bg-white/5" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
            {items.map((item) => {
              const isSelected = selectedService === item.service;
              return (
                <div
                  key={`${item.service}-${item.region}`}
                  onClick={() => onSelectService(isSelected ? "" : item.service)}
                  className={`p-3 rounded-lg border transition-all cursor-pointer flex flex-col justify-between ${
                    riskBorderMap[item.risk_level] || "border-white/10"
                  } ${isSelected ? "ring-2 ring-brand-purple scale-105" : ""}`}
                >
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <span className="font-mono font-bold text-xs truncate">{item.service}</span>
                    <Badge variant={riskBadgeVariant[item.risk_level] || "warning"}>
                      {item.risk_level}
                    </Badge>
                  </div>

                  <div className="text-[11px] text-muted-foreground flex items-center gap-1 my-1">
                    <Globe className="h-3 w-3" /> {item.region}
                  </div>

                  <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[11px]">
                    <span className="text-muted-foreground">Probability</span>
                    <span className="font-bold font-mono text-foreground">
                      {item.failure_probability.toFixed(1)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
