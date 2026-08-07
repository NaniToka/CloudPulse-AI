import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Play, ShieldAlert, Cpu, Database, Server, RefreshCw, Loader2, Sparkles, CheckCircle2 } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import BlastRadiusOverlay from "@/components/twin/BlastRadiusOverlay";
import { useTwinScenarios, useDigitalTwinMutations } from "@/hooks/useDigitalTwin";
import type { SimulationExecutionItem } from "@/services/twinService";

export default function SimulationStudioPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: scenarios = [] } = useTwinScenarios();
  const { runSimulation, isRunningSimulation } = useDigitalTwinMutations();

  const [selectedScenarioId, setSelectedScenarioId] = useState<string>(scenarios[0]?.id || "");
  const [executionResult, setExecutionResult] = useState<SimulationExecutionItem | null>(null);

  const activeScenario = scenarios.find((s) => s.id === (selectedScenarioId || scenarios[0]?.id)) || scenarios[0];

  const handleExecute = async () => {
    if (!activeScenario) return;
    try {
      const res = await runSimulation(activeScenario.id);
      setExecutionResult(res);
    } catch (e) {
      alert("Failed to run failure simulation");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="sm" onClick={() => navigate("/twin")} className="gap-1 text-xs">
          <ArrowLeft className="h-4 w-4" /> Back to Digital Twin
        </Button>
        <Button
          size="sm"
          onClick={handleExecute}
          disabled={isRunningSimulation}
          className="gap-1.5 bg-rose-600 hover:bg-rose-700 text-white text-xs"
        >
          {isRunningSimulation ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
          Inject Chaos & Compute Blast Radius
        </Button>
      </div>

      <PageHeader
        title="Simulation Studio & Chaos Injection"
        subtitle="Configure failure parameters, simulate network partitions, and evaluate cascade blast radius in isolation"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scenario Config Panel */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-sm font-semibold text-foreground">Scenario Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div>
              <label className="text-[10px] text-muted-foreground uppercase font-mono">Select Target Scenario</label>
              <select
                value={selectedScenarioId || activeScenario?.id}
                onChange={(e) => setSelectedScenarioId(e.target.value)}
                className="mt-1 w-full rounded-md border border-white/10 bg-background px-2 py-2 text-xs text-foreground font-mono"
              >
                {scenarios.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.category})
                  </option>
                ))}
              </select>
            </div>

            {activeScenario && (
              <div className="space-y-3 pt-2">
                <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 space-y-1">
                  <span className="text-[10px] text-muted-foreground uppercase font-mono">Target Virtual Artifact</span>
                  <p className="font-mono font-bold text-foreground">{activeScenario.target_resource}</p>
                </div>

                <div className="rounded-lg border border-white/10 bg-white/[0.02] p-3 space-y-1">
                  <span className="text-[10px] text-muted-foreground uppercase font-mono">Failure Mechanism</span>
                  <p className="font-mono text-rose-400 font-semibold">{activeScenario.failure_type}</p>
                </div>

                <p className="text-muted-foreground leading-relaxed pt-1">{activeScenario.description}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Blast Radius & Recovery Output */}
        <div className="lg:col-span-2 space-y-6">
          {executionResult ? (
            <div className="space-y-6">
              <BlastRadiusOverlay
                scenarioName={activeScenario?.name}
                riskScore={executionResult.risk_score}
                financialLossUsd={executionResult.financial_impact_usd}
                recoveryMins={executionResult.estimated_recovery_minutes}
                affectedServices={executionResult.affected_services}
                timeline={executionResult.predicted_timeline}
              />

              {/* Recovery Playbook */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-emerald-400" />
                    Gemini AI Automated Recovery Playbook
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-xs">
                  {executionResult.recovery_steps?.map((step, idx) => (
                    <div key={idx} className="flex items-center gap-2 rounded-lg border border-emerald-500/20 bg-emerald-500/[0.03] p-3">
                      <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                      <span className="text-foreground font-mono">{step}</span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="flex h-72 items-center justify-center rounded-xl border border-white/10 bg-slate-950 p-8 text-center text-xs text-muted-foreground">
              Click "Inject Chaos & Compute Blast Radius" above to run physics simulation and observe cascade failure propagation.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
