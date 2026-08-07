import React from "react";
import { Terminal, X, CheckCircle2, AlertTriangle, UserCheck, Play, Loader2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useWorkflowMutations } from "@/hooks/useWorkflows";
import type { WorkflowExecutionItem } from "@/services/workflowService";
import { cn } from "@/lib/utils";

interface WorkflowExecutionDrawerProps {
  execution: WorkflowExecutionItem | null;
  onClose: () => void;
}

export default function WorkflowExecutionDrawer({ execution, onClose }: WorkflowExecutionDrawerProps) {
  const { approveWorkflow, isApproving } = useWorkflowMutations();

  if (!execution) return null;

  const handleDecision = async (decision: "approved" | "rejected") => {
    try {
      await approveWorkflow({
        id: execution.workflow_id,
        payload: {
          approval_id: execution.id,
          decision,
          reason: decision === "approved" ? "Approved by SRE Operator" : "Rejected by Operator",
        },
      });
      onClose();
    } catch (e) {
      alert("Failed to submit approval decision");
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg border-l border-white/10 bg-slate-950 p-6 shadow-2xl space-y-6 overflow-y-auto backdrop-blur-xl">
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <h3 className="text-sm font-bold text-foreground font-mono flex items-center gap-2">
            <Play className="h-4 w-4 text-emerald-400" />
            Execution Run: {execution.id.slice(0, 8)}
          </h3>
          <p className="text-xs text-muted-foreground">
            Trigger: <span className="font-mono text-foreground">{execution.trigger_source}</span> · Duration:{" "}
            <span className="font-mono text-foreground">{execution.duration_ms ?? 0}ms</span>
          </p>
        </div>
        <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Status banner */}
      <div className="flex items-center justify-between rounded-lg border border-white/10 bg-white/[0.02] p-4 text-xs">
        <span className="text-muted-foreground">Run Status</span>
        <Badge
          variant={execution.status === "completed" ? "success" : execution.status === "awaiting_approval" ? "warning" : "danger"}
          className="text-xs"
        >
          {execution.status}
        </Badge>
      </div>

      {/* Manual Approval Gate Prompt */}
      {execution.status === "awaiting_approval" && (
        <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-4 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 text-xs font-semibold">
            <UserCheck className="h-4 w-4" /> Operator Approval Required
          </div>
          <p className="text-xs text-muted-foreground">
            This workflow has paused at an approval gate requiring SRE confirmation before applying production changes.
          </p>
          <div className="flex items-center gap-2 pt-1">
            <Button size="xs" onClick={() => handleDecision("approved")} disabled={isApproving} className="bg-emerald-500 hover:bg-emerald-600 text-white text-xs">
              Approve & Resume
            </Button>
            <Button size="xs" variant="outline" onClick={() => handleDecision("rejected")} disabled={isApproving} className="text-xs text-rose-400 border-rose-500/30">
              Reject & Rollback
            </Button>
          </div>
        </div>
      )}

      {/* Step Timeline */}
      <div className="space-y-3">
        <h4 className="text-xs font-semibold text-foreground font-mono">Step Execution Timeline</h4>
        <div className="space-y-2">
          {execution.step_results?.map((step, idx) => (
            <div key={idx} className="flex items-center justify-between rounded-lg border border-white/10 bg-background/80 p-3 text-xs">
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-[9px] font-mono">
                  #{idx + 1}
                </Badge>
                <span className="font-mono font-semibold text-foreground">{step.label}</span>
              </div>
              <Badge variant={step.status === "completed" ? "success" : "warning"} className="text-[10px]">
                {step.status}
              </Badge>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
