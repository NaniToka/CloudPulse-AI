/**
 * ComplianceScorecards Component — Displays compliance framework scorecards and control ratios.
 */

import React from "react";
import { ShieldCheck, CheckCircle, XCircle, Award } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import type { ComplianceReport } from "@/types/security";

interface ComplianceScorecardsProps {
  reports: ComplianceReport[];
}

export const ComplianceScorecards: React.FC<ComplianceScorecardsProps> = ({ reports }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 font-sans text-xs">
      {reports.map((report) => {
        const passPercent = Math.round((report.passed_controls / report.total_controls) * 100);
        return (
          <div
            key={report.id || report.framework}
            className="p-5 rounded-xl bg-bg-surface/90 border border-white/10 space-y-4 shadow-lg hover:border-brand-purple/40 transition-colors"
          >
            {/* Framework Title & Score */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2.5">
                <div className="h-8 w-8 rounded-lg bg-brand-purple/20 border border-brand-purple/30 text-brand-purple flex items-center justify-center">
                  <Award className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-foreground">{report.framework}</h4>
                  <span className="text-[10px] text-muted-foreground font-mono">
                    {report.passed_controls}/{report.total_controls} Controls Passed
                  </span>
                </div>
              </div>

              <Badge
                className={
                  report.overall_score >= 90
                    ? "bg-emerald-950/60 text-emerald-400 border-emerald-500/40"
                    : report.overall_score >= 80
                    ? "bg-blue-950/60 text-blue-400 border-blue-500/40"
                    : "bg-amber-950/60 text-amber-400 border-amber-500/40"
                }
              >
                {report.overall_score}% Score
              </Badge>
            </div>

            {/* Overall Progress Bar */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-[10px] font-mono text-muted-foreground">
                <span>Compliance Score</span>
                <span className="text-emerald-400 font-bold">{passPercent}% Compliance</span>
              </div>
              <Progress value={passPercent} className="h-2 bg-white/5" />
            </div>

            {/* Pass vs Fail Stats */}
            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5 font-mono text-[11px]">
              <div className="flex items-center gap-1.5 text-emerald-400 bg-emerald-950/20 p-2 rounded border border-emerald-500/20">
                <CheckCircle className="h-3.5 w-3.5" />
                <span>{report.passed_controls} Passed</span>
              </div>
              <div className="flex items-center gap-1.5 text-red-400 bg-red-950/20 p-2 rounded border border-red-500/20">
                <XCircle className="h-3.5 w-3.5" />
                <span>{report.failed_controls} Failed</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
