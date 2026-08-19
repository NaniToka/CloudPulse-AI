import { HelpCircle } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

export type MetricType =
  | "anomaly_score"
  | "confidence"
  | "health_score"
  | "projected_cost"
  | "potential_savings"
  | "risk_score"
  | "slo_error_budget"
  | "blast_radius";

const METRIC_HELP_TEXT: Record<MetricType, { label: string; explanation: string }> = {
  anomaly_score: {
    label: "Anomaly Score",
    explanation: "Statistical deviation score (0-100%) indicating how significantly recent telemetry deviates from historical baseline behavior.",
  },
  confidence: {
    label: "AI Confidence",
    explanation: "Google Gemini / SRE engine probability rating representing confidence in root cause diagnosis and recommended runbook remediation.",
  },
  health_score: {
    label: "Health Score",
    explanation: "Composite infrastructure availability metric calculated across CPU, memory, disk I/O, error rates, and active incident severity.",
  },
  projected_cost: {
    label: "Projected Monthly Spend",
    explanation: "Estimated end-of-month cloud spend extrapolated from current daily usage trends and active resource provisioning.",
  },
  potential_savings: {
    label: "Potential Savings",
    explanation: "Calculated monthly cost savings realizable by deleting orphaned volumes, releasing idle Elastic IPs, and right-sizing underutilized VMs.",
  },
  risk_score: {
    label: "Security Risk Score",
    explanation: "Normalized CSPM vulnerability index (0-100) based on open security groups, unpatched OS CVEs, and compliance framework drift.",
  },
  slo_error_budget: {
    label: "SLO Error Budget",
    explanation: "Remaining percentage of allowed SLA failure quota before triggering automated deployment freezes or incident escalations.",
  },
  blast_radius: {
    label: "Topological Blast Radius",
    explanation: "Calculated proportion of downstream microservices and customer requests impacted if the selected node or cluster fails.",
  },
};

interface MetricHelpTooltipProps {
  type?: MetricType;
  customLabel?: string;
  customText?: string;
  className?: string;
  iconClassName?: string;
}

export default function MetricHelpTooltip({
  type,
  customLabel,
  customText,
  className,
  iconClassName,
}: MetricHelpTooltipProps) {
  const metricInfo = type ? METRIC_HELP_TEXT[type] : null;
  const label = customLabel || metricInfo?.label || "Metric Info";
  const text = customText || metricInfo?.explanation || "";

  if (!text) return null;

  return (
    <TooltipProvider>
      <Tooltip delayDuration={150}>
        <TooltipTrigger asChild>
          <span className={cn("inline-flex items-center gap-1 cursor-help select-none", className)}>
            <HelpCircle className={cn("h-3.5 w-3.5 text-muted-foreground/70 hover:text-brand-purple transition-colors", iconClassName)} />
          </span>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-xs text-xs space-y-1 bg-bg-elevated border-white/10 shadow-xl p-3">
          <p className="font-semibold text-foreground">{label}</p>
          <p className="text-muted-foreground text-[11px] leading-relaxed">{text}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
