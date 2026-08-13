import React, { useEffect, useState } from 'react';
import {
  ActionDefinition,
  AutonomousOverview,
  AutonomyPolicy,
  RemediationAuditLog,
  RemediationExecution,
  RemediationPlan,
  SimulationResult,
} from '../../types/autonomous';
import { autonomousService } from '../../services/autonomousService';
import { ModeBanner } from '../../components/autonomous/ModeBanner';
import { AutonomyLevelControl } from '../../components/autonomous/AutonomyLevelControl';
import { RemediationPipelineFlow } from '../../components/autonomous/RemediationPipelineFlow';
import { ActionCatalogTable } from '../../components/autonomous/ActionCatalogTable';
import { RemediationPlansList } from '../../components/autonomous/RemediationPlansList';
import { ExecutionQueueStatus } from '../../components/autonomous/ExecutionQueueStatus';
import { PolicyGuardrailsPanel } from '../../components/autonomous/PolicyGuardrailsPanel';
import { AuditLogTable } from '../../components/autonomous/AuditLogTable';
import { SimulateActionModal } from '../../components/autonomous/SimulateActionModal';
import { Cpu, RefreshCw, ShieldAlert, Play, Activity } from 'lucide-react';

export const AutonomousOperationsPage: React.FC = () => {
  const [overview, setOverview] = useState<AutonomousOverview | null>(null);
  const [policy, setPolicy] = useState<AutonomyPolicy | null>(null);
  const [actions, setActions] = useState<ActionDefinition[]>([]);
  const [plans, setPlans] = useState<RemediationPlan[]>([]);
  const [queue, setQueue] = useState<RemediationExecution[]>([]);
  const [auditLogs, setAuditLogs] = useState<RemediationAuditLog[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [simulatingAction, setSimulatingAction] = useState<ActionDefinition | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [ovData, polData, actData, planData, qData, logData] = await Promise.all([
        autonomousService.getOverview(),
        autonomousService.getConfig(),
        autonomousService.listActions(),
        autonomousService.listPlans(),
        autonomousService.getQueue(),
        autonomousService.getAuditLogs(),
      ]);

      setOverview(ovData);
      setPolicy(polData);
      setActions(actData);
      setPlans(planData);
      setQueue(qData);
      setAuditLogs(logData);
    } catch (err) {
      console.error('Failed to load Autonomous Operations data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleLevelChange = async (newLevel: number) => {
    if (!policy) return;
    try {
      const updated = await autonomousService.updateConfig({ autonomy_level: newLevel });
      setPolicy(updated);
      fetchData();
    } catch (err) {
      console.error('Failed to update autonomy level:', err);
    }
  };

  const handlePolicyUpdate = async (updates: Partial<AutonomyPolicy>) => {
    try {
      const updated = await autonomousService.updateConfig(updates);
      setPolicy(updated);
      fetchData();
    } catch (err) {
      console.error('Failed to update policy config:', err);
    }
  };

  const handleApprovePlan = async (planId: string) => {
    try {
      await autonomousService.approvePlan(planId);
      fetchData();
    } catch (err) {
      console.error('Failed to approve plan:', err);
    }
  };

  const handleExecutePlan = async (planId: string) => {
    try {
      await autonomousService.executePlan(planId, 'SIMULATED');
      fetchData();
    } catch (err) {
      console.error('Failed to execute plan:', err);
    }
  };

  const handleRollbackPlan = async (planId: string) => {
    try {
      await autonomousService.rollbackPlan(planId);
      fetchData();
    } catch (err) {
      console.error('Failed to rollback plan:', err);
    }
  };

  const handleSimulateSubmit = async (payload: {
    action_type: string;
    affected_resource: string;
    provider: string;
    environment: string;
    execution_mode: string;
  }): Promise<SimulationResult> => {
    const res = await autonomousService.simulateAction(payload);
    fetchData();
    return res;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400">
            <Cpu className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Autonomous Cloud Operations & Self-Healing Center
            </h1>
            <p className="text-xs text-slate-400">
              Controlled multi-cloud self-healing remediation pipeline across AWS, Azure, GCP, and Kubernetes.
            </p>
          </div>
        </div>

        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium border border-slate-700 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Mode Banner */}
      <ModeBanner
        modeIndicator={overview?.mode_indicator || 'DEMO / SIMULATION MODE'}
        autonomyLevel={policy?.autonomy_level ?? 1}
        executionMode={policy?.default_execution_mode || 'SIMULATED'}
      />

      {/* Autonomy Level Controls (0-4) */}
      <AutonomyLevelControl
        currentLevel={policy?.autonomy_level ?? 1}
        onLevelChange={handleLevelChange}
      />

      {/* Pipeline Lifecycle Flow */}
      <RemediationPipelineFlow activeStep={3} />

      {/* Two Column Section: Queue & Policy Guardrails */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ExecutionQueueStatus queue={queue} />
        <PolicyGuardrailsPanel policy={policy} onUpdate={handlePolicyUpdate} />
      </div>

      {/* Action Catalog Table */}
      <ActionCatalogTable
        actions={actions}
        onSimulate={(action) => setSimulatingAction(action)}
      />

      {/* Active & Historical Plans List */}
      <RemediationPlansList
        plans={plans}
        onApprove={handleApprovePlan}
        onExecute={handleExecutePlan}
        onRollback={handleRollbackPlan}
      />

      {/* Audit Trail Viewer */}
      <AuditLogTable logs={auditLogs} />

      {/* Simulation Modal */}
      <SimulateActionModal
        action={simulatingAction}
        onClose={() => setSimulatingAction(null)}
        onSimulateSubmit={handleSimulateSubmit}
      />
    </div>
  );
};
