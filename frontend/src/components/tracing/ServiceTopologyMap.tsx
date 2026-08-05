/**
 * Service Topology Map Component — Interactive Microservices Graph & Node Metrics Modal
 */

import React, { useState } from "react";
import {
  Globe,
  Database,
  Server,
  Zap,
  HardDrive,
  Activity,
  ShieldCheck,
  AlertTriangle,
  X,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { ServiceNode, ServiceEdge, ServiceMetrics } from "@/types/trace";
import { traceService } from "@/services/traceService";

interface ServiceTopologyMapProps {
  nodes: ServiceNode[];
  edges: ServiceEdge[];
  isLoading: boolean;
}

const nodeTypeIconMap: Record<string, React.ElementType> = {
  gateway: Globe,
  service: Server,
  cache: Zap,
  database: Database,
  external: HardDrive,
};

const nodeStatusBorderMap: Record<string, string> = {
  healthy: "border-emerald-500/40 bg-emerald-950/20 text-emerald-300 hover:border-emerald-500",
  warning: "border-amber-500/50 bg-amber-950/20 text-amber-300 hover:border-amber-500 scale-105",
  critical: "border-red-500/60 bg-red-950/25 text-red-300 hover:border-red-500 scale-105",
};

export const ServiceTopologyMap: React.FC<ServiceTopologyMapProps> = ({
  nodes,
  edges,
  isLoading,
}) => {
  const [selectedNode, setSelectedNode] = useState<ServiceNode | null>(null);
  const [nodeMetrics, setNodeMetrics] = useState<ServiceMetrics | null>(null);
  const [isFetchingMetrics, setIsFetchingMetrics] = useState(false);

  const handleNodeClick = async (node: ServiceNode) => {
    setSelectedNode(node);
    setIsFetchingMetrics(true);
    try {
      const data = await traceService.getServiceMetrics(node.id);
      setNodeMetrics(data);
    } catch {
      setNodeMetrics(null);
    } finally {
      setIsFetchingMetrics(false);
    }
  };

  return (
    <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-2xl relative overflow-hidden">
      <CardHeader className="p-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-brand-purple animate-pulse" />
          <CardTitle className="text-sm font-semibold text-foreground">
            Distributed Service Topology Graph
          </CardTitle>
        </div>
        <p className="text-xs text-muted-foreground">
          Click a service node to view detailed APM metrics & AI breakdown
        </p>
      </CardHeader>

      <CardContent className="p-6 min-h-[340px] flex items-center justify-center">
        {isLoading ? (
          <div className="flex items-center gap-2 text-muted-foreground text-xs animate-pulse">
            Loading service dependency map...
          </div>
        ) : (
          <div className="w-full space-y-6">
            {/* Service Grid Flow */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
              {nodes.map((node) => {
                const IconComponent = nodeTypeIconMap[node.type] || Server;
                return (
                  <div
                    key={node.id}
                    onClick={() => handleNodeClick(node)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between shadow-lg relative group ${
                      nodeStatusBorderMap[node.status] || "border-white/10"
                    }`}
                  >
                    {/* Node Header */}
                    <div className="flex items-center justify-between gap-1 mb-2">
                      <div className="flex items-center gap-1.5 min-w-0">
                        <IconComponent className="h-4 w-4 shrink-0 text-brand-purple" />
                        <span className="font-bold text-xs truncate">{node.label}</span>
                      </div>
                      <span className={`h-2 w-2 rounded-full ${node.status === 'healthy' ? 'bg-emerald-400' : 'bg-amber-400 animate-ping'}`} />
                    </div>

                    {/* Metrics Peek */}
                    <div className="space-y-1 font-mono text-[11px]">
                      <div className="flex items-center justify-between text-muted-foreground">
                        <span>Latency:</span>
                        <span className="font-bold text-foreground">{node.avg_latency_ms} ms</span>
                      </div>
                      <div className="flex items-center justify-between text-muted-foreground">
                        <span>RPS:</span>
                        <span className="font-bold text-foreground">{node.rps.toFixed(0)}</span>
                      </div>
                      <div className="flex items-center justify-between text-muted-foreground">
                        <span>Error %:</span>
                        <span className={node.error_rate_percent > 1.0 ? "text-red-400 font-bold" : "text-emerald-400 font-bold"}>
                          {node.error_rate_percent.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Edge Summary Ribbon */}
            <div className="p-3 rounded-lg bg-bg-elevated/40 border border-white/5 flex flex-wrap items-center justify-around gap-2 text-xs font-mono text-muted-foreground">
              <span>Trace Flow: Load Balancer ➔ API Gateway ➔ Auth / User / Billing ➔ Cache & DB</span>
            </div>
          </div>
        )}
      </CardContent>

      {/* Node Click Modal */}
      {selectedNode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-bg-surface border border-white/10 rounded-xl p-6 space-y-4 text-xs shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center gap-2">
                <Server className="h-4 w-4 text-brand-purple" />
                <h3 className="text-sm font-bold text-foreground">{selectedNode.label}</h3>
                <Badge variant={selectedNode.status === "healthy" ? "success" : "warning"}>
                  {selectedNode.status}
                </Badge>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 rounded text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {isFetchingMetrics ? (
              <div className="py-8 text-center text-muted-foreground animate-pulse">
                Fetching APM metrics...
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-3 p-3 rounded-lg bg-bg-elevated/40 border border-white/5 text-center font-mono">
                  <div>
                    <div className="text-[10px] text-muted-foreground">Avg Latency</div>
                    <div className="text-sm font-bold text-foreground">{nodeMetrics?.avg_latency_ms || selectedNode.avg_latency_ms} ms</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-muted-foreground">Requests / Sec</div>
                    <div className="text-sm font-bold text-foreground">{nodeMetrics?.requests_per_second || selectedNode.rps}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-muted-foreground">Error Rate</div>
                    <div className="text-sm font-bold text-red-400">{nodeMetrics?.error_rate_percent || selectedNode.error_rate_percent}%</div>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-brand-purple/10 border border-brand-purple/20 space-y-1">
                  <div className="flex items-center gap-1.5 text-brand-purple font-semibold">
                    <Sparkles className="h-3.5 w-3.5" /> AI Health Assessment
                  </div>
                  <p className="text-foreground leading-relaxed text-xs">
                    {nodeMetrics?.ai_summary || "Service operating within healthy SLO latency bounds."}
                  </p>
                </div>
              </div>
            )}

            <div className="pt-2 text-right">
              <Button size="sm" variant="outline" onClick={() => setSelectedNode(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};
