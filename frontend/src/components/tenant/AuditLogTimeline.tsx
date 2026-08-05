/**
 * AuditLogTimeline Component — Renders organization security audit trail.
 */

import React from "react";
import { ShieldCheck, Clock, User, Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { AuditLog } from "@/types/tenant";

interface AuditLogTimelineProps {
  logs: AuditLog[];
}

export const AuditLogTimeline: React.FC<AuditLogTimelineProps> = ({ logs }) => {
  return (
    <div className="p-5 rounded-2xl bg-bg-surface/90 border border-white/10 shadow-2xl space-y-4 font-sans text-xs">
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <h3 className="text-sm font-bold text-foreground">Security Audit Trail</h3>
        </div>
        <span className="text-[10px] text-muted-foreground font-mono">{logs.length} Logged Events</span>
      </div>

      <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
        {logs.map((l) => (
          <div key={l.id} className="p-3 rounded-xl bg-white/5 border border-white/5 font-mono text-xs flex items-start justify-between gap-3">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Badge className="bg-brand-purple/20 text-brand-purple border-brand-purple/30 text-[10px]">
                  {l.action}
                </Badge>
                <span className="text-muted-foreground text-[10px] flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {new Date(l.created_at).toLocaleString()}
                </span>
              </div>
              <p className="text-foreground text-[11px]">
                {JSON.stringify(l.details)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
