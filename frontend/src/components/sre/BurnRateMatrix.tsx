import React from "react";
import { Flame, AlertTriangle } from "lucide-react";
import type { BurnRateItem } from "@/types/sre";

interface BurnRateMatrixProps {
  burnRates: BurnRateItem[];
}

export default function BurnRateMatrix({ burnRates }: BurnRateMatrixProps) {
  const getBurnStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case "CRITICAL":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">CRITICAL</span>;
      case "ELEVATED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">ELEVATED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">NORMAL</span>;
    }
  };

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Flame className="w-5 h-5 text-amber-400" />
          <h3 className="text-sm font-semibold text-foreground">Multi-Window Error Budget Burn Rate Matrix</h3>
        </div>
        <span className="text-xs text-muted-foreground font-mono">1h / 6h / 24h / 7d Horizon</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse font-mono text-xs">
          <thead>
            <tr className="border-b border-white/10 text-[11px] text-muted-foreground uppercase">
              <th className="py-2.5 px-3">Service</th>
              <th className="py-2.5 px-3">1-Hour Burn</th>
              <th className="py-2.5 px-3">6-Hour Burn</th>
              <th className="py-2.5 px-3">24-Hour Burn</th>
              <th className="py-2.5 px-3">7-Day Burn</th>
              <th className="py-2.5 px-3">Burn Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {burnRates.map((b) => (
              <tr key={b.service} className="hover:bg-white/[0.02] transition-colors">
                <td className="py-3 px-3 font-semibold text-foreground">{b.service}</td>
                <td className={`py-3 px-3 ${b.burn_1h >= 10.0 ? "text-rose-400 font-bold" : "text-foreground"}`}>{b.burn_1h.toFixed(1)}x</td>
                <td className={`py-3 px-3 ${b.burn_6h >= 3.0 ? "text-amber-400 font-bold" : "text-foreground"}`}>{b.burn_6h.toFixed(1)}x</td>
                <td className="py-3 px-3 text-muted-foreground">{b.burn_24h.toFixed(1)}x</td>
                <td className="py-3 px-3 text-muted-foreground">{b.burn_7d.toFixed(1)}x</td>
                <td className="py-3 px-3">{getBurnStatusBadge(b.status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
