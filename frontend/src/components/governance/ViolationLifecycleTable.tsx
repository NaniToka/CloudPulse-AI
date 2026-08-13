import React from "react";
import { AlertOctagon, ArrowRight } from "lucide-react";
import type { GovernanceViolationItem } from "@/types/governance";

interface ViolationLifecycleTableProps {
  violations: GovernanceViolationItem[];
  statusFilter: string;
  severityFilter: string;
  onStatusFilterChange: (s: string) => void;
  onSeverityFilterChange: (s: string) => void;
  onUpdateStatus: (id: string, status: string) => void;
}

export default function ViolationLifecycleTable({
  violations,
  statusFilter,
  severityFilter,
  onStatusFilterChange,
  onSeverityFilterChange,
  onUpdateStatus,
}: ViolationLifecycleTableProps) {
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

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case "OPEN":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">OPEN</span>;
      case "ACKNOWLEDGED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">ACKNOWLEDGED</span>;
      case "IN_REMEDIATION":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">IN REMEDIATION</span>;
      case "RESOLVED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">RESOLVED</span>;
      case "WAIVED":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">WAIVED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-500/20 text-slate-300">{status}</span>;
    }
  };

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4 font-mono">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <AlertOctagon className="w-5 h-5 text-rose-400" />
          <h3 className="text-sm font-semibold text-foreground">Non-Compliant Resource Violations</h3>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <select
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-black/40 border border-white/10 text-foreground focus:outline-none focus:border-brand-blue"
          >
            <option value="ALL">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="IN_REMEDIATION">In Remediation</option>
            <option value="RESOLVED">Resolved</option>
            <option value="WAIVED">Waived</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => onSeverityFilterChange(e.target.value)}
            className="px-2.5 py-1.5 rounded-lg bg-black/40 border border-white/10 text-foreground focus:outline-none focus:border-brand-blue"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      <div className="space-y-3">
        {violations.map((v) => (
          <div key={v.id} className="p-4 rounded-lg border border-white/5 bg-black/30 space-y-2">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                {getSeverityBadge(v.severity)}
                <h4 className="text-xs font-semibold text-foreground">{v.policy_name}</h4>
                <span className="text-[11px] text-muted-foreground">({v.provider} - {v.region})</span>
              </div>

              <div className="flex items-center gap-2">
                {getStatusBadge(v.status)}
                <select
                  value={v.status}
                  onChange={(e) => onUpdateStatus(v.id, e.target.value)}
                  className="px-2 py-1 rounded bg-white/10 border border-white/10 text-[10px] text-foreground focus:outline-none"
                >
                  <option value="OPEN">OPEN</option>
                  <option value="ACKNOWLEDGED">ACKNOWLEDGE</option>
                  <option value="IN_REMEDIATION">IN REMEDIATION</option>
                  <option value="RESOLVED">RESOLVED</option>
                  <option value="WAIVED">WAIVE</option>
                </select>
              </div>
            </div>

            <p className="text-xs text-slate-300">
              Resource: <strong className="text-foreground">{v.resource_name}</strong> ({v.resource_id})
            </p>
            <p className="text-xs text-muted-foreground">Evidence: {v.evidence}</p>

            <div className="pt-1 flex items-center gap-1.5 text-xs text-brand-blue border-t border-white/5">
              <ArrowRight className="w-3.5 h-3.5" />
              <span>Recommended Action: {v.recommended_action}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
