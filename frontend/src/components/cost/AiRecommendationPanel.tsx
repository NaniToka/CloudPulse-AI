import React from "react";
import {
  Sparkles,
  Zap,
  Layers,
  AlertTriangle,
  Flame,
  CheckCircle2,
  Calendar,
  Sliders,
  Loader2,
  BrainCircuit,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { CostAnalyzeResponse } from "@/types/cost";

interface AiRecommendationPanelProps {
  analysis: CostAnalyzeResponse | null;
  onAnalyze: () => Promise<void>;
  isAnalyzing: boolean;
}

export default function AiRecommendationPanel({
  analysis,
  onAnalyze,
  isAnalyzing,
}: AiRecommendationPanelProps) {
  return (
    <Card className="border-brand-blue/20 bg-card/80 backdrop-blur-md relative overflow-hidden">
      <CardHeader className="pb-4 border-b border-white/[0.06]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-brand-gradient text-white shadow-lg shadow-brand-blue/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <CardTitle className="text-base font-bold">FinOps AI Cloud Cost Analysis</CardTitle>
              <p className="text-xs text-muted-foreground">Powered by Google Gemini 3.6 Cost Optimization Engine</p>
            </div>
          </div>

          <Button
            size="sm"
            onClick={onAnalyze}
            disabled={isAnalyzing}
            className="gap-2 bg-brand-gradient text-white hover:opacity-90 transition-opacity"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Analyzing Cloud Costs…</span>
              </>
            ) : (
              <>
                <BrainCircuit className="w-4 h-4" />
                <span>Run AI Cost Analysis</span>
              </>
            )}
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-4 space-y-5">
        {/* Executive Cost Summary */}
        <div className="space-y-1.5">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-brand-blue flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5" />
            Cost Summary & Insights
          </h4>
          <div className="p-3.5 rounded-lg bg-brand-blue/5 border border-brand-blue/15 text-sm leading-relaxed text-foreground/90">
            {analysis?.cost_summary ||
              "Run AI Cost Analysis to generate an executive spending diagnosis and cloud savings roadmap."}
          </div>
        </div>

        {analysis && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Highest Cost Services */}
            <div className="space-y-1.5">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5" />
                Highest Cost Drivers
              </h4>
              <ul className="p-3.5 rounded-lg bg-purple-500/5 border border-purple-500/15 text-xs space-y-2 text-purple-200">
                {analysis.highest_cost_services.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-purple-400 font-bold">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Idle & Wasted Resources */}
            <div className="space-y-1.5">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
                <Flame className="w-3.5 h-3.5" />
                Idle & Wasted Resources
              </h4>
              <ul className="p-3.5 rounded-lg bg-rose-500/5 border border-rose-500/15 text-xs space-y-2 text-rose-200">
                {[...analysis.idle_resources, ...analysis.wasted_resources].map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Reserved Instance Recommendations */}
            <div className="space-y-1.5">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5" />
                Committed Use / Reserved Instances
              </h4>
              <ul className="p-3.5 rounded-lg bg-emerald-500/5 border border-emerald-500/15 text-xs space-y-2 text-emerald-200">
                {analysis.reserved_instance_recommendations.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Auto Scaling Recommendations */}
            <div className="space-y-1.5">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-sky-400 flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5" />
                Auto Scaling & Elasticity
              </h4>
              <ul className="p-3.5 rounded-lg bg-sky-500/5 border border-sky-500/15 text-xs space-y-2 text-sky-200">
                {analysis.auto_scaling_recommendations.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-sky-400 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
