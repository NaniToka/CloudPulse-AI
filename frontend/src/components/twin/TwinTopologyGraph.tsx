import React from "react";
import { Server, Database, Cloud, Radio, Zap, ShieldAlert, Cpu, Box, HardDrive, Play } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface TwinTopologyGraphProps {
  nodes: Array<{
    id: string;
    name: string;
    type: string;
    status: string;
  }>;
  affectedNodeIds?: string[];
  onSelectNode?: (nodeId: string) => void;
}

const typeIcons: Record<string, any> = {
  region: Cloud,
  load_balancer: Radio,
  gateway: Zap,
  microservice: Box,
  cache: Server,
  database: Database,
  queue: HardDrive,
};

export default function TwinTopologyGraph({ nodes, affectedNodeIds = [], onSelectNode }: TwinTopologyGraphProps) {
  return (
    <div className="relative rounded-xl border border-white/10 bg-slate-950/90 p-6 shadow-2xl overflow-hidden backdrop-blur-md">
      {/* Background Grid Pattern */}
      <div
        className="absolute inset-0 opacity-15 pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle at 1px 1px, rgba(56,189,248,0.3) 1px, transparent 0)",
          backgroundSize: "28px 28px",
        }}
      />

      <div className="flex items-center justify-between pb-5 border-b border-white/10 relative z-10">
        <div>
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2 font-mono">
            <Radio className="h-4 w-4 text-sky-400 animate-pulse" />
            3D Virtual Topology & Failure Propagation Mesh
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Real-time digital twin node health with animated blast-radius propagation
          </p>
        </div>
        <Badge variant="outline" className="border-sky-500/40 text-sky-400 font-mono text-[10px]">
          {nodes.length} Virtual Artifacts Active
        </Badge>
      </div>

      {/* Nodes Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 pt-6 relative z-10">
        {nodes.map((node) => {
          const Icon = typeIcons[node.type] || Box;
          const isAffected = affectedNodeIds.includes(node.id);

          return (
            <div
              key={node.id}
              onClick={() => onSelectNode?.(node.id)}
              className={cn(
                "rounded-xl border p-4 transition-all duration-300 cursor-pointer backdrop-blur-sm space-y-2",
                isAffected
                  ? "border-rose-500 bg-rose-500/10 shadow-lg shadow-rose-500/20 ring-2 ring-rose-500/40 animate-pulse"
                  : "border-white/10 bg-white/[0.02] hover:border-sky-500/40 hover:bg-sky-500/[0.04]"
              )}
            >
              <div className="flex items-center justify-between">
                <Icon className={cn("h-4 w-4", isAffected ? "text-rose-400" : "text-sky-400")} />
                <Badge
                  variant={isAffected ? "danger" : "success"}
                  className="text-[9px] font-mono px-1.5 py-0"
                >
                  {isAffected ? "FAILED" : "HEALTHY"}
                </Badge>
              </div>

              <div>
                <h4 className="text-xs font-mono font-bold text-foreground truncate">{node.name}</h4>
                <p className="text-[10px] text-muted-foreground uppercase font-mono mt-0.5">{node.type}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
