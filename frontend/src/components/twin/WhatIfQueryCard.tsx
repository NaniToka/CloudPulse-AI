import React, { useState } from "react";
import { Sparkles, ArrowRight, Loader2, ShieldCheck, DollarSign, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useDigitalTwinMutations } from "@/hooks/useDigitalTwin";
import type { WhatIfResponseItem } from "@/services/twinService";

const SUGGESTED_QUERIES = [
  "What happens if region us-east-1 goes offline?",
  "What happens if Redis primary cache fails?",
  "What if traffic increases by 400% during a flash sale?",
  "What if PostgreSQL connection latency doubles?",
];

export default function WhatIfQueryCard() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<WhatIfResponseItem | null>(null);
  const { askWhatIf, isAskingWhatIf } = useDigitalTwinMutations();

  const handleAsk = async (promptText: string) => {
    if (!promptText) return;
    try {
      const res = await askWhatIf(promptText);
      setResult(res);
    } catch (e) {
      alert("Failed to analyze What-If scenario");
    }
  };

  return (
    <div className="rounded-xl border border-purple-500/30 bg-purple-500/[0.03] p-5 shadow-2xl space-y-4">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-purple-400" />
        <h4 className="text-sm font-semibold text-foreground font-mono">
          Gemini AI "What-If" Infrastructure Synthesizer
        </h4>
      </div>

      <div className="flex gap-2">
        <Input
          placeholder="Ask any chaos hypothesis (e.g. 'What if PostgreSQL connection pool saturates?')..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk(query)}
          className="text-xs h-9 bg-background/80"
        />
        <Button
          size="sm"
          onClick={() => handleAsk(query)}
          disabled={isAskingWhatIf || !query}
          className="bg-purple-600 hover:bg-purple-700 text-white text-xs gap-1.5 shrink-0"
        >
          {isAskingWhatIf ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <ArrowRight className="h-3.5 w-3.5" />}
          Synthesize
        </Button>
      </div>

      {/* Suggested prompts */}
      <div className="flex items-center gap-1.5 flex-wrap">
        <span className="text-[10px] text-muted-foreground font-mono uppercase font-bold">Suggested:</span>
        {SUGGESTED_QUERIES.map((q, idx) => (
          <button
            key={idx}
            onClick={() => {
              setQuery(q);
              handleAsk(q);
            }}
            className="rounded border border-white/10 bg-white/[0.02] px-2 py-0.5 text-[10px] text-purple-300 hover:border-purple-500/40 hover:bg-purple-500/10 transition-all font-mono"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Result Card */}
      {result && (
        <div className="rounded-lg border border-purple-500/40 bg-background/90 p-4 space-y-3 text-xs mt-3 animate-in fade-in">
          <div className="flex items-center justify-between border-b border-white/10 pb-2">
            <span className="font-mono font-bold text-foreground">{result.query_text}</span>
            <Badge variant="danger" className="text-[9px] font-mono">
              RISK: {result.predicted_risk_level} · {result.financial_risk_estimate}
            </Badge>
          </div>

          <p className="text-muted-foreground leading-relaxed">{result.impact_summary}</p>

          <div className="space-y-1">
            <span className="text-[10px] text-muted-foreground font-mono uppercase font-bold">Preventive Mitigations:</span>
            <ul className="list-disc list-inside text-emerald-400 space-y-0.5">
              {result.mitigations?.map((m, idx) => (
                <li key={idx}>{m}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
