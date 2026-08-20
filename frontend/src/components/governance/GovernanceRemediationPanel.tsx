import React, { useState } from "react";
import { Sparkles, ArrowRight, Zap, Loader2, CheckCircle2, ShieldAlert, Cpu } from "lucide-react";
import type { GovernanceRemediationItem, GovernanceAnalyzeResponse } from "@/types/governance";
import { cn } from "@/lib/utils";

interface GovernanceRemediationPanelProps {
  remediations: GovernanceRemediationItem[];
  onTriggerAnalysis?: () => void;
  isAnalyzing?: boolean;
  aiAnalysis?: GovernanceAnalyzeResponse | null;
}

export default function GovernanceRemediationPanel({
  remediations,
  onTriggerAnalysis,
  isAnalyzing,
  aiAnalysis,
}: GovernanceRemediationPanelProps) {
  const [appliedPatches, setAppliedPatches] = useState<Record<string, boolean>>({});
  const [patchingId, setPatchingId] = useState<string | null>(null);

  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">CRITICAL</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">HIGH</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">MEDIUM</span>;
    }
  };

  const handleApplyPatch = (recId: string, resourceName: string) => {
    setPatchingId(recId);
    setTimeout(() => {
      setAppliedPatches((prev) => ({ ...prev, [recId]: true }));
      setPatchingId(null);
    }, 900);
  };

  return (
    <div className="p-6 rounded-2xl border border-slate-800/80 bg-slate-900/70 backdrop-blur-xl space-y-5 font-mono shadow-2xl relative overflow-hidden">
      {/* Top Accent Bar */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-amber-500 via-indigo-500 to-emerald-500" />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <h3 className="text-base font-bold text-white tracking-tight">Actionable Governance Remediation Plan</h3>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            AI-driven multi-cloud remediation recommendations and policy enforcement patches
          </p>
        </div>

        {onTriggerAnalysis && (
          <button
            onClick={onTriggerAnalysis}
            disabled={isAnalyzing}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs flex items-center gap-2 transition-all duration-200 disabled:opacity-50 shrink-0 shadow-lg shadow-indigo-600/25 border border-indigo-400/30"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-indigo-200" />
                <span>Analyzing Posture...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-amber-300" />
                <span>Run AI Governance Analysis</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Inline AI Analysis Summary Box if available */}
      {aiAnalysis && (
        <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-950/20 backdrop-blur-md space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <h4 className="font-bold text-white">Governance AI Executive Insight</h4>
            </div>
            <span className="text-[10px] text-amber-300 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
              Engine: {aiAnalysis.analysis_engine}
            </span>
          </div>

          <p className="text-slate-200 leading-relaxed font-sans text-xs">{aiAnalysis.executive_summary}</p>

          {aiAnalysis.critical_violations.length > 0 && (
            <div className="pt-2 border-t border-amber-500/20 space-y-1">
              <span className="font-bold text-rose-300">Critical Hazards Identified:</span>
              <ul className="list-disc list-inside space-y-0.5 text-slate-300 font-sans text-xs">
                {aiAnalysis.critical_violations.map((cv, idx) => (
                  <li key={idx}>{cv}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Remediation Cards List */}
      <div className="space-y-3">
        {remediations.map((rec) => {
          const isPatched = appliedPatches[rec.id];
          const isPatchingThis = patchingId === rec.id;

          return (
            <div
              key={rec.id}
              className={cn(
                "p-4 rounded-xl border transition-all duration-200 space-y-3 relative overflow-hidden",
                isPatched
                  ? "border-emerald-500/40 bg-emerald-950/10"
                  : "border-slate-800 bg-slate-950/80 hover:border-slate-700"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  {getSeverityBadge(rec.severity)}
                  <span className="font-bold text-white text-xs truncate" title={rec.resource}>
                    {rec.resource}
                  </span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    {rec.category}
                  </span>
                </div>
                <span className="text-[11px] text-slate-400 font-bold shrink-0">
                  Confidence: {(rec.confidence * 100).toFixed(0)}%
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed font-sans">Reason: {rec.reason}</p>

              <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-slate-800/80 text-xs">
                <div className="flex items-center gap-1.5 min-w-0 flex-1">
                  <ArrowRight className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  <span className="truncate">
                    Action: <strong className="text-indigo-300 font-semibold">{rec.recommended_action}</strong>
                  </span>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-slate-400 text-[11px]">Effort: {rec.estimated_effort}</span>
                  <span className="text-emerald-400 text-[11px] font-bold">Impact: {rec.risk_reduction}</span>

                  <button
                    onClick={() => handleApplyPatch(rec.id, rec.resource)}
                    disabled={isPatched || isPatchingThis}
                    className={cn(
                      "px-3 py-1 rounded-lg text-xs font-bold font-mono flex items-center gap-1.5 transition-all duration-200 border shadow-md",
                      isPatched
                        ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40 cursor-default"
                        : "bg-slate-900 hover:bg-slate-800 text-indigo-300 border-indigo-500/40 hover:border-indigo-500/60"
                    )}
                  >
                    {isPatchingThis ? (
                      <>
                        <Loader2 className="w-3 h-3 animate-spin text-indigo-400" />
                        <span>Patching...</span>
                      </>
                    ) : isPatched ? (
                      <>
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                        <span>Patch Applied</span>
                      </>
                    ) : (
                      <>
                        <Zap className="w-3 h-3 text-indigo-400" />
                        <span>Apply Patch</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
