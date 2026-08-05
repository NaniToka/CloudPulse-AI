/**
 * AIOpsActionApprovalPanel Component — Explainable AI action recommendation & approval drawer.
 */

import React, { useState } from "react";
import {
  Sparkles,
  CheckCircle2,
  XCircle,
  ShieldAlert,
  Brain,
  Zap,
  Terminal,
  Copy,
  Check,
  Clock,
  AlertTriangle,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { AgentRecommendation } from "@/types/aiops";

interface AIOpsActionApprovalPanelProps {
  recommendation: AgentRecommendation | null;
  onClose: () => void;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  isProcessing?: boolean;
}

export const AIOpsActionApprovalPanel: React.FC<AIOpsActionApprovalPanelProps> = ({
  recommendation,
  onClose,
  onApprove,
  onReject,
  isProcessing,
}) => {
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  if (!recommendation) return null;

  const handleCopy = (cmd: string) => {
    navigator.clipboard.writeText(cmd);
    setCopiedCmd(cmd);
    setTimeout(() => setCopiedCmd(null), 2000);
  };

  return (
    <Dialog open={!!recommendation} onOpenChange={onClose}>
      <DialogContent className="bg-bg-surface border-white/10 text-foreground max-w-3xl max-h-[90vh] overflow-y-auto font-sans text-xs">
        <DialogHeader>
          <div className="flex items-center justify-between border-b border-white/10 pb-3 mr-6">
            <div className="flex items-center gap-2.5">
              <Badge
                className={
                  recommendation.priority === "P0"
                    ? "bg-red-950/70 text-red-400 border-red-500/50"
                    : recommendation.priority === "P1"
                    ? "bg-amber-950/70 text-amber-400 border-amber-500/50"
                    : "bg-blue-950/70 text-blue-400 border-blue-500/50"
                }
              >
                {recommendation.priority}
              </Badge>
              <DialogTitle className="text-base font-bold">{recommendation.title}</DialogTitle>
            </div>

            <Badge variant="outline" className="font-mono text-[10px] border-white/10">
              {recommendation.status}
            </Badge>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* Metrics Header Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded-lg bg-bg-elevated/50 border border-white/5 font-mono text-[11px]">
            <div>
              <span className="text-muted-foreground">Category:</span>
              <p className="font-bold text-brand-purple">{recommendation.category}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Confidence:</span>
              <p className="font-bold text-emerald-400">{Math.round(recommendation.confidence_score * 100)}%</p>
            </div>
            <div>
              <span className="text-muted-foreground">Est Recovery:</span>
              <p className="font-bold text-blue-400">{recommendation.expected_recovery_time}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Automations:</span>
              <p className="font-bold text-foreground">{recommendation.automation_candidates?.length || 0} CLI Steps</p>
            </div>
          </div>

          {/* Explainable AI Executive Summary */}
          <div className="p-3 rounded-lg bg-white/5 border border-white/5 space-y-1">
            <h4 className="font-bold text-foreground font-mono flex items-center gap-1.5">
              <Brain className="h-4 w-4 text-brand-purple" /> Explainable AI Synthesis & Reasoning
            </h4>
            <p className="text-muted-foreground leading-relaxed">{recommendation.executive_summary}</p>
          </div>

          {/* Root Cause & Business Impact */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {recommendation.root_cause && (
              <div className="p-3 rounded-lg bg-red-950/20 border border-red-500/20 space-y-1">
                <h4 className="font-bold text-red-400 font-mono text-xs flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4" /> Root Cause Analysis
                </h4>
                <p className="text-muted-foreground leading-relaxed">{recommendation.root_cause}</p>
              </div>
            )}

            {recommendation.business_impact && (
              <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-500/20 space-y-1">
                <h4 className="font-bold text-amber-400 font-mono text-xs flex items-center gap-1.5">
                  <ShieldAlert className="h-4 w-4" /> Business & SLA Impact
                </h4>
                <p className="text-muted-foreground leading-relaxed">{recommendation.business_impact}</p>
              </div>
            )}
          </div>

          {/* Automation Candidates CLI Commands */}
          {recommendation.automation_candidates && recommendation.automation_candidates.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-bold text-foreground font-mono flex items-center gap-1.5">
                <Terminal className="h-4 w-4 text-emerald-400" /> Automated Remediation Execution Plan
              </h4>

              <div className="space-y-2">
                {recommendation.automation_candidates.map((cmd, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-black/90 border border-white/10 font-mono text-xs text-emerald-400 flex items-start justify-between gap-2"
                  >
                    <code className="whitespace-pre-wrap break-all flex-1">$ {cmd}</code>
                    <button
                      onClick={() => handleCopy(cmd)}
                      className="p-1 rounded bg-white/10 hover:bg-white/20 text-muted-foreground hover:text-white transition-colors shrink-0"
                    >
                      {copiedCmd === cmd ? (
                        <Check className="h-3.5 w-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="h-3.5 w-3.5" />
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Execution Logs */}
          {recommendation.executions && recommendation.executions.length > 0 && (
            <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/20 space-y-2 font-mono">
              <h5 className="font-bold text-emerald-400 text-xs flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4" /> Execution Audit Logs
              </h5>
              <div className="space-y-1">
                {recommendation.executions[0].execution_logs?.map((l, i) => (
                  <p key={i} className="text-[11px] text-muted-foreground">
                    {l}
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* Approval Controls */}
          {recommendation.status === "Pending_Approval" && (
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/10">
              <Button
                variant="outline"
                onClick={() => onReject(recommendation.id)}
                disabled={isProcessing}
                className="gap-1.5 text-xs text-red-400 hover:text-red-300"
              >
                <XCircle className="h-4 w-4" /> Reject Action
              </Button>

              <Button
                onClick={() => onApprove(recommendation.id)}
                disabled={isProcessing}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold gap-1.5 text-xs"
              >
                <CheckCircle2 className="h-4 w-4" /> Approve & Execute Autonomous Action
              </Button>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
