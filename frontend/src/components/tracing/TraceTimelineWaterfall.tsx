/**
 * Trace Timeline Waterfall Component — Interactive OpenTelemetry Span Tree Visualization.
 */

import React, { useState } from "react";
import {
  ChevronRight,
  ChevronDown,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Server,
  Zap,
  Database,
  Globe,
  HardDrive,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Span, Trace } from "@/types/trace";

interface TraceTimelineWaterfallProps {
  trace: Trace | null;
  onSelectSpan?: (span: Span) => void;
}

const serviceKindIconMap: Record<string, React.ElementType> = {
  "load-balancer": Globe,
  "api-gateway": Globe,
  "auth-service": Server,
  "user-service": Server,
  "billing-service": Server,
  "notification-service": Server,
  "redis-cache": Zap,
  "postgresql-db": Database,
  "external-payment-api": HardDrive,
};

export const TraceTimelineWaterfall: React.FC<TraceTimelineWaterfallProps> = ({
  trace,
  onSelectSpan,
}) => {
  const [collapsedSpans, setCollapsedSpans] = useState<Record<string, boolean>>({});

  if (!trace || !trace.spans || trace.spans.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground text-xs font-mono">
        Select a trace to visualize OpenTelemetry span tree & latency waterfall.
      </div>
    );
  }

  const totalDuration = trace.duration_ms || 1.0;

  const toggleCollapse = (spanId: string) => {
    setCollapsedSpans((prev) => ({ ...prev, [spanId]: !prev[spanId] }));
  };

  return (
    <div className="space-y-3 text-xs font-mono">
      {/* Waterfall Header */}
      <div className="flex items-center justify-between p-3 rounded-lg bg-bg-elevated/40 border border-white/10 text-muted-foreground">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-brand-purple" />
          <span className="font-bold text-foreground">{trace.name}</span>
          <Badge variant={trace.status === "ok" ? "success" : "danger"}>
            {trace.http_status} {trace.status.toUpperCase()}
          </Badge>
        </div>
        <div>
          Total Duration: <span className="font-bold text-foreground">{trace.duration_ms} ms</span> ({trace.span_count} spans)
        </div>
      </div>

      {/* Spans Waterfall List */}
      <div className="border border-white/10 rounded-lg overflow-hidden divide-y divide-white/5 bg-bg-surface/60">
        {trace.spans.map((span, idx) => {
          const IconComp = serviceKindIconMap[span.service_name] || Server;
          const isError = span.status_code === "ERROR";

          // Calculate offset % and width % for waterfall bar
          const widthPercent = Math.max(1.0, Math.min(100.0, (span.duration_ms / totalDuration) * 100.0));
          const offsetPercent = Math.min(95.0, (idx * 12.0) % 60.0);
          const isCriticalPath = span.duration_ms > totalDuration * 0.4;

          return (
            <div
              key={span.span_id}
              onClick={() => onSelectSpan && onSelectSpan(span)}
              className={`p-3 transition-colors hover:bg-white/[0.04] cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-3 ${
                isCriticalPath ? "bg-red-950/10" : ""
              }`}
            >
              {/* Span info */}
              <div className="flex items-center gap-2 min-w-0 md:w-1/2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleCollapse(span.span_id);
                  }}
                  className="p-0.5 rounded text-muted-foreground hover:text-foreground"
                >
                  {collapsedSpans[span.span_id] ? (
                    <ChevronRight className="h-3.5 w-3.5" />
                  ) : (
                    <ChevronDown className="h-3.5 w-3.5" />
                  )}
                </button>

                <IconComp className={`h-4 w-4 shrink-0 ${isError ? "text-red-400" : "text-brand-purple"}`} />

                <div className="truncate">
                  <span className="font-bold text-foreground">{span.service_name}</span>
                  <span className="text-muted-foreground ml-2 text-[11px]">{span.operation_name}</span>
                </div>
              </div>

              {/* Waterfall Duration Bar */}
              <div className="flex-1 flex items-center gap-3">
                <div className="flex-1 bg-white/5 rounded-full h-3 relative overflow-hidden">
                  <div
                    style={{
                      left: `${offsetPercent}%`,
                      width: `${widthPercent}%`,
                    }}
                    className={`absolute top-0 bottom-0 rounded-full transition-all duration-300 ${
                      isError
                        ? "bg-red-500 shadow-glow-red"
                        : isCriticalPath
                        ? "bg-amber-500"
                        : "bg-brand-purple"
                    }`}
                  />
                </div>

                <div className="w-16 text-right font-bold text-foreground text-[11px]">
                  {span.duration_ms.toFixed(1)} ms
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
