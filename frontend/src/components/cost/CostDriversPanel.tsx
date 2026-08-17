import React from "react";
import { Compass, ArrowUpRight, ArrowDownRight, Layers, Globe, Server, AlertCircle, Sparkles } from "lucide-react";
import type { CostDriversResponse, PeriodComparisonResponse } from "@/types/cost";

interface CostDriversPanelProps {
  drivers: CostDriversResponse | null;
  comparison: PeriodComparisonResponse | null;
}

export default function CostDriversPanel({ drivers, comparison }: CostDriversPanelProps) {
  if (!drivers || !comparison) return null;

  return (
    <div className="space-y-6">
      {/* 1. Major Cost Drivers Grid */}
      <div className="p-5 rounded-xl border border-white/[0.08] bg-bg-surface space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Compass className="w-5 h-5 text-brand-blue" />
            <h3 className="text-sm font-semibold text-foreground">Major Cost Driver Analysis</h3>
          </div>
          <span className="text-xs text-muted-foreground font-mono">Data-Derived Cost Attribution</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Top Provider */}
          <div className="p-3.5 rounded-lg border border-white/[0.06] bg-slate-900/60 space-y-2">
            <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
              <span className="flex items-center gap-1.5"><Globe className="w-3.5 h-3.5 text-brand-blue" /> Top Provider</span>
              <span className="font-bold text-foreground">${drivers.top_provider.cost.toLocaleString()}</span>
            </div>
            <div className="text-sm font-bold text-foreground">{drivers.top_provider.name}</div>
            <p className="text-[11px] text-muted-foreground leading-relaxed">{drivers.top_provider.reason}</p>
          </div>

          {/* Top Service */}
          <div className="p-3.5 rounded-lg border border-white/[0.06] bg-slate-900/60 space-y-2">
            <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
              <span className="flex items-center gap-1.5"><Layers className="w-3.5 h-3.5 text-purple-400" /> Top Service</span>
              <span className="font-bold text-foreground">${drivers.top_service.cost.toLocaleString()}</span>
            </div>
            <div className="text-sm font-bold text-foreground">{drivers.top_service.name}</div>
            <p className="text-[11px] text-muted-foreground leading-relaxed">{drivers.top_service.reason}</p>
          </div>

          {/* Top Region */}
          <div className="p-3.5 rounded-lg border border-white/[0.06] bg-slate-900/60 space-y-2">
            <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
              <span className="flex items-center gap-1.5"><Globe className="w-3.5 h-3.5 text-emerald-400" /> Top Region</span>
              <span className="font-bold text-foreground">${drivers.top_region.cost.toLocaleString()}</span>
            </div>
            <div className="text-sm font-bold text-foreground">{drivers.top_region.name}</div>
            <p className="text-[11px] text-muted-foreground leading-relaxed">{drivers.top_region.reason}</p>
          </div>

          {/* Top Resource */}
          <div className="p-3.5 rounded-lg border border-white/[0.06] bg-slate-900/60 space-y-2">
            <div className="flex items-center justify-between text-xs text-muted-foreground font-mono">
              <span className="flex items-center gap-1.5"><Server className="w-3.5 h-3.5 text-amber-400" /> Top Resource</span>
              <span className="font-bold text-foreground">${drivers.top_resource.cost.toLocaleString()}</span>
            </div>
            <div className="text-sm font-bold text-foreground truncate">{drivers.top_resource.name}</div>
            <p className="text-[11px] text-muted-foreground leading-relaxed">{drivers.top_resource.reason}</p>
          </div>
        </div>
      </div>

      {/* 2. Period Comparison Widget */}
      <div className="p-5 rounded-xl border border-white/[0.08] bg-bg-surface space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-foreground">Current vs Previous Period Comparison</h3>
          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="text-muted-foreground">Change:</span>
            <span className={`font-bold flex items-center gap-0.5 ${comparison.total_spend_difference >= 0 ? "text-rose-400" : "text-emerald-400"}`}>
              {comparison.total_spend_difference >= 0 ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
              ${Math.abs(comparison.total_spend_difference).toLocaleString()} ({comparison.percentage_difference >= 0 ? "+" : ""}{comparison.percentage_difference}%)
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Provider Changes */}
          <div className="p-3.5 rounded-lg border border-white/[0.05] bg-slate-900/40 space-y-2">
            <span className="text-xs font-semibold text-muted-foreground">Provider Spend Changes</span>
            <div className="space-y-1.5">
              {comparison.provider_changes.map((p, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs font-mono">
                  <span className="text-foreground">{p.provider}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-muted-foreground">${p.previous_cost.toLocaleString()} → ${p.current_cost.toLocaleString()}</span>
                    <span className={`font-semibold ${p.difference >= 0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {p.difference >= 0 ? "+" : ""}${p.difference.toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Service Changes */}
          <div className="p-3.5 rounded-lg border border-white/[0.05] bg-slate-900/40 space-y-2">
            <span className="text-xs font-semibold text-muted-foreground">Service Spend Changes</span>
            <div className="space-y-1.5">
              {comparison.service_changes.slice(0, 4).map((s, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs font-mono">
                  <span className="text-foreground">{s.service}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-muted-foreground">${s.previous_cost.toLocaleString()} → ${s.current_cost.toLocaleString()}</span>
                    <span className={`font-semibold ${s.difference >= 0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {s.difference >= 0 ? "+" : ""}${s.difference.toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
