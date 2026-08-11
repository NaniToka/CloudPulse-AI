import React, { ReactNode } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";
import { MetricCard, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export interface StatCardProps {
  label?: string;
  title?: string;
  value: string | number;
  subValue?: string;
  subtitle?: string;
  icon?: any;
  trend?: { value: string; direction: "up" | "down" | "neutral"; positive?: boolean };
  variant?: "default" | "success" | "warning" | "danger" | "critical" | string;
  loading?: boolean;
  className?: string;
}

export default function StatCard({
  label,
  title,
  value,
  subValue,
  subtitle,
  icon,
  trend,
  variant,
  loading,
  className,
}: StatCardProps) {
  const displayLabel = label || title || "";
  const displaySubValue = subValue || subtitle || "";

  const TrendIcon =
    trend?.direction === "up" ? TrendingUp :
    trend?.direction === "down" ? TrendingDown : Minus;

  const trendColor = !trend ? "" :
    trend.direction === "neutral" ? "text-muted-foreground" :
    trend.positive
      ? (trend.direction === "up" ? "text-success" : "text-danger")
      : (trend.direction === "up" ? "text-danger" : "text-success");

  const renderIcon = () => {
    if (!icon) return null;
    if (React.isValidElement(icon)) return icon;
    if (typeof icon === "function" || (typeof icon === "object" && icon !== null && "$$typeof" in icon)) {
      const IconComp = icon as React.ElementType;
      return <IconComp className="h-4 w-4" />;
    }
    return null;
  };

  return (
    <MetricCard className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{displayLabel}</CardTitle>
          {icon && (
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-bg-overlay border border-white/[0.06] text-muted-foreground">
              {renderIcon()}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-1">
        {loading ? (
          <div className="h-8 w-20 animate-pulse rounded bg-slate-800" />
        ) : (
          <p className="text-3xl font-bold gradient-text tabular-nums leading-none">{value}</p>
        )}
        {displaySubValue && <p className="text-xs text-muted-foreground">{displaySubValue}</p>}
        {trend && (
          <div className={cn("flex items-center gap-1 text-xs font-medium", trendColor)}>
            <TrendIcon className="h-3 w-3" />
            <span>{trend.value}</span>
          </div>
        )}
      </CardContent>
    </MetricCard>
  );
}
