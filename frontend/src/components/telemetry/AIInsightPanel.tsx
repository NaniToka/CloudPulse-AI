import React from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BrainCircuit, AlertTriangle, CheckCircle2 } from "lucide-react";
import { AIOperationalSummaryItem } from "@/services/telemetryService";

interface AIInsightPanelProps {
  summary: AIOperationalSummaryItem | undefined;
  isLoading: boolean;
}

export const AIInsightPanel: React.FC<AIInsightPanelProps> = ({ summary, isLoading }) => {
  if (isLoading) {
    return (
      <Card className="col-span-full border-indigo-500/20 bg-indigo-500/5">
        <CardHeader>
          <CardTitle className="text-indigo-400 flex items-center">
            <BrainCircuit className="w-5 h-5 mr-2 animate-pulse" />
            AI Generating Operational Summary...
          </CardTitle>
        </CardHeader>
        <CardContent className="h-32 flex items-center justify-center">
          <div className="flex space-x-2">
            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-75" />
            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-150" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!summary) {
    return null;
  }

  return (
    <Card className="col-span-full border-indigo-500/30 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 shadow-lg">
      <CardHeader className="pb-3 border-b border-indigo-500/10">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg font-bold text-indigo-400 flex items-center">
              <BrainCircuit className="w-5 h-5 mr-2" />
              AI Operational Summary
            </CardTitle>
            <CardDescription className="text-indigo-200/70 mt-1">
              Cross-pipeline intelligent correlation engine
            </CardDescription>
          </div>
          <div className="bg-indigo-500/20 text-indigo-300 text-xs px-2 py-1 rounded flex items-center">
            <CheckCircle2 className="w-3 h-3 mr-1" />
            {(summary.confidence_score * 100).toFixed(0)}% Confidence
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center">
            <AlertTriangle className="w-4 h-4 mr-2 text-yellow-500" />
            Root Cause Analysis
          </h4>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {summary.root_cause_analysis}
          </p>
          <div className="mt-4">
            <h5 className="text-xs font-semibold text-foreground mb-2">Impacted Services</h5>
            <div className="flex flex-wrap gap-2">
              {summary.impacted_services.map((service) => (
                <span key={service} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-1 rounded">
                  {service}
                </span>
              ))}
            </div>
          </div>
        </div>
        
        <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-800">
          <h4 className="text-sm font-semibold text-foreground mb-2">Recommended Mitigations</h4>
          <ul className="space-y-2">
            {summary.recommended_mitigations.map((mitigation, idx) => (
              <li key={idx} className="text-sm text-muted-foreground flex items-start">
                <span className="text-indigo-400 mr-2">•</span>
                {mitigation}
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};
