import React, { useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Lock,
  Play,
  RotateCcw,
  ShieldCheck,
  Workflow,
  Wrench,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";
import type { RecommendedAction } from "@/types/incident";

interface Props {
  actions?: RecommendedAction[];
  onExecuteAction?: (actionId: string, authorizedBy: string) => Promise<void>;
  isExecuting?: boolean;
}

export function RemediationPanel({ actions = [], onExecuteAction, isExecuting = false }: Props) {
  const [selectedAction, setSelectedAction] = useState<RecommendedAction | null>(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [authorizerName, setAuthorizerName] = useState("SRE Lead");

  const defaultActions: RecommendedAction[] = [
    {
      id: "act-db-pool-expand",
      title: "Increase DB Connection Pool & Scale Read Replicas",
      description: "Scale PostgreSQL max_connections from 200 to 500 and route read traffic to replica pool.",
      action_type: "scale",
      workflow_id: "wf-db-autoscale",
      automated: true,
      risk_level: "LOW",
    },
    {
      id: "act-pgbouncer-flush",
      title: "Reset PgBouncer Pool & Flush Orphaned Sessions",
      description: "Execute graceful PAUSE and RESUME on PgBouncer to clear stale backend connections without dropping traffic.",
      action_type: "restart",
      workflow_id: "wf-pgbouncer-flush",
      automated: true,
      risk_level: "LOW",
    },
    {
      id: "act-restart-workers",
      title: "Restart Saturated Worker Pods",
      description: "Perform rolling restart of worker pods holding unclosed database sessions.",
      action_type: "restart",
      workflow_id: "wf-k8s-pod-restart",
      automated: true,
      risk_level: "MEDIUM",
    },
  ];

  const items = actions.length > 0 ? actions : defaultActions;

  const handleOpenConfirm = (action: RecommendedAction) => {
    setSelectedAction(action);
    setIsConfirmOpen(true);
  };

  const handleConfirmExecute = async () => {
    if (!selectedAction || !onExecuteAction) return;
    await onExecuteAction(selectedAction.id, authorizerName);
    setIsConfirmOpen(false);
  };

  const getRiskBadge = (risk: string = "LOW") => {
    const r = risk.toUpperCase();
    if (r === "HIGH" || r === "CRITICAL") {
      return (
        <Badge className="bg-red-500/15 text-red-400 border-red-500/30 text-[10px] font-mono">
          HIGH RISK
        </Badge>
      );
    }
    if (r === "MEDIUM") {
      return (
        <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 text-[10px] font-mono">
          MEDIUM RISK
        </Badge>
      );
    }
    return (
      <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 text-[10px] font-mono">
        LOW RISK (SAFE)
      </Badge>
    );
  };

  return (
    <div className="space-y-4">
      {/* Safety Notice */}
      <div className="rounded-lg border border-brand-500/30 bg-brand-500/5 p-3 flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-2 text-brand-300">
          <ShieldCheck className="w-4 h-4 text-brand-400 shrink-0" />
          <span>Autonomous Safety Gate: Destructive actions require explicit engineer authorization.</span>
        </div>
        <Badge variant="outline" className="text-[10px] border-brand-500/40 text-brand-300">
          Human-in-the-Loop
        </Badge>
      </div>

      {/* Action Cards List */}
      <div className="space-y-3">
        {items.map((action, idx) => (
          <div
            key={action.id || idx}
            className="rounded-xl border border-white/[0.08] bg-white/[0.02] p-4 hover:border-brand-500/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
          >
            <div className="space-y-1.5 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-sm font-semibold text-white tracking-wide">
                  {idx + 1}. {action.title}
                </span>
                {getRiskBadge(action.risk_level)}
                {action.workflow_id && (
                  <Badge variant="outline" className="text-[10px] font-mono border-white/20 text-muted-foreground flex items-center gap-1">
                    <Workflow className="w-3 h-3" />
                    {action.workflow_id}
                  </Badge>
                )}
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed font-mono">
                {action.description}
              </p>
            </div>

            <Button
              onClick={() => handleOpenConfirm(action)}
              disabled={isExecuting}
              size="sm"
              className="bg-brand-600 hover:bg-brand-500 text-white font-mono text-xs h-9 px-4 shrink-0 shadow-md flex items-center gap-1.5"
            >
              <Play className="w-3.5 h-3.5" />
              Authorize & Run
            </Button>
          </div>
        ))}
      </div>

      {/* Authorization Confirmation Modal */}
      <Dialog open={isConfirmOpen} onOpenChange={setIsConfirmOpen}>
        <DialogContent className="sm:max-w-[480px] bg-bg-surface border-white/[0.1] text-white">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-base font-mono">
              <Lock className="w-4 h-4 text-brand-400" />
              Authorize Remediation Workflow Execution
            </DialogTitle>
            <DialogDescription className="text-xs text-muted-foreground font-mono">
              Explicit authorization is required before triggering autonomous remediation workflows in production.
            </DialogDescription>
          </DialogHeader>

          {selectedAction && (
            <div className="rounded-lg border border-white/[0.08] bg-white/[0.02] p-4 my-2 space-y-3">
              <div>
                <div className="text-[11px] font-mono text-muted-foreground">Action</div>
                <div className="text-sm font-bold text-white font-mono">{selectedAction.title}</div>
              </div>

              <div>
                <div className="text-[11px] font-mono text-muted-foreground">Workflow Template</div>
                <div className="text-xs font-mono text-brand-400">{selectedAction.workflow_id || "wf-remediation-standard"}</div>
              </div>

              <div>
                <div className="text-[11px] font-mono text-muted-foreground">Risk Level</div>
                <div className="mt-1">{getRiskBadge(selectedAction.risk_level)}</div>
              </div>
            </div>
          )}

          <DialogFooter className="gap-2 sm:gap-0">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsConfirmOpen(false)}
              className="border-white/[0.1] text-xs font-mono"
            >
              Cancel
            </Button>
            <Button
              size="sm"
              disabled={isExecuting}
              onClick={handleConfirmExecute}
              className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-4 h-4 mr-1" />
              Confirm & Execute
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
