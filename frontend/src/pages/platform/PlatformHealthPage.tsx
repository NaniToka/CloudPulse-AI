import React, { useEffect, useState, useCallback, useRef } from "react";
import {
  Activity,
  RefreshCw,
  Server,
  Database,
  Cpu,
  Zap,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  ShieldCheck,
  Globe,
  Radio,
  Layers,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { getDetailedPlatformHealth } from "@/services/platformService";
import { PlatformHealthDetailedResponse, DependencyHealthItem } from "@/types/platform";

export function PlatformHealthPage() {
  const [data, setData] = useState<PlatformHealthDetailedResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(false);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getDetailedPlatformHealth();
      setData(res);
      setLastRefreshed(new Date());
    } catch (err: any) {
      setError(err?.response?.data?.error || err.message || "Failed to load platform health telemetry.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  useEffect(() => {
    if (autoRefresh) {
      timerRef.current = setInterval(() => {
        fetchHealth();
      }, 30000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [autoRefresh, fetchHealth]);

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / (3600 * 24));
    const hours = Math.floor((seconds % (3600 * 24)) / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    if (days > 0) return `${days}d ${hours}h ${mins}m`;
    if (hours > 0) return `${hours}h ${mins}m ${secs}s`;
    return `${mins}m ${secs}s`;
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "healthy":
      case "configured":
        return (
          <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 gap-1.5 px-2.5 py-0.5">
            <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
          </Badge>
        );
      case "degraded":
      case "demo_local_mode":
        return (
          <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20 gap-1.5 px-2.5 py-0.5">
            <AlertTriangle className="w-3.5 h-3.5" /> Degraded / Fallback
          </Badge>
        );
      case "unhealthy":
      case "critical":
        return (
          <Badge className="bg-rose-500/10 text-rose-400 border-rose-500/20 gap-1.5 px-2.5 py-0.5">
            <XCircle className="w-3.5 h-3.5" /> Unhealthy
          </Badge>
        );
      default:
        return (
          <Badge variant="outline" className="gap-1.5 px-2.5 py-0.5">
            <Radio className="w-3.5 h-3.5 text-muted-foreground" /> {status}
          </Badge>
        );
    }
  };

  const getDepIcon = (name: string) => {
    switch (name.toLowerCase()) {
      case "backend_api":
        return <Server className="w-5 h-5 text-indigo-400" />;
      case "database":
        return <Database className="w-5 h-5 text-emerald-400" />;
      case "redis":
        return <Zap className="w-5 h-5 text-rose-400" />;
      case "chromadb":
        return <Layers className="w-5 h-5 text-amber-400" />;
      case "ai_engine":
        return <Cpu className="w-5 h-5 text-purple-400" />;
      case "workers":
        return <Activity className="w-5 h-5 text-cyan-400" />;
      case "cloud_integrations":
        return <Globe className="w-5 h-5 text-blue-400" />;
      default:
        return <Radio className="w-5 h-5 text-slate-400" />;
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto min-h-screen">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-border/40 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
              <ShieldCheck className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Platform Health & Quality Center</h1>
              <p className="text-sm text-muted-foreground">
                Real-time dependency readiness, system resource metrics, and API quality score.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center space-x-2 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-border/40">
            <input
              type="checkbox"
              id="auto-refresh-check"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="accent-indigo-500 cursor-pointer rounded"
            />
            <label htmlFor="auto-refresh-check" className="text-xs font-medium cursor-pointer text-slate-300">
              Auto Refresh (30s)
            </label>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={fetchHealth}
            disabled={loading}
            className="gap-2 border-indigo-500/30 hover:bg-indigo-500/10 text-indigo-300"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh Telemetry
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-rose-400 shrink-0" />
            <div>
              <p className="text-sm font-semibold">Platform Telemetry Error</p>
              <p className="text-xs text-rose-300/80 mt-0.5">{error}</p>
            </div>
          </div>
          <Button size="sm" variant="outline" onClick={fetchHealth} className="border-rose-500/30 hover:bg-rose-500/20 text-rose-300">
            Retry Connection
          </Button>
        </div>
      )}

      {loading && !data && (
        <div className="py-24 text-center space-y-4">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-indigo-400" />
          <p className="text-sm text-muted-foreground">Evaluating core platform dependencies and hardware metrics...</p>
        </div>
      )}

      {data && (
        <>
          {/* Section 1: Health Score & Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
              <CardHeader className="pb-2">
                <CardDescription className="text-xs uppercase tracking-wider font-semibold">Overall Health Score</CardDescription>
                <div className="flex items-baseline justify-between mt-1">
                  <span className="text-3xl font-extrabold text-foreground">{data.overall_health_score} <span className="text-lg font-normal text-muted-foreground">/ 100</span></span>
                  {getStatusBadge(data.overall_status)}
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <Progress value={data.overall_health_score} className="h-2 mt-2 bg-slate-800" />
                <p className="text-xs text-muted-foreground mt-2">
                  Calculated deterministically from 7 platform subsystems.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
              <CardHeader className="pb-2">
                <CardDescription className="text-xs uppercase tracking-wider font-semibold">System Availability</CardDescription>
                <div className="text-3xl font-extrabold text-emerald-400 mt-1">
                  {data.availability_pct}%
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <p className="text-xs text-muted-foreground mt-2">
                  {data.healthy_components_count} Healthy / {data.degraded_components_count} Degraded / {data.unhealthy_components_count} Unhealthy
                </p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
              <CardHeader className="pb-2">
                <CardDescription className="text-xs uppercase tracking-wider font-semibold">Process Memory (RSS)</CardDescription>
                <div className="text-3xl font-extrabold text-indigo-400 mt-1">
                  {data.system_metrics.process_memory_mb} <span className="text-sm font-normal text-muted-foreground">MB</span>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <p className="text-xs text-muted-foreground mt-2">
                  System Memory Load: {data.system_metrics.system_memory_pct}%
                </p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
              <CardHeader className="pb-2">
                <CardDescription className="text-xs uppercase tracking-wider font-semibold">Process Uptime</CardDescription>
                <div className="text-3xl font-extrabold text-cyan-400 mt-1">
                  {formatUptime(data.system_metrics.process_uptime_seconds)}
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <p className="text-xs text-muted-foreground mt-2">
                  Last checked: {new Date(lastRefreshed).toLocaleTimeString()}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Section 2: Dependency Status Grid */}
          <div className="space-y-3">
            <h2 className="text-lg font-semibold tracking-tight flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" /> System Subsystems & Dependencies
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(data.dependencies).map(([key, dep]: [string, DependencyHealthItem]) => (
                <Card key={key} className="bg-slate-900/40 border-slate-800/80 hover:border-slate-700 transition-colors">
                  <CardHeader className="pb-3 flex flex-row items-center justify-between space-y-0">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 rounded-lg bg-slate-800/60 border border-slate-700/50">
                        {getDepIcon(key)}
                      </div>
                      <div>
                        <CardTitle className="text-sm font-semibold capitalize">
                          {key.replace("_", " ")}
                        </CardTitle>
                        <CardDescription className="text-xs font-mono text-slate-400 mt-0.5">
                          Latency: {dep.latency_ms} ms
                        </CardDescription>
                      </div>
                    </div>
                    {getStatusBadge(dep.status)}
                  </CardHeader>
                  <CardContent className="pt-0 space-y-2">
                    <p className="text-xs text-slate-300 line-clamp-2">{dep.message}</p>
                    <div className="flex items-center justify-between text-[11px] text-muted-foreground border-t border-slate-800/60 pt-2 mt-2">
                      <span>Checked: {new Date(dep.last_checked).toLocaleTimeString()}</span>
                      {dep.status !== "healthy" && dep.status !== "configured" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={fetchHealth}
                          className="h-6 text-[11px] px-2 text-amber-400 hover:text-amber-300 hover:bg-amber-500/10"
                        >
                          Retry
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Section 3: API Performance Telemetry & Slowest Endpoints */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2 bg-slate-900/50 border-slate-800">
              <CardHeader>
                <CardTitle className="text-base font-semibold flex items-center gap-2">
                  <Zap className="w-5 h-5 text-amber-400" /> API Performance & Latency Telemetry
                </CardTitle>
                <CardDescription>Real-time request throughput and endpoint latency tracing.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-3 p-3 rounded-lg bg-slate-950/60 border border-slate-800/60 text-center">
                  <div>
                    <span className="text-xs text-muted-foreground">Requests / Min</span>
                    <p className="text-xl font-bold text-foreground mt-0.5">{data.api_performance.requests_per_minute}</p>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground">Avg Latency</span>
                    <p className="text-xl font-bold text-indigo-400 mt-0.5">{data.api_performance.avg_latency_ms} ms</p>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground">Error Rate</span>
                    <p className={`text-xl font-bold mt-0.5 ${data.api_performance.error_rate_pct > 0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {data.api_performance.error_rate_pct}%
                    </p>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Slowest Monitored Endpoints</h4>
                  {data.api_performance.slowest_endpoints.length === 0 ? (
                    <p className="text-xs text-muted-foreground italic py-4 text-center">No slow endpoints recorded in current telemetry buffer.</p>
                  ) : (
                    <div className="space-y-2">
                      {data.api_performance.slowest_endpoints.map((ep, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2.5 rounded-md bg-slate-950/40 border border-slate-800/40 text-xs">
                          <div className="flex items-center gap-2 font-mono">
                            <Badge variant="outline" className="text-[10px] uppercase px-1.5 py-0 border-indigo-500/30 text-indigo-300">
                              {ep.method}
                            </Badge>
                            <span className="text-slate-300 truncate max-w-[280px] sm:max-w-[400px]">{ep.endpoint}</span>
                          </div>
                          <div className="flex items-center gap-3 font-mono">
                            <span className="text-muted-foreground">{ep.requests} reqs</span>
                            <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20">
                              {ep.avg_latency_ms} ms
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Section 4: Operational Mode & Environment Badges */}
            <Card className="bg-slate-900/50 border-slate-800 flex flex-col justify-between">
              <CardHeader>
                <CardTitle className="text-base font-semibold flex items-center gap-2">
                  <Globe className="w-5 h-5 text-blue-400" /> Platform Operational Mode
                </CardTitle>
                <CardDescription>Environment configuration and AI engine status.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/60 space-y-2.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-muted-foreground">Environment:</span>
                    <Badge variant="outline" className="font-mono capitalize border-blue-500/30 text-blue-300">
                      {data.environment_info.environment}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-muted-foreground">AI Intelligence Mode:</span>
                    <Badge variant="outline" className="font-mono text-[11px] border-purple-500/30 text-purple-300">
                      {data.environment_info.ai_mode_label}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-muted-foreground">Cloud Credentials:</span>
                    <Badge variant="outline" className="font-mono text-[11px] border-emerald-500/30 text-emerald-300">
                      {data.environment_info.cloud_credential_status}
                    </Badge>
                  </div>
                </div>

                {data.environment_info.demo_mode && (
                  <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-300 text-xs space-y-1">
                    <div className="flex items-center gap-2 font-semibold">
                      <Radio className="h-4 w-4 text-blue-400 shrink-0" />
                      <span>Local Demo / Development Mode Active</span>
                    </div>
                    <p className="text-[11px] text-blue-200/80 pl-6">
                      System telemetry is enriched using local deterministic fixture data when external cloud keys are not configured.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Section 5: Recent System Events Log */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Clock className="w-5 h-5 text-cyan-400" /> Recent Platform System Events
              </CardTitle>
              <CardDescription>Audit event log generated by core system health probes.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {data.system_events.map((evt, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950/40 border border-slate-800/40 text-xs">
                    <div className="flex items-center gap-3">
                      <Badge className={evt.severity === "ERROR" ? "bg-rose-500/10 text-rose-400" : evt.severity === "WARNING" ? "bg-amber-500/10 text-amber-400" : "bg-emerald-500/10 text-emerald-400"}>
                        {evt.severity}
                      </Badge>
                      <span className="font-semibold text-slate-300">{evt.component}</span>
                      <span className="text-slate-400">{evt.message}</span>
                    </div>
                    <span className="font-mono text-muted-foreground text-[11px]">
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
