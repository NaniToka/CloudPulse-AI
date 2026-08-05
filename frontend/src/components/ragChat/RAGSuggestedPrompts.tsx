/**
 * RAG Suggested Prompts Component — Displays interactive quick question chips.
 */

import React from "react";
import { Sparkles, Activity, AlertTriangle, DollarSign, Clock, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";

interface RAGSuggestedPromptsProps {
  onSelectPrompt: (prompt: string) => void;
  disabled?: boolean;
}

const prompts = [
  { icon: Activity, text: "Why is CPU high on api-gateway?", category: "Metrics" },
  { icon: AlertTriangle, text: "Show all incidents this week.", category: "Incidents" },
  { icon: Clock, text: "Which service causes the highest latency?", category: "Traces" },
  { icon: DollarSign, text: "Which cloud resource costs the most?", category: "FinOps" },
  { icon: ShieldCheck, text: "Summarize today's infrastructure health.", category: "Health" },
];

export const RAGSuggestedPrompts: React.FC<RAGSuggestedPromptsProps> = ({
  onSelectPrompt,
  disabled,
}) => {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-mono">
        <Sparkles className="h-3.5 w-3.5 text-brand-purple" />
        <span>Suggested Infrastructure Prompts:</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {prompts.map((p, idx) => {
          const IconComp = p.icon;
          return (
            <button
              key={idx}
              disabled={disabled}
              onClick={() => onSelectPrompt(p.text)}
              className="px-3 py-1.5 rounded-full bg-bg-surface hover:bg-bg-elevated border border-white/10 text-xs text-foreground hover:text-brand-purple transition-all duration-150 flex items-center gap-2 group shadow-sm disabled:opacity-50"
            >
              <IconComp className="h-3.5 w-3.5 text-muted-foreground group-hover:text-brand-purple transition-colors" />
              <span>{p.text}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
