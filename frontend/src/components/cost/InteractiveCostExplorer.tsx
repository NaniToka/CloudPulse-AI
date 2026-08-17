import React, { useState } from "react";
import { ChevronRight, ChevronDown, Folder, Server, Globe, Layers, DollarSign } from "lucide-react";
import type { CostExplorerResponse, CostExplorerNode } from "@/types/cost";

interface InteractiveCostExplorerProps {
  explorer: CostExplorerResponse | null;
}

export default function InteractiveCostExplorer({ explorer }: InteractiveCostExplorerProps) {
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({});

  if (!explorer || !explorer.nodes || explorer.nodes.length === 0) return null;

  const toggleNode = (nodeId: string) => {
    setExpandedNodes((prev) => ({
      ...prev,
      [nodeId]: !prev[nodeId],
    }));
  };

  const renderNode = (node: CostExplorerNode, depth = 0) => {
    const isExpanded = !!expandedNodes[node.id];
    const hasChildren = node.children && node.children.length > 0;

    const getIcon = (level: string) => {
      switch (level) {
        case "provider":
          return <Globe className="w-3.5 h-3.5 text-brand-blue" />;
        case "service":
          return <Layers className="w-3.5 h-3.5 text-purple-400" />;
        case "region":
          return <Folder className="w-3.5 h-3.5 text-emerald-400" />;
        default:
          return <Server className="w-3.5 h-3.5 text-amber-400" />;
      }
    };

    return (
      <div key={node.id} className="space-y-1">
        <div
          onClick={() => hasChildren && toggleNode(node.id)}
          className={`flex items-center justify-between p-2 rounded-lg border border-white/[0.04] transition-colors ${
            hasChildren ? "cursor-pointer hover:bg-white/5" : "bg-slate-900/30"
          }`}
          style={{ paddingLeft: `${depth * 1.25 + 0.5}rem` }}
        >
          <div className="flex items-center gap-2 font-mono text-xs text-foreground">
            {hasChildren ? (
              isExpanded ? (
                <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
              ) : (
                <ChevronRight className="w-3.5 h-3.5 text-muted-foreground" />
              )
            ) : (
              <span className="w-3.5 h-3.5 inline-block" />
            )}
            {getIcon(node.level)}
            <span className="font-semibold">{node.name}</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-white/5 text-muted-foreground uppercase">{node.level}</span>
          </div>

          <div className="flex items-center gap-4 font-mono text-xs">
            <span className="text-muted-foreground text-[11px]">{node.resource_count} resource(s)</span>
            <span className="text-brand-blue text-[11px] font-semibold">{node.percentage_of_total}% of total</span>
            <span className="font-bold text-foreground">${node.cost.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
          </div>
        </div>

        {isExpanded && hasChildren && (
          <div className="space-y-1">
            {node.children!.map((child) => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-5 rounded-xl border border-white/[0.08] bg-bg-surface space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-brand-blue" />
          <h3 className="text-sm font-semibold text-foreground">Interactive Cost Explorer</h3>
        </div>
        <span className="text-xs text-muted-foreground font-mono">
          Drill Down: Provider → Service → Region → Resource (Total: ${explorer.total_cost.toLocaleString()})
        </span>
      </div>

      <div className="space-y-1 max-h-[450px] overflow-y-auto pr-1">
        {explorer.nodes.map((node) => renderNode(node, 0))}
      </div>
    </div>
  );
}
