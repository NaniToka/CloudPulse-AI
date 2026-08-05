/**
 * RunbookExecutionTimeline Component — Renders approval workflow and execution logs.
 */

import React from "react";
import { Play, CheckCircle, ShieldAlert, UserCheck, Terminal, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { Runbook, RunbookExecution } from "@/types/runbook";

interface RunbookExecutionTimelineProps {
  runbook: Runbook;
  onApprove: () => void;
  onExecute: () => void;
  isApproving?: boolean;
  isExecuting?: boolean;
}

export const RunbookExecutionTimeline: React.FC<RunbookExecutionTimelineProps> = ({
  runbook,
  onApprove,
  onExecute,
  isApproving,
  isExecuting,
}) => {
  const latestExec: RunbookExecution | undefined = runbook.executions?.[0];

  return (
    <div className="space-y-4 my-4 p-4 rounded-xl bg-bg-elevated/40 border border-white/10">
      {/* Approval & Execution Control Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-white/10 pb-3">
        <div className="flex items-center gap-2">
          <Badge
            className={
              runbook.status === "Completed"
                ? "bg-emerald-950/60 text-emerald-400 border-emerald-500/40"
                : runbook.status === "Approved"
                ? "bg-blue-950/60 text-blue-400 border-blue-500/40"
                : runbook.status === "Executing"
                ? "bg-purple-950/60 text-purple-400 border-purple-500/40 animate-pulse"
                : "bg-amber-950/60 text-amber-400 border-amber-500/40"
            }
          >
            Status: {runbook.status}
          </Badge>
          <span className="text-xs text-muted-foreground font-mono">
            Risk Score: <span className="text-emerald-400 font-bold">{runbook.risk_score}/10</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          {runbook.status === "Draft" && (
            <Button
              size="sm"
              onClick={onApprove}
              disabled={isApproving}
              className="bg-blue-600 hover:bg-blue-500 text-white gap-2 text-xs"
            >
              <UserCheck className="h-3.5 w-3.5" />
              {isApproving ? "Approving..." : "Approve Runbook"}
            </Button>
          )}

          {(runbook.status === "Approved" || runbook.status === "Draft") && (
            <Button
              size="sm"
              onClick={onExecute}
              disabled={isExecuting}
              className="bg-emerald-600 hover:bg-emerald-500 text-white gap-2 text-xs"
            >
              <Play className="h-3.5 w-3.5 fill-current" />
              {isExecuting ? "Executing Steps..." : "Execute Runbook"}
            </Button>
          )}
        </div>
      </div>

      {/* Execution Logs Stream */}
      {latestExec ? (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <Terminal className="h-3.5 w-3.5 text-brand-purple" /> Live Execution Stream
            </span>
            <span>Executed by: {latestExec.executed_by}</span>
          </div>

          <div className="p-3 rounded-lg bg-black/90 border border-white/10 font-mono text-xs text-emerald-400 space-y-1 max-h-40 overflow-y-auto">
            {latestExec.logs_json && latestExec.logs_json.length > 0 ? (
              latestExec.logs_json.map((logLine, idx) => (
                <p key={idx} className="text-xs font-mono">
                  {logLine}
                </p>
              ))
            ) : (
              <p className="text-muted-foreground">Execution initiated. Waiting for step logs...</p>
            )}
          </div>
        </div>
      ) : (
        <div className="text-xs text-muted-foreground font-mono flex items-center gap-2 py-2">
          <Activity className="h-4 w-4 text-brand-purple" />
          <span>No executions recorded yet. Approve and trigger 'Execute Runbook' to initiate automated SRE remediation.</span>
        </div>
      )}
    </div>
  );
};
