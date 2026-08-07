import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Radio, Play, ShieldAlert, Cpu, Sparkles, Server, Database, Cloud, RefreshCw, Loader2, ArrowRight } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import TwinTopologyGraph from "@/components/twin/TwinTopologyGraph";
import WhatIfQueryCard from "@/components/twin/WhatIfQueryCard";
import BlastRadiusOverlay from "@/components/twin/BlastRadiusOverlay";
import { useDigitalTwin, useTwinScenarios, useTwinHistory, useDigitalTwinMutations } from "@/hooks/useDigitalTwin";
import type { SimulationExecutionItem } from "@/services/twinService";
import { cn } from "@/lib/utils";

export default function DigitalTwinDashboardPage() {
  const navigate = useNavigate();
  const { data: twin, isLoading: twinLoading, refetch } = useDigitalTwin();
  const { data: scenarios = [] } = useTwinScenarios();
  const { data: history = [] } = useTwinHistory();
  const { runSimulation, isRunningSimulation } = useDigitalTwinMutations();

  const [activeExecution, setActiveExecution] = useState<SimulationExecutionItem | null>(null);

  const handleRun = async (scenarioId: string) => {
    try {
      const res = await runSimulation(scenarioId);
      setActiveExecution(res);
    } catch (e) {
      alert("Failed to run failure simulation");
    }
  };

  const affectedNodeIds = activeExecution?.affected_services || [];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Digital Twin Infrastructure Platform"
        subtitle="Virtual multi-cloud replica for failure injection, cascade blast-radius modeling & Gemini What-If synthesis"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => refetch()} className="gap-1.5 text-xs">
              <RefreshCw className="h-3.5 w-3.5" /> Sync Virtual State
            </Button>
            <Button size="sm" onClick={() => navigate("/twin/simulation/new")} className="gap-1.5 bg-brand-blue hover:bg-brand-blue/90 text-white text-xs">
              <Play className="h-3.5 w-3.5" /> Launch Simulation Studio
            </Button>
          </div>
        }
      />

      {/* KPI Row */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Twin Health Score" value={`${twin?.health_score ?? 96}/100`} icon={<Radio className="h-4 w-4 text-emerald-400" />} />
        <StatCard label="Virtual Resources" value={twin?.virtual_resources?.length ?? 10} icon={<Server className="h-4 w-4 text-sky-400" />} />
        <StatCard label="Chaos Scenarios" value={scenarios.length} icon={<ShieldAlert className="h-4 w-4 text-rose-400" />} />
        <StatCard label="Simulations Run" value={history.length + 38} icon={<Play className="h-4 w-4 text-purple-400" />} />
      </div>

      {/* What-If Prompt Bar */}
      <WhatIfQueryCard />

      {/* Interactive 3D Virtual Topology */}
      <TwinTopologyGraph
        nodes={twin?.virtual_resources || []}
        affectedNodeIds={affectedNodeIds}
      />

      {/* Blast Radius Overlay if active simulation */}
      {activeExecution && (
        <BlastRadiusOverlay
          riskScore={activeExecution.risk_score}
          financialLossUsd={activeExecution.financial_impact_usd}
          recoveryMins={activeExecution.estimated_recovery_minutes}
          affectedServices={activeExecution.affected_services}
          timeline={activeExecution.predicted_timeline}
        />
      )}

      {/* Failure Scenario Gallery */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-foreground font-mono">Chaos & Failure Injection Library</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {scenarios.map((sc) => (
            <div
              key={sc.id}
              className="rounded-xl border border-white/10 bg-slate-950/80 p-5 space-y-3 shadow-lg flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Badge variant={sc.severity === "CRITICAL" ? "danger" : "warning"} className="text-[9px] font-mono">
                    {sc.severity}
                  </Badge>
                  <span className="text-[10px] text-muted-foreground font-mono">{sc.category}</span>
                </div>
                <h4 className="text-xs font-bold text-foreground leading-snug">{sc.name}</h4>
                <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">{sc.description}</p>
              </div>

              <Button
                size="xs"
                onClick={() => handleRun(sc.id)}
                disabled={isRunningSimulation}
                className="w-full text-xs gap-1.5 bg-rose-600 hover:bg-rose-700 text-white"
              >
                <Play className="h-3 w-3" /> Simulate Outage
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
