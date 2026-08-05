/**
 * Prediction Explanation Drawer Component
 * Displays complete Gemini AI predictive diagnostics.
 */

import React from "react";
import {
  X,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  Activity,
  CheckCircle2,
  Clock,
  TrendingUp,
  Zap,
  Globe,
  Check,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { Prediction } from "@/types/prediction";

interface PredictionDrawerProps {
  prediction: Prediction | null;
  isOpen: boolean;
  onClose: () => void;
  onMitigate: (id: string) => Promise<void>;
  isMitigating: boolean;
}

export const PredictionDrawer: React.FC<PredictionDrawerProps> = ({
  prediction,
  isOpen,
  onClose,
  onMitigate,
  isMitigating,
}) => {
  if (!isOpen || !prediction) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-xl bg-bg-surface border-l border-white/10 h-full overflow-y-auto p-6 space-y-6 flex flex-col justify-between text-xs">
        {/* Header */}
        <div className="space-y-3">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <div className="flex items-center gap-2">
              <Badge variant={prediction.risk_level === "Critical" ? "critical" : "warning"}>
                {prediction.risk_level} Risk
              </Badge>
              <span className="font-mono text-muted-foreground">{prediction.service}</span>
              <span className="text-muted-foreground">•</span>
              <span className="text-muted-foreground flex items-center gap-1">
                <Globe className="h-3 w-3" /> {prediction.region}
              </span>
            </div>

            <button
              onClick={onClose}
              className="p-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-white/10 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div>
            <h2 className="text-base font-bold text-foreground leading-tight">
              {prediction.title}
            </h2>
            <p className="text-[11px] text-muted-foreground mt-1">
              Expected Failure:{" "}
              <span className="font-mono text-red-400 font-bold">
                {prediction.expected_failure_time
                  ? new Date(prediction.expected_failure_time).toLocaleString()
                  : "Within 30 minutes"}
              </span>
            </p>
          </div>

          {/* Probability & Confidence Meter */}
          <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-bg-elevated/40 border border-white/10">
            <div>
              <span className="text-[10px] text-muted-foreground">Failure Probability</span>
              <div className="text-lg font-extrabold text-red-400 font-mono">
                {prediction.failure_probability.toFixed(1)}%
              </div>
            </div>
            <div>
              <span className="text-[10px] text-muted-foreground">AI Confidence Score</span>
              <div className="text-lg font-extrabold text-emerald-400 font-mono flex items-center gap-1">
                <ShieldCheck className="h-4 w-4" />
                {Math.round(prediction.confidence_score * 100)}%
              </div>
            </div>
          </div>
        </div>

        {/* AI Diagnostics Sections */}
        <div className="space-y-4 flex-1 my-4">
          {/* Why Prediction was Made */}
          <Card className="p-4 bg-brand-purple/10 border border-brand-purple/20 space-y-2">
            <div className="flex items-center gap-2 text-brand-purple font-semibold text-xs">
              <Sparkles className="h-4 w-4" /> Why This Prediction Was Made
            </div>
            <p className="text-foreground leading-relaxed text-xs">
              {prediction.ai_explanation || "Continuous metric anomaly pattern detected across CPU and memory bounds."}
            </p>
          </Card>

          {/* Metrics Causing Concern */}
          <Card className="p-4 bg-bg-elevated/30 border border-white/10 space-y-3">
            <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs">
              <Activity className="h-4 w-4" /> Telemetry Metrics of Concern
            </div>
            <div className="space-y-2">
              {prediction.ai_metrics_of_concern && prediction.ai_metrics_of_concern.length > 0 ? (
                prediction.ai_metrics_of_concern.map((m, idx) => (
                  <div key={idx} className="p-2.5 rounded bg-black/30 border border-white/5 space-y-1 font-mono text-[11px]">
                    <div className="flex items-center justify-between font-bold text-foreground">
                      <span>{m.name}</span>
                      <span className="text-amber-400">{m.current_value} (Threshold: {m.threshold})</span>
                    </div>
                    <div className="text-muted-foreground text-[10px] flex items-center justify-between">
                      <span>Trend: {m.anomaly_trend}</span>
                      <span className="text-red-400">{m.risk_impact}</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground text-xs">CPU and Memory heap saturation thresholds breached.</p>
              )}
            </div>
          </Card>

          {/* Historical Pattern Comparison & Possible Impact */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Card className="p-3 bg-bg-elevated/30 border border-white/10 space-y-1">
              <div className="font-semibold text-foreground text-xs flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5 text-brand-blue" /> Historical Pattern Match
              </div>
              <p className="text-muted-foreground text-xs leading-relaxed">
                {prediction.ai_historical_pattern_comparison || "Matches prior cache exhaustion incident trajectory."}
              </p>
            </Card>

            <Card className="p-3 bg-bg-elevated/30 border border-white/10 space-y-1">
              <div className="font-semibold text-foreground text-xs flex items-center gap-1.5">
                <TrendingUp className="h-3.5 w-3.5 text-red-400" /> Forecasted Business Impact
              </div>
              <p className="text-muted-foreground text-xs leading-relaxed">
                {prediction.ai_possible_impact || "Potential 100% auth login outage across active user sessions."}
              </p>
            </Card>
          </div>

          {/* Immediate Preventive Actions */}
          <Card className="p-4 bg-bg-elevated/30 border border-white/10 space-y-2">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
              <Zap className="h-4 w-4" /> Immediate Preventive Actions
            </div>
            <ul className="list-disc list-inside text-xs text-muted-foreground space-y-1.5 font-mono bg-black/20 p-3 rounded border border-white/5">
              {(prediction.ai_immediate_preventive_actions || prediction.recommended_preventive_actions || []).map((act, i) => (
                <li key={i} className="text-foreground">{act}</li>
              ))}
            </ul>
          </Card>
        </div>

        {/* Footer Action Buttons */}
        <div className="pt-4 border-t border-white/10 flex items-center justify-between gap-3">
          <Button variant="outline" size="sm" onClick={onClose}>
            Close Drawer
          </Button>

          {prediction.status === "Active" && (
            <Button
              size="sm"
              disabled={isMitigating}
              onClick={() => onMitigate(prediction.id)}
              className="bg-emerald-600 hover:bg-emerald-500 text-white gap-1.5"
            >
              <Check className="h-3.5 w-3.5" />
              {isMitigating ? "Mitigating..." : "Apply Auto-Mitigation"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
