import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { GitMerge } from "lucide-react";
import { TelemetryEventItem } from "@/services/telemetryService";
import { format } from "date-fns";

interface TraceTimelineProps {
  events: TelemetryEventItem[];
}

export const TraceTimeline: React.FC<TraceTimelineProps> = ({ events }) => {
  const traceEvents = events.filter((e) => e.event_type === "trace_bottleneck" || e.source === "trace_processor");

  return (
    <Card className="col-span-2 md:col-span-1 border border-border/50">
      <CardHeader className="bg-muted/30 py-3 border-b">
        <CardTitle className="text-sm font-semibold flex items-center">
          <GitMerge className="w-4 h-4 mr-2" />
          Distributed Traces & Bottlenecks
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 h-[400px] overflow-y-auto">
        {traceEvents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground text-sm">
            <GitMerge className="w-8 h-8 mb-2 opacity-20" />
            No trace bottlenecks detected
          </div>
        ) : (
          <div className="space-y-4">
            {traceEvents.map((event, i) => (
              <div key={event.id} className="relative pl-6 pb-4 border-l-2 border-slate-200 dark:border-slate-800 last:border-0 last:pb-0">
                <div className={`absolute -left-1.5 top-1.5 w-3 h-3 rounded-full ${event.severity === 'CRITICAL' ? 'bg-red-500' : 'bg-yellow-500'} border-2 border-white dark:border-slate-950`} />
                <div className="flex justify-between items-start mb-1">
                  <div className="font-medium text-sm">
                    {event.metadata?.operation || event.raw_payload?.operation || "Unknown Operation"}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {format(new Date(event.timestamp), "HH:mm:ss")}
                  </div>
                </div>
                <div className="text-xs text-muted-foreground">
                  Service: <span className="font-semibold text-foreground">{event.metadata?.slowest_service || "Unknown"}</span>
                </div>
                <div className="text-xs text-muted-foreground">
                  Duration: <span className="font-semibold text-foreground">{event.metadata?.duration_ms?.toFixed(1) || 0}ms</span>
                </div>
                {event.metadata?.error_spans_count > 0 && (
                  <div className="mt-2 text-xs text-red-500 bg-red-500/10 px-2 py-1 rounded inline-block">
                    {event.metadata.error_spans_count} Error Span(s) Detected
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
