import { ReactNode } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";
import { MetricCard, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface StatCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  icon?: ReactNode;
  trend?: { value: string; direction: "up" | "down" | "neutral"; positive?: boolean };
  className?: string;
}

export default function StatCard({ label, value, subValue, icon, trend, className }: StatCardProps) {
  const TrendIcon =
    trend?.direction === "up" ? TrendingUp :
    trend?.direction === "down" ? TrendingDown : Minus;

  const trendColor = !trend ? "" :
    trend.direction === "neutral" ? "text-muted-foreground" :
    trend.positive
      ? (trend.direction === "up" ? "text-success" : "text-danger")
      : (trend.direction === "up" ? "text-danger" : "text-success");

  return (
    <MetricCard className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>{label}</CardTitle>
          {icon && (
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-bg-overlay border border-white/[0.06] text-muted-foreground">
              {icon}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-1">
        <p className="text-3xl font-bold gradient-text tabular-nums leading-none">{value}</p>
        {subValue && <p className="text-xs text-muted-foreground">{subValue}</p>}
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
