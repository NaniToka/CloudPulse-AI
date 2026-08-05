/**
 * FindingDetailDrawer Component — Wiz & Google Security Command Center style finding detail modal.
 */

import React, { useState } from "react";
import {
  ShieldAlert,
  Sparkles,
  AlertTriangle,
  FileText,
  Copy,
  Check,
  Zap,
  Award,
  Clock,
  CheckCircle,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { SecurityFinding } from "@/types/security";

interface FindingDetailDrawerProps {
  finding: SecurityFinding | null;
  onClose: () => void;
}

export const FindingDetailDrawer: React.FC<FindingDetailDrawerProps> = ({
  finding,
  onClose,
}) => {
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  if (!finding) return null;

  const ai = finding.ai_analysis;

  const handleCopy = (cmd: string, idx: number) => {
    navigator.clipboard.writeText(cmd);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  return (
    <Dialog open={!!finding} onOpenChange={onClose}>
      <DialogContent className="bg-bg-surface border-white/10 text-foreground max-w-3xl max-h-[90vh] overflow-y-auto font-sans text-xs">
        <DialogHeader>
          <div className="flex items-center justify-between border-b border-white/10 pb-3 mr-6">
            <div className="flex items-center gap-2.5">
              <Badge
                className={
                  finding.severity === "Critical"
                    ? "bg-red-950/70 text-red-400 border-red-500/50"
                    : finding.severity === "High"
                    ? "bg-amber-950/70 text-amber-400 border-amber-500/50"
                    : "bg-blue-950/70 text-blue-400 border-blue-500/50"
                }
              >
                {finding.severity}
              </Badge>
              <DialogTitle className="text-base font-bold">{finding.scan_name}</DialogTitle>
            </div>

            <Badge variant="outline" className="font-mono text-[10px] border-white/10">
              Framework: {finding.compliance_framework}
            </Badge>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* Resource & Metadata Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded-lg bg-bg-elevated/50 border border-white/5 font-mono text-[11px]">
            <div>
              <span className="text-muted-foreground">Provider:</span>
              <p className="font-bold text-foreground">{finding.provider}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Category:</span>
              <p className="font-bold text-brand-purple">{finding.category}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Est Fix Time:</span>
              <p className="font-bold text-emerald-400">{ai?.estimated_fix_time || "15 mins"}</p>
            </div>
            <div>
              <span className="text-muted-foreground">AI Risk Score:</span>
              <p className="font-bold text-red-400">{ai?.risk_score || 9.5}/10</p>
            </div>
          </div>

          {/* Finding Description */}
          <div className="p-3 rounded-lg bg-white/5 border border-white/5 space-y-1">
            <h4 className="font-bold text-foreground font-mono flex items-center gap-1.5">
              <FileText className="h-4 w-4 text-brand-purple" /> Finding Description & Location
            </h4>
            <p className="text-muted-foreground leading-relaxed">{finding.description}</p>
            <p className="text-emerald-400 font-mono text-[11px] pt-1">Resource: {finding.resource}</p>
          </div>

          {/* AI Attack Scenario & Business Impact */}
          {ai && (
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-red-950/20 border border-red-500/20 space-y-1">
                <h4 className="font-bold text-red-400 font-mono flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4" /> AI Simulated Attack Scenario
                </h4>
                <p className="text-muted-foreground leading-relaxed">{ai.attack_scenario}</p>
              </div>

              <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-500/20 space-y-1">
                <h4 className="font-bold text-amber-400 font-mono flex items-center gap-1.5">
                  <ShieldAlert className="h-4 w-4" /> Business & Regulatory Impact
                </h4>
                <p className="text-muted-foreground leading-relaxed">{ai.business_impact}</p>
              </div>
            </div>
          )}

          {/* Executable Remediation Steps */}
          <div className="space-y-2">
            <h4 className="font-bold text-foreground font-mono flex items-center gap-1.5">
              <Zap className="h-4 w-4 text-emerald-400" /> AI Automated Remediation Guide
            </h4>

            <div className="space-y-2">
              {(ai?.remediation_steps || [finding.recommendation]).map((step, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-black/80 border border-white/10 font-mono text-xs text-emerald-400 flex items-start justify-between gap-2"
                >
                  <code className="whitespace-pre-wrap break-all flex-1">$ {step}</code>
                  <button
                    onClick={() => handleCopy(step, idx)}
                    className="p-1 rounded bg-white/10 hover:bg-white/20 text-muted-foreground hover:text-white transition-colors shrink-0"
                  >
                    {copiedIdx === idx ? (
                      <Check className="h-3.5 w-3.5 text-emerald-400" />
                    ) : (
                      <Copy className="h-3.5 w-3.5" />
                    )}
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Compliance Violation Badge */}
          {ai?.compliance_impact && (
            <div className="p-3 rounded-lg bg-blue-950/20 border border-blue-500/20 flex items-center gap-2 font-mono text-[11px] text-blue-400">
              <Award className="h-4 w-4 shrink-0" />
              <span>{ai.compliance_impact}</span>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
