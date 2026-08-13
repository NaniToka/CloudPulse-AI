import React from "react";
import { History, User } from "lucide-react";
import type { AuditEventItem } from "@/types/governance";

interface GovernanceAuditTrailPanelProps {
  auditEvents: AuditEventItem[];
}

export default function GovernanceAuditTrailPanel({ auditEvents }: GovernanceAuditTrailPanelProps) {
  if (!auditEvents || auditEvents.length === 0) return null;

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4 font-mono">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm font-semibold text-foreground">Governance Audit Trail & History</h3>
        </div>
        <span className="text-xs text-muted-foreground">{auditEvents.length} Audit Events</span>
      </div>

      <div className="space-y-2">
        {auditEvents.map((evt) => (
          <div key={evt.id} className="p-3 rounded-lg border border-white/5 bg-black/20 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                {evt.action}
              </span>
              <span className="text-slate-300 font-semibold">{JSON.stringify(evt.details)}</span>
            </div>

            <div className="flex items-center gap-3 text-[11px] text-muted-foreground shrink-0">
              <span className="flex items-center gap-1">
                <User className="w-3 h-3 text-muted-foreground" />
                {evt.actor_user_id ? evt.actor_user_id.slice(0, 8) : "System"}
              </span>
              <span>{new Date(evt.timestamp).toLocaleTimeString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
