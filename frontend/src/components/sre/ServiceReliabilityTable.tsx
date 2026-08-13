import React from "react";
import { Activity, AlertOctagon, CheckCircle2, Flame, ArrowUpDown } from "lucide-react";
import type { ServiceReliabilityItem } from "@/types/sre";

interface ServiceReliabilityTableProps {
  services: ServiceReliabilityItem[];
  sortBy: string;
  onSortChange: (sort: string) => void;
}

export default function ServiceReliabilityTable({
  services,
  sortBy,
  onSortChange,
}: ServiceReliabilityTableProps) {
  const getRatingBadge = (rating: string) => {
    switch (rating.toUpperCase()) {
      case "EXCELLENT":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">EXCELLENT</span>;
      case "GOOD":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">GOOD</span>;
      case "DEGRADED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">DEGRADED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">CRITICAL</span>;
    }
  };

  const getSloBadge = (status: string) => {
    if (status === "BREACHED") {
      return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">BREACHED</span>;
    }
    if (status === "AT_RISK") {
      return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">AT RISK</span>;
    }
    return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">HEALTHY</span>;
  };

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-brand-blue" />
          <h3 className="text-sm font-semibold text-foreground">Service Reliability Scorecard</h3>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground font-mono">Sort By:</span>
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-black/40 border border-white/10 text-xs font-mono text-foreground focus:outline-none focus:border-brand-blue"
          >
            <option value="worst_reliability">Worst Reliability Score</option>
            <option value="highest_error_rate">Highest Error Rate</option>
            <option value="highest_latency">Highest Latency P95</option>
            <option value="highest_burn_rate">Highest Error Budget Burn</option>
            <option value="most_incidents">Most Incidents</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/10 text-[11px] font-mono text-muted-foreground uppercase">
              <th className="py-2.5 px-3">Service</th>
              <th className="py-2.5 px-3">Reliability Score</th>
              <th className="py-2.5 px-3">Availability</th>
              <th className="py-2.5 px-3">Latency P95</th>
              <th className="py-2.5 px-3">Error Rate</th>
              <th className="py-2.5 px-3">SLO Status</th>
              <th className="py-2.5 px-3">Budget Remaining</th>
              <th className="py-2.5 px-3">Incidents</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-xs font-mono">
            {services.map((svc) => (
              <tr key={svc.service} className="hover:bg-white/[0.02] transition-colors">
                <td className="py-3 px-3 font-semibold text-foreground">{svc.service}</td>
                <td className="py-3 px-3">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-foreground">{svc.reliability_score.toFixed(1)}</span>
                    {getRatingBadge(svc.rating)}
                  </div>
                </td>
                <td className="py-3 px-3 font-bold text-foreground">{svc.availability.toFixed(2)}%</td>
                <td className="py-3 px-3 text-muted-foreground">{svc.latency_p95_ms.toFixed(1)}ms</td>
                <td className={`py-3 px-3 ${svc.error_rate > 0.5 ? "text-rose-400 font-bold" : "text-muted-foreground"}`}>
                  {svc.error_rate.toFixed(2)}%
                </td>
                <td className="py-3 px-3">{getSloBadge(svc.slo_status)}</td>
                <td className="py-3 px-3">
                  <div className="w-24 bg-white/10 rounded-full h-1.5 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        svc.error_budget_remaining_pct <= 20
                          ? "bg-rose-500"
                          : svc.error_budget_remaining_pct <= 50
                          ? "bg-amber-500"
                          : "bg-emerald-400"
                      }`}
                      style={{ width: `${Math.max(0, Math.min(100, svc.error_budget_remaining_pct))}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-muted-foreground">{svc.error_budget_remaining_pct.toFixed(1)}%</span>
                </td>
                <td className="py-3 px-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${svc.active_incidents_count > 0 ? "bg-rose-500/20 text-rose-300" : "text-muted-foreground"}`}>
                    {svc.active_incidents_count}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
