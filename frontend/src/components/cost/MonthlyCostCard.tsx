import React from "react";
import { DollarSign, TrendingUp, TrendingDown, Target, Zap } from "lucide-react";
import StatCard from "@/components/shared/StatCard";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent } from "@/components/ui/card";

interface MonthlyCostCardProps {
  monthlyCost: number;
  projectedCost: number;
  potentialSavings: number;
  efficiencyScore: number;
  percentageChange: number;
}

export default function MonthlyCostCard({
  monthlyCost,
  projectedCost,
  potentialSavings,
  efficiencyScore,
  percentageChange,
}: MonthlyCostCardProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Monthly MTD Spend */}
      <StatCard
        label="MTD Cloud Spend"
        value={`$${monthlyCost.toLocaleString()}`}
        subValue="Month-to-date total"
        icon={<DollarSign className="h-4 w-4 text-brand-blue" />}
        trend={{
          value: `${percentageChange > 0 ? "+" : ""}${percentageChange}% vs last month`,
          direction: percentageChange > 0 ? "up" : "down",
          positive: percentageChange <= 0,
        }}
      />

      {/* 2. End-of-Month Forecast */}
      <StatCard
        label="Forecasted Monthly Spend"
        value={`$${projectedCost.toLocaleString()}`}
        subValue="Projected EOM run-rate"
        icon={<TrendingUp className="h-4 w-4 text-purple-400" />}
      />

      {/* 3. Potential Monthly Savings */}
      <StatCard
        label="Potential Savings"
        value={`$${potentialSavings.toLocaleString()}`}
        subValue="FinOps AI identified"
        icon={<Zap className="h-4 w-4 text-emerald-400" />}
        trend={{
          value: "Actionable recommendations",
          direction: "up",
          positive: true,
        }}
      />

      {/* 4. Efficiency Score */}
      <Card className="border-white/[0.08] bg-card/80 backdrop-blur-md">
        <CardContent className="p-5 flex flex-col justify-between h-full space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
              Efficiency Score
            </span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Target className="h-4 w-4" />
            </div>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-foreground">{efficiencyScore}</span>
            <span className="text-xs text-muted-foreground">/ 100</span>
          </div>

          <div className="space-y-1">
            <Progress value={efficiencyScore} className="h-1.5 bg-white/10" />
            <p className="text-[11px] text-muted-foreground">
              {efficiencyScore >= 80 ? "Optimal cloud efficiency" : "Requires FinOps optimization"}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
