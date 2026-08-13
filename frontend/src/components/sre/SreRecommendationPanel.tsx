import React from "react";
import { Sparkles, CheckCircle2, ArrowRight, ShieldCheck } from "lucide-react";
import type { SreRecommendationItem } from "@/types/sre";

interface SreRecommendationPanelProps {
  recommendations: SreRecommendationItem[];
  onTriggerAnalysis?: () => void;
  isAnalyzing?: boolean;
}

export default function SreRecommendationPanel({
  recommendations,
  onTriggerAnalysis,
  isAnalyzing,
}: SreRecommendationPanelProps) {
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

  return (
    <div className="p-5 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-4 font-mono">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-amber-400" />
          <h3 className="text-sm font-semibold text-foreground">Actionable SRE Remediation & Recommendations</h3>
        </div>

        {onTriggerAnalysis && (
          <button
            onClick={onTriggerAnalysis}
            disabled={isAnalyzing}
            className="px-4 py-2 rounded-lg bg-brand-blue text-white font-semibold text-xs flex items-center gap-2 hover:bg-brand-blue/80 transition-all disabled:opacity-50 shrink-0"
          >
            <Sparkles className="w-4 h-4" />
            {isAnalyzing ? "Analyzing Telemetry..." : "Run AI SRE Analysis"}
          </button>
        )}
      </div>

      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div key={rec.id} className="p-4 rounded-lg border border-white/5 bg-black/40 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getSeverityBadge(rec.severity)}
                <span className="font-semibold text-foreground text-xs">{rec.service} — {rec.category}</span>
              </div>
              <span className="text-[11px] text-muted-foreground">Confidence: {(rec.confidence * 100).toFixed(0)}%</span>
            </div>

            <p className="text-xs text-muted-foreground">{rec.reason}</p>
            <p className="text-xs text-slate-400">Evidence: <span className="text-foreground">{rec.evidence}</span></p>

            <div className="pt-1 flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-t border-white/5 text-xs text-brand-blue">
              <div className="flex items-center gap-1.5">
                <ArrowRight className="w-3.5 h-3.5 shrink-0" />
                <span>Action: <strong>{rec.recommended_action}</strong></span>
              </div>
              <span className="text-emerald-400 text-[11px] font-bold shrink-0">Impact: {rec.expected_impact}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
