/**
 * MetricGauge Component — Memoized circular progress gauge for live CPU/Memory/Disk usage.
 */

import React, { memo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MetricGaugeProps {
  title: string;
  value: number; // 0 to 100
  unit?: string;
  subValue?: string;
  icon?: React.ElementType;
}

export const MetricGauge: React.FC<MetricGaugeProps> = memo(({
  title,
  value,
  unit = "%",
  subValue,
  icon: Icon,
}) => {
  const normalized = Math.max(0, Math.min(100, value));

  const getColor = (val: number) => {
    if (val >= 85) return "text-red-400 stroke-red-500 bg-red-950/20 border-red-500/30";
    if (val >= 70) return "text-amber-400 stroke-amber-500 bg-amber-950/20 border-amber-500/30";
    return "text-emerald-400 stroke-emerald-500 bg-emerald-950/20 border-emerald-500/30";
  };

  const getTrackColor = (val: number) => {
    if (val >= 85) return "#ef4444";
    if (val >= 70) return "#f59e0b";
    return "#10b981";
  };

  const strokeDashoffset = 283 - (283 * normalized) / 100;

  return (
    <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-xl flex flex-col justify-between">
      <CardHeader className="p-4 border-b border-white/5 flex items-center justify-between pb-2">
        <CardTitle className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {title}
        </CardTitle>
        {Icon && <Icon className="h-4 w-4 text-brand-purple" />}
      </CardHeader>

      <CardContent className="p-4 flex items-center justify-between">
        <div className="space-y-1">
          <div className={cn("text-2xl font-extrabold font-mono tracking-tight", getColor(value).split(" ")[0])}>
            {value.toFixed(1)}
            <span className="text-sm font-normal text-muted-foreground ml-0.5">{unit}</span>
          </div>
          {subValue && <div className="text-[11px] text-muted-foreground">{subValue}</div>}
        </div>

        {/* Circular SVG Gauge */}
        <div className="relative h-16 w-16 shrink-0 flex items-center justify-center">
          <svg className="h-16 w-16 -rotate-90 transform" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="45"
              className="stroke-white/10"
              strokeWidth="8"
              fill="transparent"
            />
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke={getTrackColor(value)}
              strokeWidth="8"
              strokeDasharray="283"
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              className="transition-all duration-500 ease-out"
            />
          </svg>
          <span className="absolute font-mono text-[10px] font-bold text-foreground">
            {Math.round(value)}%
          </span>
        </div>
      </CardContent>
    </Card>
  );
});

MetricGauge.displayName = "MetricGauge";
