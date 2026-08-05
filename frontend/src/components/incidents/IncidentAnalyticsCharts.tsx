/**
 * Incident Analytics Charts Component
 * Visualizes:
 * - Incidents by Severity
 * - Monthly Incident Trend
 * - Active vs Resolved Distribution
 * - MTTR & Resolution Rate Metrics
 */

import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Clock, CheckCircle2, AlertOctagon, TrendingUp } from "lucide-react";
import type { IncidentAnalytics } from "@/types/incident";

interface IncidentAnalyticsChartsProps {
  analytics: IncidentAnalytics | undefined;
  isLoading: boolean;
}

const SEVERITY_COLORS: Record<string, string> = {
  P0: "#ef4444", // red-500
  P1: "#f97316", // orange-500
  P2: "#eab308", // yellow-500
  P3: "#3b82f6", // blue-500
};

const PIE_COLORS = ["#ef4444", "#10b981"]; // Active = red, Resolved = emerald

export const IncidentAnalyticsCharts: React.FC<IncidentAnalyticsChartsProps> = ({
  analytics,
  isLoading,
}) => {
  if (isLoading || !analytics) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-pulse">
        <div className="h-64 bg-white/5 rounded-xl" />
        <div className="h-64 bg-white/5 rounded-xl" />
        <div className="h-64 bg-white/5 rounded-xl" />
        <div className="h-64 bg-white/5 rounded-xl" />
      </div>
    );
  }

  const activeVsResolvedData = [
    { name: "Active", value: analytics.active_incidents },
    { name: "Resolved", value: analytics.resolved_incidents },
  ];

  return (
    <div className="space-y-6">
      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 bg-bg-surface/80 border-white/10 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Mean Time To Resolve (MTTR)</span>
            <div className="p-2 rounded-lg bg-brand-blue/20 text-brand-blue">
              <Clock className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-foreground mt-2">
            {analytics.mean_time_to_resolve_minutes} <span className="text-xs font-normal text-muted-foreground">mins</span>
          </div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
            <TrendingUp className="h-3 w-3" /> 12% faster than last month
          </div>
        </Card>

        <Card className="p-4 bg-bg-surface/80 border-white/10 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Resolution Rate</span>
            <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400">
              <CheckCircle2 className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-foreground mt-2">
            {analytics.resolution_rate_percent}%
          </div>
          <div className="text-[11px] text-muted-foreground mt-1">
            {analytics.resolved_incidents} of {analytics.total_incidents} closed
          </div>
        </Card>

        <Card className="p-4 bg-bg-surface/80 border-white/10 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Active Incidents</span>
            <div className="p-2 rounded-lg bg-red-500/20 text-red-400">
              <AlertOctagon className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-red-400 mt-2">
            {analytics.active_incidents}
          </div>
          <div className="text-[11px] text-muted-foreground mt-1">Requiring active triage</div>
        </Card>

        <Card className="p-4 bg-bg-surface/80 border-white/10 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Total Managed</span>
            <div className="p-2 rounded-lg bg-brand-purple/20 text-brand-purple">
              <Activity className="h-4 w-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-foreground mt-2">
            {analytics.total_incidents}
          </div>
          <div className="text-[11px] text-muted-foreground mt-1">Tracked lifetime</div>
        </Card>
      </div>

      {/* Grid of Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Incidents by Severity */}
        <Card className="p-4 bg-bg-surface/80 border-white/10 backdrop-blur-md">
          <CardHeader className="p-0 pb-3">
            <CardTitle className="text-sm font-semibold text-foreground">
              Incidents by Severity
            </CardTitle>
            <p className="text-xs text-muted-foreground">Distribution across P0, P1, P2, and P3 levels</p>
          </CardHeader>
          <CardContent className="p-0 h-[220px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics.incidents_by_severity} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
                <XAxis dataKey="severity" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-bg-elevated p-2 rounded border border-white/10 text-xs shadow-xl">
                          <span className="font-bold text-foreground">{data.severity}:</span> {data.count} incidents
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {analytics.incidents_by_severity.map((entry) => (
                    <Cell key={entry.severity} fill={SEVERITY_COLORS[entry.severity] || "#3b82f6"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Chart 2: Monthly Trend */}
        <Card className="p-4 bg-bg-surface/80 border-white/10 backdrop-blur-md">
          <CardHeader className="p-0 pb-3">
            <CardTitle className="text-sm font-semibold text-foreground">
              Monthly Incident Trend
            </CardTitle>
            <p className="text-xs text-muted-foreground">Total opened vs resolved incidents over time</p>
          </CardHeader>
          <CardContent className="p-0 h-[220px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={analytics.monthly_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-bg-elevated p-2 rounded border border-white/10 text-xs shadow-xl space-y-1">
                          <div className="font-bold text-foreground">{d.month}</div>
                          <div className="text-purple-400">Total Opened: {d.count}</div>
                          <div className="text-emerald-400">Resolved: {d.resolved_count}</div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Area type="monotone" dataKey="count" stroke="#8b5cf6" strokeWidth={2} fill="url(#trendGradient)" />
                <Area type="monotone" dataKey="resolved_count" stroke="#10b981" strokeWidth={2} fillOpacity={0} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Chart 3: Active vs Resolved Donut */}
        <Card className="p-4 bg-bg-surface/80 border-white/10 backdrop-blur-md lg:col-span-2">
          <CardHeader className="p-0 pb-3">
            <CardTitle className="text-sm font-semibold text-foreground">
              Active vs Resolved Ratio
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0 h-[200px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={activeVsResolvedData}
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {activeVsResolvedData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
