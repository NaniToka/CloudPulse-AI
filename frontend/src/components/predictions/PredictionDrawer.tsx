/**
 * Prediction Explanation Drawer Component
 * Displays complete Gemini AI / SRE predictive diagnostics and lifecycle actions.
 */

import React, { useState } from "react";
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
  ShieldAlert,
  Flame,
  ExternalLink,
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
  onCreateIncident?: (id: string) => Promise<void>;
  onMarkFalsePositive?: (id: string) => Promise<void>;
  isMitigating: boolean;
}

export const PredictionDrawer: React.FC<PredictionDrawerProps> = ({
  prediction,
  isOpen,
  onClose,
  onMitigate,
  onCreateIncident,
  onMarkFalsePositive,
  isMitigating,
}) => {
  const [isEscalating, setIsEscalating] = useState(false);

  if (!isOpen || !prediction) return null;

  const handleCreateIncident = async () => {
    if (!onCreateIncident) return;
    try {
      setIsEscalating(true);
      await onCreateIncident(prediction.id);
    } finally {
      setIsEscalating(false);
    }
  };

  const isGemini = prediction.analysis_engine === "gemini";
  const estMins = prediction.estimated_time_to_threshold_minutes || 28;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-xl bg-slate-900 border-l border-slate-800 h-full overflow-y-auto p-6 space-y-6 flex flex-col justify-between text-xs text-slate-200">
        {/* Header */}
        <div className="space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2">
              <Badge variant={prediction.risk_level === "Critical" ? "critical" : "warning"}>
                {prediction.risk_level} Risk
              </Badge>
              <span className="font-mono text-slate-300 font-semibold">{prediction.service}</span>
              <span className="text-slate-500">•</span>
              <span className="text-slate-400 flex items-center gap-1">
                <Globe className="h-3 w-3" /> {prediction.region}
              </span>
              <Badge variant="outline" className="border-indigo-500/30 bg-indigo-500/10 text-indigo-300 ml-1 text-[10px]">
                {isGemini ? "Grounded Gemini" : "Deterministic Engine"}
              </Badge>
            </div>

            <button
              onClick={onClose}
              className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div>
            <h2 className="text-base font-bold text-white leading-tight">
              {prediction.title}
            </h2>
            <div className="flex items-center gap-4 mt-2">
              <p className="text-[11px] text-slate-400">
                Projected Breach:{" "}
                <span className="font-mono text-rose-400 font-bold">
                  ~{estMins.toFixed(0)} minutes
                </span>
              </p>
              <p className="text-[11px] text-slate-400">
                Trend:{" "}
                <span className="font-mono text-amber-400 font-bold uppercase">
                  {prediction.trend_direction || "INCREASING"}
                </span>
              </p>
            </div>
          </div>

          {/* Probability & Confidence Meter */}
          <div className="grid grid-cols-3 gap-3 p-3 rounded-lg bg-slate-950/60 border border-slate-800">
            <div>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider">Failure Probability</span>
              <div className="text-lg font-extrabold text-rose-400 font-mono">
                {prediction.failure_probability.toFixed(1)}%
              </div>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider">Confidence Score</span>
              <div className="text-lg font-extrabold text-emerald-400 font-mono flex items-center gap-1">
                <ShieldCheck className="h-4 w-4" />
                {Math.round(prediction.confidence_score * 100)}%
              </div>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider">Lifecycle Status</span>
              <div className="text-sm font-bold text-slate-200 mt-1 uppercase font-mono">
                {prediction.status}
              </div>
            </div>
          </div>
        </div>

        {/* AI Diagnostics Sections */}
        <div className="space-y-4 flex-1 my-4">
          {/* Why Prediction was Made */}
          <Card className="p-4 bg-indigo-950/20 border border-indigo-500/30 space-y-2">
            <div className="flex items-center gap-2 text-indigo-300 font-semibold text-xs">
              <Sparkles className="h-4 w-4 text-indigo-400" /> Root Cause & Diagnostic Reasoning
            </div>
            <p className="text-slate-200 leading-relaxed text-xs">
              {prediction.ai_explanation || prediction.likely_root_cause || "Accelerating resource saturation detected."}
            </p>
          </Card>

          {/* Metrics Causing Concern */}
          <Card className="p-4 bg-slate-950/40 border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs">
              <Activity className="h-4 w-4" /> Correlated Telemetry Metrics of Concern
            </div>
            <div className="space-y-2">
              {prediction.ai_metrics_of_concern && prediction.ai_metrics_of_concern.length > 0 ? (
                prediction.ai_metrics_of_concern.map((m, idx) => (
                  <div key={idx} className="p-2.5 rounded bg-slate-900 border border-slate-800 space-y-1 font-mono text-[11px]">
                    <div className="flex items-center justify-between font-bold text-slate-200">
                      <span>{m.name}</span>
                      <span className="text-amber-400">{m.current_value} (Threshold: {m.threshold})</span>
                    </div>
                    <div className="text-slate-400 text-[10px] flex items-center justify-between">
                      <span>Trend: {m.anomaly_trend}</span>
                      <span className="text-rose-400">{m.risk_impact}</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-slate-400 text-xs">CPU and Memory heap saturation thresholds breached.</p>
              )}
            </div>
          </Card>

          {/* Historical Pattern Comparison & Possible Impact */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Card className="p-3 bg-slate-950/40 border border-slate-800 space-y-1">
              <div className="font-semibold text-slate-200 text-xs flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5 text-indigo-400" /> Historical Pattern Match
              </div>
              <p className="text-slate-400 text-xs leading-relaxed">
                {prediction.ai_historical_pattern_comparison || "Matches prior cache exhaustion incident trajectory."}
              </p>
            </Card>

            <Card className="p-3 bg-slate-950/40 border border-slate-800 space-y-1">
              <div className="font-semibold text-slate-200 text-xs flex items-center gap-1.5">
                <TrendingUp className="h-3.5 w-3.5 text-rose-400" /> Forecasted Impact
              </div>
              <p className="text-slate-400 text-xs leading-relaxed">
                {prediction.ai_possible_impact || "Potential downstream latency cascade across dependent microservices."}
              </p>
            </Card>
          </div>

          {/* Immediate Preventive Actions */}
          <Card className="p-4 bg-slate-950/40 border border-slate-800 space-y-2">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
              <Zap className="h-4 w-4" /> Recommended Mitigation Actions
            </div>
            <ul className="list-disc list-inside text-xs text-slate-300 space-y-1.5 font-mono bg-slate-900/60 p-3 rounded border border-slate-800">
              {(prediction.ai_immediate_preventive_actions || prediction.recommended_preventive_actions || []).map((act, i) => (
                <li key={i} className="text-slate-200">{act}</li>
              ))}
            </ul>
          </Card>
        </div>

        {/* Footer Action Buttons */}
        <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={onClose} className="border-slate-700 text-slate-300 hover:bg-slate-800">
              Close
            </Button>
            {onMarkFalsePositive && prediction.status === "Active" && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onMarkFalsePositive(prediction.id)}
                className="text-slate-400 hover:text-rose-400 text-xs"
              >
                Mark False Positive
              </Button>
            )}
          </div>

          <div className="flex items-center gap-2">
            {onCreateIncident && prediction.status === "Active" && (
              <Button
                size="sm"
                disabled={isEscalating}
                onClick={handleCreateIncident}
                className="bg-rose-600 hover:bg-rose-500 text-white gap-1.5 font-semibold shadow-lg shadow-rose-600/20"
              >
                <Flame className="h-3.5 w-3.5" />
                {isEscalating ? "Declaring..." : "Declare Incident"}
              </Button>
            )}

            {prediction.status === "Active" && (
              <Button
                size="sm"
                disabled={isMitigating}
                onClick={() => onMitigate(prediction.id)}
                className="bg-emerald-600 hover:bg-emerald-500 text-white gap-1.5 font-semibold"
              >
                <Check className="h-3.5 w-3.5" />
                {isMitigating ? "Mitigating..." : "Auto-Mitigate"}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
