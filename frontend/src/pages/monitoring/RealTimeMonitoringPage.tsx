/**
 * Real-Time Observability Platform — Main Page
 */

import React from "react";
import {
  Radio,
  Pause,
  Play,
  Zap,
  Activity,
  Users,
  Clock,
  ShieldAlert,
  Server,
  Database,
  TrendingUp,
  X,
} from "lucide-react";

import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";

import { useRealtimeMetrics } from "@/hooks/useRealtimeMetrics";
import { MetricGauge } from "@/components/monitoring/MetricGauge";
import { LiveChart } from "@/components/monitoring/LiveChart";
import { K8sPodsTable } from "@/components/monitoring/K8sPodsTable";

export default function RealTimeMonitoringPage() {
  const {
    current,
    history,
    isConnected,
    isPaused,
    togglePause,
    lastAlert,
    clearAlert,
  } = useRealtimeMetrics();

  return (
    <div className="space-y-6">
      {/* Real-time Alert Banner Popup */}
      {lastAlert && (
        <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-red-300 flex items-center justify-between text-xs animate-in slide-in-from-top duration-300">
          <div className="flex items-center gap-2 font-mono">
            <ShieldAlert className="h-4 w-4 text-red-400 animate-bounce" />
            <span className="font-bold">Realtime Telemetry Alert:</span> {lastAlert}
          </div>
          <button
            onClick={clearAlert}
            className="p-1 rounded hover:bg-white/10 text-muted-foreground hover:text-foreground"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      {/* Page Header */}
      <PageHeader
        title="Real-Time Observability Platform"
        subtitle="Datadog & Grafana Cloud style live sub-second metric streaming with WebSockets"
        actions={
          <div className="flex items-center gap-3">
            {/* Live WebSocket Connection Badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-bg-surface border border-white/10 text-xs font-mono">
              <Radio
                className={`h-3.5 w-3.5 ${
                  isConnected ? "text-emerald-400 animate-pulse" : "text-amber-400"
                }`}
              />
              <span className="text-muted-foreground">Stream:</span>
              <span className={isConnected ? "text-emerald-400 font-bold" : "text-amber-400"}>
                {isConnected ? "LIVE (2s)" : "Reconnecting..."}
              </span>
            </div>

            {/* Pause / Resume Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={togglePause}
              className={`gap-1.5 text-xs ${
                isPaused
                  ? "bg-amber-950/20 text-amber-400 border-amber-500/30"
                  : "bg-bg-surface text-foreground"
              }`}
            >
              {isPaused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
              {isPaused ? "Resume Stream" : "Pause Stream"}
            </Button>
          </div>
        }
      />

      {/* Animated Top KPI Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="Active User Sessions"
          value={current?.active_users.toLocaleString() || "8,450"}
          subValue="Live concurrent connections"
        />
        <StatCard
          label="Requests / Sec (RPS)"
          value={current?.requests_per_second.toLocaleString() || "1,450"}
          subValue="Ingress HTTP throughput"
        />
        <StatCard
          label="P99 Response Time"
          value={`${current?.response_time_ms.toFixed(1) || "124.0"} ms`}
          subValue="Mean latency across services"
        />
        <StatCard
          label="Error Rate"
          value={`${current?.error_rate.toFixed(2) || "0.25"}%`}
          subValue="HTTP 5xx / 4xx failure ratio"
        />
      </div>

      {/* Realtime Gauges Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricGauge
          title="CPU Utilization"
          value={current?.cpu_usage || 48.0}
          subValue="8 Cores Allocated"
          icon={Activity}
        />
        <MetricGauge
          title="Memory Heap Usage"
          value={current?.memory_usage || 62.5}
          subValue="16.0 GB Total RAM"
          icon={Zap}
        />
        <MetricGauge
          title="Disk I/O Usage"
          value={current?.disk_usage || 58.0}
          subValue="500 GB NVMe Storage"
          icon={Server}
        />
      </div>

      {/* Streaming Recharts Area Graphs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LiveChart
          title="P99 Latency & Response Time Trajectory (ms)"
          data={history}
          dataKey="response_time_ms"
          strokeColor="#a855f7"
          fillGradientId="latencyGradient"
          unit=" ms"
          icon={Clock}
        />

        <LiveChart
          title="Ingress Traffic Requests per Second (RPS)"
          data={history}
          dataKey="requests_per_second"
          strokeColor="#3b82f6"
          fillGradientId="rpsGradient"
          icon={TrendingUp}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LiveChart
          title="HTTP Error Rate Sparkline (%)"
          data={history}
          dataKey="error_rate"
          strokeColor="#ef4444"
          fillGradientId="errorGradient"
          unit="%"
          icon={ShieldAlert}
        />

        <LiveChart
          title="Database Active Pool Connections"
          data={history}
          dataKey="db_connections_active"
          strokeColor="#10b981"
          fillGradientId="dbGradient"
          icon={Database}
        />
      </div>

      {/* Kubernetes Pod Telemetry Table */}
      <K8sPodsTable pods={current?.k8s_pods || []} />
    </div>
  );
}
