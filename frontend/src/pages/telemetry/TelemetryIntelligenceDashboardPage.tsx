import React from "react";
import { useTelemetryHealth, useTelemetryEvents, useAIOperationalSummary } from "@/hooks/useTelemetry";
import { MetricCard } from "@/components/telemetry/MetricCard";
import { LogViewer } from "@/components/telemetry/LogViewer";
import { TraceTimeline } from "@/components/telemetry/TraceTimeline";
import { AIInsightPanel } from "@/components/telemetry/AIInsightPanel";
import { Activity, Network, ShieldAlert, Cpu } from "lucide-react";
import { Button } from "@/components/ui/button";

const TelemetryIntelligenceDashboardPage: React.FC = () => {
  const { data: health, isLoading: isHealthLoading } = useTelemetryHealth();
  const { data: events = [], isLoading: isEventsLoading } = useTelemetryEvents(100);
  const { data: aiSummary, isLoading: isAiSummaryLoading } = useAIOperationalSummary();

  const metricsIngested = health?.metrics_ingested_total || 0;
  const eventsIngested = health?.events_ingested_total || 0;
  const tracesIngested = health?.traces_ingested_total || 0;
  const anomaliesCount = health?.active_anomalies_count || 0;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Telemetry Intelligence</h1>
          <p className="text-muted-foreground mt-1">Unified observability pipelines and AI-driven correlation.</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center text-sm text-muted-foreground bg-muted/50 px-3 py-1.5 rounded-full">
            <span className={`w-2 h-2 rounded-full mr-2 ${health?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
            Pipeline: {health?.status === 'healthy' ? 'Operational' : 'Degraded'}
          </div>
          <Button variant="outline" size="sm">Configure Collectors</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Metrics Processed"
          value={metricsIngested}
          unit="datapoints"
          trend="up"
          trendValue="+12%"
          description="last 1h"
        />
        <MetricCard
          title="Log Events"
          value={eventsIngested}
          unit="lines"
          trend="stable"
          trendValue="0%"
          description="last 1h"
        />
        <MetricCard
          title="Distributed Traces"
          value={tracesIngested}
          unit="spans"
          trend="up"
          trendValue="+5%"
          description="last 1h"
        />
        <MetricCard
          title="Active Anomalies"
          value={anomaliesCount}
          unit="incidents"
          trend={anomaliesCount > 0 ? "up" : "stable"}
          description="requires attention"
        />
      </div>

      <div className="grid grid-cols-1 gap-6">
        <AIInsightPanel summary={aiSummary} isLoading={isAiSummaryLoading} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <LogViewer events={events} />
        <TraceTimeline events={events} />
      </div>
    </div>
  );
};

export default TelemetryIntelligenceDashboardPage;
