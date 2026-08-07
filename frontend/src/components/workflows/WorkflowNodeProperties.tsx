import React from "react";
import { Settings, Zap, Play, UserCheck, Sparkles, X, ShieldAlert, Cpu } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface WorkflowNodePropertiesProps {
  node: {
    id: string;
    type: string;
    label: string;
    config?: Record<string, any>;
  } | null;
  onClose: () => void;
}

export default function WorkflowNodeProperties({ node, onClose }: WorkflowNodePropertiesProps) {
  if (!node) return null;

  return (
    <div className="w-80 rounded-xl border border-white/10 bg-slate-950 p-5 shadow-2xl space-y-5 text-xs">
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <h4 className="font-semibold text-foreground flex items-center gap-1.5 font-mono">
          <Settings className="h-4 w-4 text-sky-400" />
          Node Properties
        </h4>
        <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
          <X className="h-3.5 w-3.5" />
        </button>
      </div>

      <div className="space-y-3">
        <div>
          <label className="text-[10px] text-muted-foreground uppercase font-mono">Node Label</label>
          <Input defaultValue={node.label} className="h-8 text-xs mt-1" />
        </div>

        <div>
          <label className="text-[10px] text-muted-foreground uppercase font-mono">Node Type</label>
          <div className="mt-1">
            <Badge variant="outline" className="text-xs font-mono uppercase text-sky-400 border-sky-500/30">
              {node.type}
            </Badge>
          </div>
        </div>

        <div>
          <label className="text-[10px] text-muted-foreground uppercase font-mono">Retry Policy</label>
          <select className="mt-1 w-full rounded-md border border-white/10 bg-background px-2 py-1.5 text-xs text-foreground font-mono">
            <option value="exponential">Exponential Backoff (3 retries)</option>
            <option value="linear">Linear (2 retries)</option>
            <option value="none">No Retries</option>
          </select>
        </div>

        <div>
          <label className="text-[10px] text-muted-foreground uppercase font-mono">Timeout</label>
          <Input defaultValue="300s" className="h-8 text-xs font-mono mt-1" />
        </div>

        {node.type === "approval" && (
          <div>
            <label className="text-[10px] text-muted-foreground uppercase font-mono">Required Role</label>
            <Input defaultValue="sre-admin" className="h-8 text-xs font-mono mt-1" />
          </div>
        )}
      </div>
    </div>
  );
}
