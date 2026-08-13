import React from "react";
import { DollarSign, ShieldAlert, Activity, Box } from "lucide-react";

interface DomainGovernancePanelsProps {
  overview: any;
}

export default function DomainGovernancePanels({ overview }: DomainGovernancePanelsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
      {/* Security Governance */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Security Governance</span>
          <ShieldAlert className="w-4 h-4 text-rose-400" />
        </div>
        <p className="text-xl font-bold text-rose-400">76.5 / 100</p>
        <div className="text-[11px] text-muted-foreground space-y-0.5">
          <p>Public Storage: <strong className="text-foreground">2 Buckets</strong></p>
          <p>Unencrypted: <strong className="text-foreground">2 Disks</strong></p>
          <p>Missing Monitoring: <strong className="text-foreground">1 Node</strong></p>
        </div>
      </div>

      {/* Cost Governance */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">Cost Governance</span>
          <DollarSign className="w-4 h-4 text-amber-400" />
        </div>
        <p className="text-xl font-bold text-amber-400">82.0 / 100</p>
        <div className="text-[11px] text-muted-foreground space-y-0.5">
          <p>Missing Cost Tags: <strong className="text-foreground">3 Assets</strong></p>
          <p>Unapproved Regions: <strong className="text-foreground">1 EC2 Node</strong></p>
          <p>Unowned Expensive: <strong className="text-foreground">1 Asset</strong></p>
        </div>
      </div>

      {/* SRE Governance */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">SRE Governance</span>
          <Activity className="w-4 h-4 text-emerald-400" />
        </div>
        <p className="text-xl font-bold text-emerald-400">88.0 / 100</p>
        <div className="text-[11px] text-muted-foreground space-y-0.5">
          <p>Services w/o SLOs: <strong className="text-foreground">1 Service</strong></p>
          <p>Breached SLOs: <strong className="text-foreground">1 Service</strong></p>
          <p>High Burn Rate: <strong className="text-foreground">1 Service</strong></p>
        </div>
      </div>

      {/* Kubernetes Governance */}
      <div className="p-4 rounded-xl border border-white/10 bg-bg-elevated/40 backdrop-blur-md space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">K8s Governance</span>
          <Box className="w-4 h-4 text-indigo-400" />
        </div>
        <p className="text-xl font-bold text-indigo-400">72.0 / 100</p>
        <div className="text-[11px] text-muted-foreground space-y-0.5">
          <p>Privileged Workloads: <strong className="text-foreground">1 Deployment</strong></p>
          <p>Missing Limits: <strong className="text-foreground">1 Deployment</strong></p>
          <p>Root Execution: <strong className="text-foreground">1 Pod Context</strong></p>
        </div>
      </div>
    </div>
  );
}
