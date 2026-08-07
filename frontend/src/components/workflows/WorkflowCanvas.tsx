import React from "react";
import { Zap, Play, ShieldAlert, Cpu, Box, MessageSquare, Server, Terminal, CheckCircle2, AlertTriangle, UserCheck, Sparkles, ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface WorkflowCanvasProps {
  nodes: Array<{
    id: string;
    type: string;
    label: string;
    position: { x: number; y: number };
    config?: Record<string, any>;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    condition?: string;
  }>;
  selectedNodeId: string | null;
  onSelectNode: (id: string) => void;
}

const nodeTypeStyles: Record<string, { border: string; bg: string; icon: any; color: string }> = {
  trigger: { border: "border-amber-500/40", bg: "bg-amber-500/10", icon: Zap, color: "text-amber-400" },
  action: { border: "border-sky-500/40", bg: "bg-sky-500/10", icon: Play, color: "text-sky-400" },
  approval: { border: "border-purple-500/40", bg: "bg-purple-500/10", icon: UserCheck, color: "text-purple-400" },
  ai: { border: "border-emerald-500/40", bg: "bg-emerald-500/10", icon: Sparkles, color: "text-emerald-400" },
  condition: { border: "border-pink-500/40", bg: "bg-pink-500/10", icon: AlertTriangle, color: "text-pink-400" },
};

export default function WorkflowCanvas({ nodes, edges, selectedNodeId, onSelectNode }: WorkflowCanvasProps) {
  return (
    <div className="relative h-[550px] w-full rounded-xl border border-white/10 bg-slate-950/90 overflow-hidden shadow-2xl p-6 select-none">
      {/* Grid Pattern Background */}
      <div
        className="absolute inset-0 opacity-15 pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.2) 1px, transparent 0)",
          backgroundSize: "24px 24px",
        }}
      />

      <div className="absolute top-4 left-4 z-10 flex items-center gap-2">
        <Badge variant="outline" className="text-[10px] border-white/10 bg-background/80 backdrop-blur-md font-mono text-muted-foreground">
          Interactive DAG Canvas ({nodes.length} Nodes · {edges.length} Transitions)
        </Badge>
      </div>

      {/* Nodes Render Flow */}
      <div className="relative z-10 flex flex-wrap items-center gap-6 pt-10">
        {nodes.map((node, index) => {
          const style = nodeTypeStyles[node.type] || nodeTypeStyles.action;
          const Icon = style.icon;
          const isSelected = selectedNodeId === node.id;

          return (
            <React.Fragment key={node.id}>
              <div
                onClick={() => onSelectNode(node.id)}
                className={cn(
                  "relative flex flex-col rounded-xl border p-4 shadow-xl transition-all cursor-pointer w-64 backdrop-blur-md",
                  style.border,
                  style.bg,
                  isSelected && "ring-2 ring-brand-blue shadow-brand-blue/20 scale-105"
                )}
              >
                <div className="flex items-center justify-between pb-2 border-b border-white/10">
                  <span className={cn("text-xs font-mono font-bold uppercase tracking-wider flex items-center gap-1.5", style.color)}>
                    <Icon className="h-3.5 w-3.5" /> {node.type}
                  </span>
                  <Badge variant="outline" className="text-[9px] font-mono border-white/10">
                    #{index + 1}
                  </Badge>
                </div>
                <div className="pt-2">
                  <h4 className="text-xs font-semibold text-foreground leading-snug">{node.label}</h4>
                  <p className="text-[10px] text-muted-foreground mt-1 font-mono truncate">
                    {node.config?.action_type || node.config?.alert_name || "Configured"}
                  </p>
                </div>
              </div>

              {index < nodes.length - 1 && (
                <div className="flex items-center text-muted-foreground/60 animate-pulse">
                  <ArrowRight className="h-5 w-5" />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
