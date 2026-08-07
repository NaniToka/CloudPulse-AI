import React from "react";
import { ShieldAlert, DollarSign, Clock, AlertTriangle, CheckCircle2, ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface BlastRadiusOverlayProps {
  scenarioName?: string;
  riskScore: number;
  financialLossUsd: number;
  recoveryMins: number;
  affectedServices: string[];
  timeline?: Array<{ minute: string; event: string }>;
}

export default function BlastRadiusOverlay({
  scenarioName = "Simulated Failure Event",
  riskScore,
  financialLossUsd,
  recoveryMins,
  affectedServices,
  timeline = [],
}: BlastRadiusOverlayProps) {
  return (
    <div className="rounded-xl border border-rose-500/40 bg-rose-500/[0.04] p-5 shadow-2xl space-y-5 backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-rose-500/20 pb-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-rose-400" />
          <h4 className="text-sm font-bold text-foreground font-mono">{scenarioName} (Blast Radius)</h4>
        </div>
        <Badge variant="danger" className="text-[10px] font-mono">
          RISK SCORE: {riskScore}/100
        </Badge>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-3 text-xs">
        <div className="rounded-lg border border-white/10 bg-background/80 p-3 space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase font-mono">Revenue at Risk</span>
          <p className="text-base font-bold text-amber-400 font-mono">${financialLossUsd.toLocaleString()} / hr</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-background/80 p-3 space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase font-mono">Estimated MTTR</span>
          <p className="text-base font-bold text-sky-400 font-mono">{recoveryMins} Minutes</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-background/80 p-3 space-y-1">
          <span className="text-[10px] text-muted-foreground uppercase font-mono">Degraded Services</span>
          <p className="text-base font-bold text-rose-400 font-mono">{affectedServices.length} Nodes</p>
        </div>
      </div>

      {/* Affected services pills */}
      <div className="space-y-2 text-xs">
        <span className="text-[10px] text-muted-foreground font-mono uppercase font-bold">Failure Cascade Chain:</span>
        <div className="flex flex-wrap gap-1.5">
          {affectedServices.map((svc, idx) => (
            <span
              key={idx}
              className="rounded border border-rose-500/30 bg-rose-500/10 px-2 py-0.5 font-mono text-[10px] text-rose-300 font-semibold"
            >
              {svc}
            </span>
          ))}
        </div>
      </div>

      {/* Predicted Incident Timeline */}
      {timeline.length > 0 && (
        <div className="space-y-2 text-xs pt-1">
          <span className="text-[10px] text-muted-foreground font-mono uppercase font-bold">Cascade Progression Timeline:</span>
          <div className="space-y-1.5">
            {timeline.map((step, idx) => (
              <div key={idx} className="flex items-start gap-2 rounded border border-white/10 bg-background/60 p-2 text-[11px]">
                <span className="font-mono font-bold text-sky-400">{step.minute}</span>
                <span className="text-muted-foreground leading-snug">{step.event}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
