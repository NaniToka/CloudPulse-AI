import React from "react";
import { DollarSign, Zap, ArrowRight, ShieldCheck, Download } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface EstimatedSavingsCardProps {
  potentialSavings: number;
  onApplyAll?: () => void;
}

export default function EstimatedSavingsCard({ potentialSavings, onApplyAll }: EstimatedSavingsCardProps) {
  return (
    <Card className="relative overflow-hidden border-emerald-500/30 bg-slate-900/80 backdrop-blur-xl shadow-2xl">
      {/* Top ambient gradient accent line */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-500" />
      <div className="absolute -top-12 -right-12 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />

      <CardContent className="p-5 flex flex-col justify-between gap-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-emerald-400">
              <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                <Zap className="w-4 h-4 fill-emerald-400/20" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider">
                Identified Monthly Savings
              </span>
            </div>
            <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              FINOPS OPTIMIZED
            </span>
          </div>

          <div className="flex flex-wrap items-baseline gap-2 pt-1">
            <span className="text-3xl font-black font-mono text-emerald-400 tracking-tight">
              ${potentialSavings.toLocaleString()}
            </span>
            <span className="text-xs text-emerald-300/90 font-medium">
              / month <span className="text-slate-400 font-normal">(~${(potentialSavings * 12).toLocaleString()}/yr)</span>
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed pt-1">
            Reclaiming unattached development resources, committing to Committed Use Discounts (CUD), and rightsizing database instances can reduce monthly cloud spend immediately.
          </p>
        </div>

        <div className="pt-2 border-t border-slate-800/80">
          <Button
            onClick={onApplyAll}
            className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs py-2.5 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 transition-all duration-200"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Savings Plan</span>
            <ArrowRight className="w-3.5 h-3.5 ml-auto" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
