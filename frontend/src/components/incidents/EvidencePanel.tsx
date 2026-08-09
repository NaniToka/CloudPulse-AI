import React, { useState } from "react";
import {
  Activity,
  AlertCircle,
  Database,
  FileText,
  Layers,
  Network,
  Server,
  Terminal,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import type { EvidenceItem } from "@/types/incident";

interface Props {
  evidence?: EvidenceItem[];
}

export function EvidencePanel({ evidence = [] }: Props) {
  const [activeTab, setActiveTab] = useState<string>("all");

  const defaultEvidence: EvidenceItem[] = [
    {
      type: "metric",
      source: "postgres-primary",
      message: "Database active connection pool at 98.4% (197/200 connections in use)",
      severity: "CRITICAL",
      metric_value: 98.4,
      threshold: 80.0,
      details: { max_connections: 200, active: 197, idle_in_transaction: 42 },
    },
    {
      type: "trace",
      source: "api-gateway",
      message: "HTTP 504 Gateway Timeouts on /api/v1/checkout. Trace span latency 4.2x above SLO baseline.",
      severity: "HIGH",
      metric_value: 2450.0,
      threshold: 350.0,
      details: { p99_latency_ms: 2450, error_rate_pct: 12.4 },
    },
    {
      type: "log",
      source: "postgres-primary",
      message: "FATAL: remaining connection slots are reserved for non-replication superuser connections (SQLSTATE 53300)",
      severity: "CRITICAL",
      details: { process_id: 8192, log_level: "FATAL" },
    },
    {
      type: "topology",
      source: "ServiceDependencyGraph",
      message: "Multiple microservices (payment-service, auth-service, order-worker) share postgres-primary dependency",
      severity: "MEDIUM",
      details: { shared_nodes_count: 4 },
    },
  ];

  const items = evidence.length > 0 ? evidence : defaultEvidence;

  const filteredItems = items.filter((item) => {
    if (activeTab === "all") return true;
    return item.type.toLowerCase() === activeTab.toLowerCase();
  });

  const getEvidenceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "metric":
        return <Activity className="w-4 h-4 text-amber-400" />;
      case "trace":
        return <Network className="w-4 h-4 text-red-400" />;
      case "log":
        return <Terminal className="w-4 h-4 text-rose-400" />;
      case "topology":
      case "infrastructure":
        return <Layers className="w-4 h-4 text-cyan-400" />;
      default:
        return <FileText className="w-4 h-4 text-blue-400" />;
    }
  };

  const getSeverityBadge = (sev: string = "HIGH") => {
    const s = sev.toUpperCase();
    if (s === "CRITICAL" || s === "P0") {
      return <Badge className="bg-red-500/15 text-red-400 border-red-500/30 text-[10px] font-mono">CRITICAL</Badge>;
    }
    if (s === "HIGH" || s === "P1") {
      return <Badge className="bg-orange-500/15 text-orange-400 border-orange-500/30 text-[10px] font-mono">HIGH</Badge>;
    }
    if (s === "MEDIUM" || s === "P2") {
      return <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 text-[10px] font-mono">MEDIUM</Badge>;
    }
    return <Badge className="bg-blue-500/15 text-blue-400 border-blue-500/30 text-[10px] font-mono">INFO</Badge>;
  };

  return (
    <div className="space-y-4">
      {/* Evidence Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-2">
          <TabsList className="bg-bg-surface border border-white/[0.08] h-9 p-1">
            <TabsTrigger value="all" className="text-xs font-mono">
              All Evidence ({items.length})
            </TabsTrigger>
            <TabsTrigger value="metric" className="text-xs font-mono">
              Metrics
            </TabsTrigger>
            <TabsTrigger value="log" className="text-xs font-mono">
              Logs
            </TabsTrigger>
            <TabsTrigger value="trace" className="text-xs font-mono">
              Traces
            </TabsTrigger>
            <TabsTrigger value="topology" className="text-xs font-mono">
              Topology
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value={activeTab} className="mt-4 space-y-3">
          {filteredItems.map((item, idx) => (
            <div
              key={idx}
              className="rounded-lg border border-white/[0.08] bg-white/[0.02] p-4 hover:border-white/[0.18] transition-all"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded bg-white/[0.04] border border-white/[0.08]">
                    {getEvidenceIcon(item.type)}
                  </div>
                  <span className="font-mono text-xs font-semibold text-white">
                    {item.source}
                  </span>
                  <Badge variant="outline" className="text-[10px] font-mono uppercase border-white/20">
                    {item.type}
                  </Badge>
                </div>
                <div>{getSeverityBadge(item.severity)}</div>
              </div>

              <p className="text-xs font-mono text-muted-foreground leading-relaxed pl-8">
                {item.message}
              </p>

              {item.details && Object.keys(item.details).length > 0 && (
                <div className="mt-3 pl-8 flex flex-wrap gap-2 text-[11px] font-mono">
                  {Object.entries(item.details).map(([k, v]) => (
                    <span
                      key={k}
                      className="px-2 py-0.5 rounded bg-white/[0.03] border border-white/[0.06] text-muted-foreground"
                    >
                      <span className="text-muted-foreground/60">{k}:</span> {String(v)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}
