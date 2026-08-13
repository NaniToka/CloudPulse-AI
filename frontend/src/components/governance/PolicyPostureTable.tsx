import React from "react";
import { FileCode2 } from "lucide-react";
import type { GovernancePolicyItem } from "@/types/governance";

interface PolicyPostureTableProps {
  policies: GovernancePolicyItem[];
  categoryFilter: string;
  providerFilter: string;
  onCategoryFilterChange: (c: string) => void;
  onProviderFilterChange: (p: string) => void;
}

export default function PolicyPostureTable({
  policies,
  categoryFilter,
  providerFilter,
  onCategoryFilterChange,
  onProviderFilterChange,
}: PolicyPostureTableProps) {
  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">CRITICAL</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">HIGH</span>;
      case "MEDIUM":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">MEDIUM</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-500/20 text-slate-300 border border-slate-500/30">LOW</span>;
    }
  };

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4 font-mono">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <FileCode2 className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm font-semibold text-foreground">Governance Policy Rules Matrix</h3>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <select
            value={categoryFilter}
            onChange={(e) => onCategoryFilterChange(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-black/40 border border-white/10 text-foreground focus:outline-none focus:border-brand-blue"
          >
            <option value="ALL">All Categories</option>
            <option value="Security">Security</option>
            <option value="FinOps">FinOps</option>
            <option value="SRE">SRE</option>
            <option value="Kubernetes">Kubernetes</option>
            <option value="Tagging">Tagging</option>
            <option value="Operations">Operations</option>
          </select>

          <select
            value={providerFilter}
            onChange={(e) => onProviderFilterChange(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-black/40 border border-white/10 text-foreground focus:outline-none focus:border-brand-blue"
          >
            <option value="ALL">All Providers</option>
            <option value="AWS">AWS</option>
            <option value="Azure">Azure</option>
            <option value="GCP">GCP</option>
            <option value="Kubernetes">Kubernetes</option>
            <option value="Multi-Cloud">Multi-Cloud</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-white/10 text-[11px] text-muted-foreground uppercase">
              <th className="py-2.5 px-3">Rule ID</th>
              <th className="py-2.5 px-3">Policy Name</th>
              <th className="py-2.5 px-3">Category</th>
              <th className="py-2.5 px-3">Provider</th>
              <th className="py-2.5 px-3">Severity</th>
              <th className="py-2.5 px-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {policies.map((p) => (
              <tr key={p.id} className="hover:bg-white/[0.02] transition-colors">
                <td className="py-3 px-3 font-semibold text-brand-blue">{p.rule_identifier}</td>
                <td className="py-3 px-3">
                  <span className="font-semibold text-foreground">{p.name}</span>
                  <p className="text-[11px] text-muted-foreground line-clamp-1">{p.description}</p>
                </td>
                <td className="py-3 px-3 text-muted-foreground">{p.category}</td>
                <td className="py-3 px-3 font-semibold text-foreground">{p.provider}</td>
                <td className="py-3 px-3">{getSeverityBadge(p.severity)}</td>
                <td className="py-3 px-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${p.enabled ? "bg-emerald-500/20 text-emerald-300" : "bg-slate-500/20 text-slate-400"}`}>
                    {p.enabled ? "ACTIVE" : "DISABLED"}
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
