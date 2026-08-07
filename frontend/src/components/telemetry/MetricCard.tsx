import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: number;
  unit: string;
  trend?: "up" | "down" | "stable";
  trendValue?: string;
  description?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, unit, trend, trendValue, description }) => {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Activity className="w-4 h-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {value.toLocaleString()} <span className="text-sm font-normal text-muted-foreground">{unit}</span>
        </div>
        {(trend || description) && (
          <p className="text-xs text-muted-foreground mt-1 flex items-center">
            {trend === "up" && <ArrowUpRight className="w-3 h-3 text-red-500 mr-1" />}
            {trend === "down" && <ArrowDownRight className="w-3 h-3 text-green-500 mr-1" />}
            {trend === "stable" && <Minus className="w-3 h-3 text-blue-500 mr-1" />}
            {trendValue && <span className="mr-1">{trendValue}</span>}
            {description && <span>{description}</span>}
          </p>
        )}
      </CardContent>
    </Card>
  );
};
