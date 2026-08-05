/**
 * SecurityRiskHeatmap Component — Renders Provider x Severity matrix heatmap.
 */

import React from "react";
import { ShieldAlert, Server } from "lucide-react";
import type { SecurityFinding } from "@/types/security";

interface SecurityRiskHeatmapProps {
  findings: SecurityFinding[];
}

const providers = ["AWS", "GCP", "Azure"] as const;
const severities = ["Critical", "High", "Medium", "Low"] as const;

export const SecurityRiskHeatmap: React.FC<SecurityRiskHeatmapProps> = ({ findings }) => {
  // Count findings per provider & severity
  const matrix: Record<string, Record<string, number>> = {
    AWS: { Critical: 0, High: 0, Medium: 0, Low: 0 },
    GCP: { Critical: 0, High: 0, Medium: 0, Low: 0 },
    Azure: { Critical: 0, High: 0, Medium: 0, Low: 0 },
  };

  findings.forEach((f) => {
    const p = f.provider || "AWS";
    const s = f.severity || "Medium";
    if (matrix[p] && matrix[p][s] !== undefined) {
      matrix[p][s] += 1;
    }
  });

  const getHeatmapColor = (count: number, severity: string) => {
    if (count === 0) return "bg-white/5 text-muted-foreground border-white/5";
    if (severity === "Critical") return "bg-red-950/70 text-red-400 border-red-500/50 shadow-glow-blue";
    if (severity === "High") return "bg-amber-950/70 text-amber-400 border-amber-500/50";
    if (severity === "Medium") return "bg-blue-950/70 text-blue-400 border-blue-500/50";
    return "bg-slate-900 text-slate-300 border-slate-700";
  };

  return (
    <div className="space-y-4 my-4 p-5 rounded-xl bg-bg-surface/90 border border-white/10 shadow-xl font-sans text-xs">
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <h4 className="text-xs font-bold text-foreground font-mono flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-brand-purple" /> Cloud Provider x Risk Severity Heatmap
        </h4>
        <span className="text-[11px] text-muted-foreground font-mono">
          Matrix across {findings.length} active CSPM findings
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono">
          <thead>
            <tr className="border-b border-white/10 text-muted-foreground text-[11px]">
              <th className="py-2 px-3">Cloud Provider</th>
              {severities.map((sev) => (
                <th key={sev} className="py-2 px-3 text-center">
                  {sev}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {providers.map((prov) => (
              <tr key={prov} className="hover:bg-white/5 transition-colors">
                <td className="py-3 px-3 font-bold text-foreground flex items-center gap-2">
                  <Server className="h-3.5 w-3.5 text-brand-purple" /> {prov} Infrastructure
                </td>

                {severities.map((sev) => {
                  const cnt = matrix[prov][sev];
                  return (
                    <td key={sev} className="py-3 px-3 text-center">
                      <div
                        className={`py-2 px-3 rounded-lg border font-bold text-xs inline-block w-16 text-center ${getHeatmapColor(
                          cnt,
                          sev
                        )}`}
                      >
                        {cnt}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
