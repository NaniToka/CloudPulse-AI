import React from "react";
import { AlertCircle, AlertTriangle, Info, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";
import type { SeverityLevel } from "@/types/incident";

interface Props {
  severity: SeverityLevel | string;
  size?: "sm" | "md" | "lg";
  showIcon?: boolean;
  className?: string;
}

export function IncidentSeverityBadge({
  severity,
  size = "md",
  showIcon = true,
  className,
}: Props) {
  const norm = String(severity).toUpperCase();

  const isCritical = norm === "CRITICAL" || norm === "P0";
  const isHigh = norm === "HIGH" || norm === "P1";
  const isMedium = norm === "MEDIUM" || norm === "P2";

  const sizeClasses = {
    sm: "px-2 py-0.5 text-[11px]",
    md: "px-2.5 py-1 text-xs",
    lg: "px-3.5 py-1.5 text-sm font-semibold",
  }[size];

  let colorClasses = "bg-blue-500/10 text-blue-400 border-blue-500/30";
  let Icon = Info;
  let label = norm;

  if (isCritical) {
    colorClasses = "bg-red-500/15 text-red-400 border-red-500/40 shadow-red-500/10 shadow-sm";
    Icon = ShieldAlert;
    label = norm.startsWith("P") ? "P0 CRITICAL" : "CRITICAL";
  } else if (isHigh) {
    colorClasses = "bg-orange-500/15 text-orange-400 border-orange-500/40";
    Icon = AlertCircle;
    label = norm.startsWith("P") ? "P1 HIGH" : "HIGH";
  } else if (isMedium) {
    colorClasses = "bg-amber-500/15 text-amber-400 border-amber-500/40";
    Icon = AlertTriangle;
    label = norm.startsWith("P") ? "P2 MEDIUM" : "MEDIUM";
  } else {
    colorClasses = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    Icon = Info;
    label = norm.startsWith("P") ? "P3 LOW" : "LOW";
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md font-mono font-medium border uppercase tracking-wider backdrop-blur-sm transition-all",
        sizeClasses,
        colorClasses,
        className
      )}
    >
      {showIcon && (
        <span className="relative flex h-2 w-2">
          {isCritical && (
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
          )}
          <span
            className={cn(
              "relative inline-flex rounded-full h-2 w-2",
              isCritical
                ? "bg-red-500"
                : isHigh
                ? "bg-orange-500"
                : isMedium
                ? "bg-amber-500"
                : "bg-emerald-500"
            )}
          />
        </span>
      )}
      <span>{label}</span>
    </span>
  );
}
