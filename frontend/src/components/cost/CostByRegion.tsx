import React from "react";
import { Globe } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { RegionCostItem } from "@/types/cost";

interface CostByRegionProps {
  regions: RegionCostItem[];
}

export default function CostByRegion({ regions }: CostByRegionProps) {
  return (
    <Card className="border-white/[0.08] bg-card/80 backdrop-blur-md">
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-brand-blue" />
          <CardTitle className="text-sm font-semibold">Cost by Region</CardTitle>
        </div>
        <span className="text-xs text-muted-foreground font-mono">{regions.length} regions</span>
      </CardHeader>

      <CardContent className="space-y-4 pt-1">
        {regions.map((r) => (
          <div key={r.region} className="space-y-1.5 font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="font-sans font-medium text-foreground">{r.region}</span>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">{r.percentage}%</span>
                <span className="font-semibold text-foreground">${r.cost.toLocaleString()}</span>
              </div>
            </div>
            <Progress value={r.percentage} className="h-1.5 bg-white/10" />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
