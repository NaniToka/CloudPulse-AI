/**
 * RunbookStepList Component — Renders step-by-step automation CLI/K8s commands.
 */

import React, { useState } from "react";
import { Terminal, Copy, Check, ShieldCheck, Clock, RotateCcw, CheckCircle, AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { AutomationStep } from "@/types/runbook";

interface RunbookStepListProps {
  steps: AutomationStep[];
}

export const RunbookStepList: React.FC<RunbookStepListProps> = ({ steps }) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (cmd: string, id: string) => {
    navigator.clipboard.writeText(cmd);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-4 my-4">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-bold text-foreground uppercase tracking-wider font-mono flex items-center gap-2">
          <Terminal className="h-4 w-4 text-brand-purple" /> Automated Step-by-Step Recovery Procedure ({steps.length} steps)
        </h4>
      </div>

      <div className="space-y-3">
        {steps.map((step) => (
          <div
            key={step.id || step.step_number}
            className="p-4 rounded-xl bg-bg-surface/90 border border-white/10 space-y-3 shadow-md hover:border-brand-purple/40 transition-colors"
          >
            {/* Step Header */}
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <div className="h-7 w-7 rounded-lg bg-brand-purple/20 border border-brand-purple/30 text-brand-purple font-mono font-bold flex items-center justify-center text-xs">
                  #{step.step_number}
                </div>
                <div>
                  <h5 className="text-xs font-bold text-foreground">{step.title}</h5>
                  {step.description && (
                    <p className="text-[11px] text-muted-foreground mt-0.5">{step.description}</p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <span className="text-[10px] text-muted-foreground font-mono flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {step.estimated_time}
                </span>
                <Badge
                  variant="outline"
                  className={
                    step.status === "Completed"
                      ? "bg-emerald-950/40 text-emerald-400 border-emerald-500/30"
                      : step.status === "Running"
                      ? "bg-blue-950/40 text-blue-400 border-blue-500/30 animate-pulse"
                      : "bg-white/5 text-muted-foreground border-white/10"
                  }
                >
                  {step.status}
                </Badge>
              </div>
            </div>

            {/* Executable CLI Command Block */}
            <div className="relative rounded-lg bg-black/80 border border-white/10 p-3 font-mono text-xs text-emerald-400 flex items-start justify-between gap-2 overflow-x-auto">
              <code className="whitespace-pre-wrap break-all text-xs font-mono select-all">
                $ {step.command}
              </code>

              <button
                onClick={() => handleCopy(step.command, step.id || String(step.step_number))}
                className="p-1 rounded bg-white/10 hover:bg-white/20 text-muted-foreground hover:text-white transition-colors shrink-0"
                title="Copy Command"
              >
                {copiedId === (step.id || String(step.step_number)) ? (
                  <Check className="h-3.5 w-3.5 text-emerald-400" />
                ) : (
                  <Copy className="h-3.5 w-3.5" />
                )}
              </button>
            </div>

            {/* Expected Output & Rollback */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono">
              {step.expected_output && (
                <div className="p-2 rounded bg-white/5 border border-white/5 space-y-0.5">
                  <span className="text-muted-foreground text-[10px] flex items-center gap-1">
                    <CheckCircle className="h-3 w-3 text-emerald-400" /> Expected Output:
                  </span>
                  <p className="text-foreground truncate">{step.expected_output}</p>
                </div>
              )}

              {step.rollback_command && (
                <div className="p-2 rounded bg-red-950/20 border border-red-500/20 space-y-0.5">
                  <span className="text-red-400 text-[10px] flex items-center gap-1">
                    <RotateCcw className="h-3 w-3" /> Rollback Command:
                  </span>
                  <p className="text-muted-foreground truncate">{step.rollback_command}</p>
                </div>
              )}
            </div>

            {/* Verification Method */}
            {step.verification_method && (
              <div className="text-[10px] font-mono text-muted-foreground flex items-center gap-1 pt-1 border-t border-white/5">
                <ShieldCheck className="h-3 w-3 text-blue-400" /> Verification: {step.verification_method}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
