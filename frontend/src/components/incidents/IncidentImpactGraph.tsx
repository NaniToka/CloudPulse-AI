import React from "react";
import {
  AlertTriangle,
  ArrowRight,
  Database,
  DollarSign,
  Layers,
  Network,
  Server,
  ShieldAlert,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { BlastRadius } from "@/types/incident";

interface Props {
  blastRadius?: BlastRadius;
  rootService?: string;
  affectedServices?: string[];
}

export function IncidentImpactGraph({ blastRadius, rootService = "database-cluster", affectedServices = [] }: Props) {
  const root = blastRadius?.root_component || rootService;
  const services = blastRadius?.affected_services || affectedServices || [root];
  const downstream = services.filter((s) => s.toLowerCase() !== root.toLowerCase());

  const depth = blastRadius?.dependency_depth || Math.max(1, services.length);
  const financialRisk = blastRadius?.financial_risk_estimate || "$12,000 / hr";
  const userImpact = blastRadius?.estimated_user_impact || "HIGH";

  return (
    <div className="space-y-4">
      {/* Top Blast Radius Metric Pills */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="rounded-lg border border-white/[0.08] bg-white/[0.02] p-3 flex items-center gap-3">
          <div className="p-2 rounded-md bg-red-500/10 text-red-400">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] text-muted-foreground font-mono">User Impact</div>
            <div className="text-sm font-semibold text-white font-mono">{userImpact}</div>
          </div>
        </div>

        <div className="rounded-lg border border-white/[0.08] bg-white/[0.02] p-3 flex items-center gap-3">
          <div className="p-2 rounded-md bg-amber-500/10 text-amber-400">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] text-muted-foreground font-mono">Affected Services</div>
            <div className="text-sm font-semibold text-white font-mono">{services.length} Services</div>
          </div>
        </div>

        <div className="rounded-lg border border-white/[0.08] bg-white/[0.02] p-3 flex items-center gap-3">
          <div className="p-2 rounded-md bg-emerald-500/10 text-emerald-400">
            <DollarSign className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[11px] text-muted-foreground font-mono">Est. Financial Risk</div>
            <div className="text-sm font-semibold text-emerald-400 font-mono">{financialRisk}</div>
          </div>
        </div>
      </div>

      {/* Topology DAG Visualizer */}
      <div className="rounded-xl border border-white/[0.1] bg-bg-surface/60 p-5 shadow-glass backdrop-blur-md relative overflow-hidden">
        <div className="flex items-center justify-between border-b border-white/[0.06] pb-3 mb-4">
          <div className="flex items-center gap-2">
            <Network className="w-4 h-4 text-brand-400" />
            <span className="text-xs font-semibold text-white font-mono uppercase tracking-wider">
              Dependency Blast Radius & Propagation Tree
            </span>
          </div>
          <div className="flex items-center gap-2">
            <a
              href={`/dependencies?service=${encodeURIComponent(root)}`}
              className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-cyan-950/60 hover:bg-cyan-900/60 border border-cyan-500/40 text-cyan-300 text-[10px] font-mono transition-colors"
            >
              <span>Explore Topology</span>
              <ArrowRight className="w-3 h-3" />
            </a>
            <Badge variant="outline" className="text-[10px] font-mono border-white/20 text-muted-foreground">
              Depth: {depth} tiers
            </Badge>
          </div>
        </div>

        <div className="flex flex-col md:flex-row items-center justify-center gap-6 py-4">
          {/* Root Origin Node */}
          <div className="flex flex-col items-center">
            <div className="relative group">
              <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 opacity-75 blur-sm group-hover:opacity-100 transition duration-500 animate-pulse" />
              <div className="relative rounded-xl border-2 border-red-500 bg-bg-surface px-5 py-4 text-center shadow-xl min-w-[180px]">
                <div className="flex justify-center mb-1.5 text-red-400">
                  <Database className="w-6 h-6 animate-bounce" />
                </div>
                <div className="font-mono text-xs font-bold text-white tracking-wide">{root}</div>
                <Badge className="mt-2 text-[10px] uppercase font-mono bg-red-500/20 text-red-300 border-red-500/40">
                  Root Origin
                </Badge>
              </div>
            </div>
            <span className="mt-2 text-[10px] text-red-400 font-mono font-medium">
              Source Failure Origin
            </span>
          </div>

          {/* Propagation Arrows */}
          <div className="hidden md:flex flex-col items-center justify-center text-red-400/80">
            <span className="text-[10px] font-mono uppercase tracking-widest text-muted-foreground mb-1">
              Cascades To
            </span>
            <div className="flex items-center gap-1">
              <div className="h-[2px] w-8 bg-gradient-to-r from-red-500 to-amber-500" />
              <ArrowRight className="w-4 h-4 text-amber-400 animate-pulse" />
            </div>
          </div>

          {/* Downstream Impact Grid */}
          <div className="flex-1 w-full">
            <div className="text-[11px] font-mono text-muted-foreground mb-2 flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Downstream Degraded Services ({downstream.length || 1})</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {downstream.length > 0 ? (
                downstream.map((svc, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between rounded-lg border border-amber-500/30 bg-amber-500/5 px-3 py-2 text-xs hover:border-amber-500/60 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <Server className="w-3.5 h-3.5 text-amber-400" />
                      <span className="font-mono text-white font-medium">{svc}</span>
                    </div>
                    <Badge variant="outline" className="text-[9px] font-mono bg-amber-500/10 text-amber-400 border-amber-500/30">
                      Degraded
                    </Badge>
                  </div>
                ))
              ) : (
                <div className="col-span-2 rounded-lg border border-white/[0.08] bg-white/[0.02] p-3 text-center text-xs text-muted-foreground font-mono">
                  No downstream cascading propagation detected. Incident isolated to {root}.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
