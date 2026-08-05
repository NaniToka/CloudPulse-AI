/**
 * AIOpsAgentLoopCard Component — Renders the live 6-phase Autonomous Agent Loop.
 */

import React from "react";
import { Eye, Search, Brain, Map, Sparkles, CheckCircle2, Bot, Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { AIOpsAgentStatus } from "@/types/aiops";

interface AIOpsAgentLoopCardProps {
  status: AIOpsAgentStatus | undefined;
  onTriggerLoop?: () => void;
  isAnalyzing?: boolean;
}

const phases = [
  { name: "Observe", icon: Eye, desc: "Telemetry Collection" },
  { name: "Detect", icon: Search, desc: "Anomaly Isolation" },
  { name: "Analyze", icon: Brain, desc: "Root Cause Mining" },
  { name: "Plan", icon: Map, desc: "Remediation Strategy" },
  { name: "Recommend", icon: Sparkles, desc: "Actionable Insights" },
  { name: "Verify", icon: CheckCircle2, desc: "SLO Feedback Loop" },
];

export const AIOpsAgentLoopCard: React.FC<AIOpsAgentLoopCardProps> = ({
  status,
  onTriggerLoop,
  isAnalyzing,
}) => {
  const currentPhase = status?.current_phase || "Observe";

  return (
    <div className="p-5 rounded-2xl bg-bg-surface/90 border border-white/10 shadow-2xl space-y-4 font-sans text-xs">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-white/10 pb-3">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-brand-purple/20 border border-brand-purple/30 text-brand-purple flex items-center justify-center shadow-glow-blue">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-foreground">
                {status?.agent_name || "CloudPulse Autonomous Core Agent"}
              </h3>
              <Badge className="bg-emerald-950/60 text-emerald-400 border-emerald-500/40">
                {status?.status || "Autonomous"}
              </Badge>
            </div>
            <p className="text-[11px] text-muted-foreground font-mono mt-0.5 flex items-center gap-1.5">
              <Activity className="h-3 w-3 text-emerald-400 animate-pulse" />
              <span>
                Health: <strong className="text-emerald-400 font-bold">{status?.health_status || "Healthy"}</strong>
              </span>
              <span>•</span>
              <span>Last Observation: {status?.last_observation_at ? new Date(status.last_observation_at).toLocaleTimeString() : 'Just now'}</span>
            </p>
          </div>
        </div>

        <button
          onClick={onTriggerLoop}
          disabled={isAnalyzing}
          className="px-3 py-1.5 rounded-lg bg-brand-purple hover:bg-brand-purple/90 text-white font-bold text-xs flex items-center gap-2 transition-all shadow-md disabled:opacity-50"
        >
          <Sparkles className={`h-3.5 w-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
          {isAnalyzing ? "Executing Agent Loop..." : "Run Autonomous Cycle"}
        </button>
      </div>

      {/* 6-Phase Agent Loop Timeline */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
        {phases.map((p, idx) => {
          const IconComp = p.icon;
          const isActive = currentPhase.toLowerCase() === p.name.toLowerCase();
          return (
            <div
              key={p.name}
              className={`p-3 rounded-xl border transition-all duration-200 space-y-1 ${
                isActive
                  ? "bg-brand-purple/20 border-brand-purple shadow-glow-blue text-white"
                  : "bg-white/5 border-white/5 text-muted-foreground hover:bg-white/10"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-muted-foreground">Step {idx + 1}</span>
                <IconComp className={`h-4 w-4 ${isActive ? 'text-brand-purple' : 'text-muted-foreground'}`} />
              </div>
              <p className="text-xs font-bold text-foreground">{p.name}</p>
              <p className="text-[10px] text-muted-foreground line-clamp-1">{p.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
