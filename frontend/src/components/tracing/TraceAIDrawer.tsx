/**
 * Trace AI Analysis Drawer Component — Displays Gemini AI Trace Bottleneck Diagnostics.
 */

import React from "react";
import {
  X,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  Clock,
  TrendingUp,
  Zap,
  Activity,
  CheckCircle2,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { TraceAIAnalysis } from "@/types/trace";

interface TraceAIDrawerProps {
  analysis: TraceAIAnalysis | null;
  isOpen: boolean;
  onClose: () => void;
  isLoading: boolean;
}

export const TraceAIDrawer: React.FC<TraceAIDrawerProps> = ({
  analysis,
  isOpen,
  onClose,
  isLoading,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-xl bg-bg-surface border-l border-white/10 h-full overflow-y-auto p-6 space-y-6 flex flex-col justify-between text-xs">
        {/* Header */}
        <div className="space-y-3">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-brand-purple" />
              <span className="font-bold text-foreground">Gemini AI Trace Diagnostics</span>
            </div>

            <button
              onClick={onClose}
              className="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-white/10"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {isLoading ? (
            <div className="py-12 text-center text-muted-foreground animate-pulse font-mono">
              Running Gemini AI Trace Bottleneck Analysis...
            </div>
          ) : analysis ? (
            <div className="space-y-4">
              {/* Performance Score & Confidence */}
              <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-bg-elevated/40 border border-white/10">
                <div>
                  <span className="text-[10px] text-muted-foreground">Performance Score</span>
                  <div className="text-xl font-extrabold font-mono text-amber-400">
                    {analysis.performance_score.toFixed(1)} / 100
                  </div>
                </div>
                <div>
                  <span className="text-[10px] text-muted-foreground">AI Confidence</span>
                  <div className="text-xl font-extrabold font-mono text-emerald-400 flex items-center gap-1">
                    <ShieldCheck className="h-4 w-4" />
                    {Math.round(analysis.confidence_score * 100)}%
                  </div>
                </div>
              </div>

              {/* Slowest Service & Root Cause */}
              <Card className="p-4 bg-brand-purple/10 border border-brand-purple/20 space-y-2">
                <div className="flex items-center justify-between text-brand-purple font-semibold">
                  <span className="flex items-center gap-1.5">
                    <AlertTriangle className="h-4 w-4 text-amber-400" /> Bottleneck Detected
                  </span>
                  <Badge variant="warning">{analysis.slowest_service}</Badge>
                </div>
                <p className="text-foreground leading-relaxed text-xs">
                  {analysis.root_cause}
                </p>
              </Card>

              {/* Latency Breakdown per Service */}
              <Card className="p-4 bg-bg-elevated/30 border border-white/10 space-y-2">
                <div className="font-semibold text-foreground flex items-center gap-1.5">
                  <Clock className="h-4 w-4 text-brand-blue" /> Service Latency Breakdown
                </div>
                <div className="space-y-1.5 font-mono text-[11px]">
                  {Object.entries(analysis.latency_breakdown || {}).map(([service, lat]) => (
                    <div key={service} className="flex items-center justify-between p-1.5 rounded bg-black/20">
                      <span className="text-muted-foreground">{service}</span>
                      <span className="font-bold text-foreground">{lat} ms</span>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Optimization Suggestions */}
              <Card className="p-4 bg-bg-elevated/30 border border-white/10 space-y-2">
                <div className="font-semibold text-emerald-400 flex items-center gap-1.5">
                  <Zap className="h-4 w-4" /> Optimization Recommendations
                </div>
                <ul className="list-disc list-inside text-xs text-muted-foreground space-y-1 font-mono">
                  {analysis.optimization_suggestions.map((opt, i) => (
                    <li key={i} className="text-foreground">{opt}</li>
                  ))}
                </ul>
              </Card>

              {/* Scaling & Retry Suggestions */}
              <Card className="p-4 bg-bg-elevated/30 border border-white/10 space-y-2">
                <div className="font-semibold text-brand-purple flex items-center gap-1.5">
                  <TrendingUp className="h-4 w-4" /> Scaling & Resilience Policy
                </div>
                <div className="space-y-1 text-xs text-muted-foreground font-mono">
                  {analysis.scaling_suggestions.map((sc, i) => (
                    <div key={i} className="text-foreground">
                      • {sc}
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-white/10 text-right">
          <Button variant="outline" size="sm" onClick={onClose}>
            Close Analysis
          </Button>
        </div>
      </div>
    </div>
  );
};
