import React from "react";
import { DollarSign, Zap, CheckCircle2, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface EstimatedSavingsCardProps {
  potentialSavings: number;
  onApplyAll?: () => void;
}

export default function EstimatedSavingsCard({ potentialSavings, onApplyAll }: EstimatedSavingsCardProps) {
  return (
    <Card className="border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 via-card/80 to-card/90 backdrop-blur-md">
      <CardContent className="p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-emerald-400">
            <Zap className="w-5 h-5 fill-emerald-400/20" />
            <span className="text-xs font-semibold uppercase tracking-wider">
              Identified Monthly Savings
            </span>
          </div>

          <div className="flex items-baseline gap-3">
            <span className="text-3xl font-extrabold font-mono text-emerald-400">
              ${potentialSavings.toLocaleString()}
            </span>
            <span className="text-xs text-emerald-300/80">/ month (~${(potentialSavings * 12).toLocaleString()}/year)</span>
          </div>

          <p className="text-xs text-muted-foreground max-w-xl">
            Reclaiming unattached development resources, committing to Committed Use Discounts (CUD), and rightsizing database instances can reduce monthly cloud spend immediately.
          </p>
        </div>

        <Button
          onClick={onApplyAll}
          className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-semibold gap-2 shrink-0 shadow-lg shadow-emerald-500/20"
        >
          <span>Export Savings Plan</span>
          <ArrowRight className="w-4 h-4" />
        </Button>
      </CardContent>
    </Card>
  );
}
