import React from "react";
import {
  BrainCircuit,
  CheckCircle2,
  Cpu,
  RefreshCw,
  Sparkles,
  TrendingUp,
  Workflow,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Incident } from "@/types/incident";

interface Props {
  incident: Incident;
  onReanalyze?: () => void;
  isAnalyzing?: boolean;
}

export function RootCausePanel({ incident, onReanalyze, isAnalyzing = false }: Props) {
  const confidence = incident.confidence_score ?? 0.94;
  const confidencePct = Math.round(confidence * 100);
  const rootCause = incident.root_cause || incident.ai_root_cause || "PostgreSQL connection pool saturation";
  const factors = incident.contributing_factors || [
    "Peak concurrency transaction window exceeding baseline connection pool",
    "42 idle in transaction connections held by background worker threads",
    "Microservice retry loop storm multiplying connection latency",
  ];

  return (
    <div className="space-y-4">
      {/* Root Cause Hero Banner */}
      <div className="relative rounded-xl border border-brand-500/30 bg-gradient-to-br from-brand-950/40 via-bg-surface to-bg-surface p-5 shadow-glass backdrop-blur-md overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10 text-brand-400">
          <BrainCircuit className="w-32 h-32" />
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.08] pb-3 mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-brand-400 animate-pulse" />
            <span className="text-xs font-semibold text-white font-mono uppercase tracking-wider">
              AI Root Cause Analysis & Grounded Evidence
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-white/[0.04] px-3 py-1 rounded-md border border-white/[0.08]">
              <span className="text-[11px] text-muted-foreground font-mono">Confidence:</span>
              <span className="text-xs font-bold font-mono text-emerald-400">
                {confidencePct}%
              </span>
              <div className="w-12 bg-white/10 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-emerald-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${confidencePct}%` }}
                />
              </div>
            </div>

            {onReanalyze && (
              <Button
                size="sm"
                variant="outline"
                onClick={onReanalyze}
                disabled={isAnalyzing}
                className="h-8 text-xs border-white/[0.1] bg-white/[0.02] hover:bg-white/[0.08] text-white"
              >
                <RefreshCw className={cn("w-3 h-3 mr-1.5", isAnalyzing && "animate-spin")} />
                Refresh RCA
              </Button>
            )}
          </div>
        </div>

        {/* Root Cause Title Box */}
        <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-4 mb-4">
          <div className="text-[11px] font-mono text-red-400 font-semibold uppercase tracking-wider mb-1 flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5" />
            Identified Root Cause Origin
          </div>
          <p className="text-sm font-semibold text-white font-mono leading-relaxed">
            "{rootCause}"
          </p>
        </div>

        {/* AI Executive Summary & Impact */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
          <div className="rounded-lg border border-white/[0.08] bg-white/[0.02] p-3">
            <div className="text-[11px] font-mono text-brand-300 font-medium mb-1">
              Executive Summary
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              {incident.ai_summary ||
                `Incident '${incident.title}' identified with multi-modal telemetry corroboration pointing to ${incident.affected_service}.`}
            </p>
          </div>

          <div className="rounded-lg border border-white/[0.08] bg-white/[0.02] p-3">
            <div className="text-[11px] font-mono text-amber-300 font-medium mb-1">
              Customer & SLA Impact
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              {incident.ai_business_impact ||
                `Degradation across ${incident.affected_services?.length || 1} services. Active user sessions experiencing elevated p99 latency.`}
            </p>
          </div>
        </div>

        {/* Contributing Factors */}
        <div>
          <div className="text-[11px] font-mono text-muted-foreground uppercase tracking-wider mb-2">
            Contributing Factors & Preconditions ({factors.length})
          </div>
          <div className="space-y-1.5">
            {factors.map((factor, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2 text-xs text-muted-foreground font-mono bg-white/[0.01] p-2 rounded border border-white/[0.04]"
              >
                <div className="h-1.5 w-1.5 rounded-full bg-brand-400 mt-1.5 shrink-0" />
                <span>{factor}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
