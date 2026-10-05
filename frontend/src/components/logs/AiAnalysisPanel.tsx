import React, { useState } from "react";
import {
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Copy,
  Check,
  Download,
  ShieldCheck,
  Wrench,
  BrainCircuit,
  Loader2,
  Info,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { exportAnalysisToPdf } from "@/lib/pdfExport";
import type { LogAnalysis } from "@/types/log_analysis";
import { cn } from "@/lib/utils";

interface AiAnalysisPanelProps {
  analysis: LogAnalysis | null;
  isLoading?: boolean;
}

const severityBadges: Record<string, { label: string; badgeVariant: "danger" | "warning" | "info" | "muted"; color: string }> = {
  critical: { label: "CRITICAL", badgeVariant: "danger", color: "text-rose-400 bg-rose-500/10 border-rose-500/30" },
  high:     { label: "HIGH", badgeVariant: "danger", color: "text-orange-400 bg-orange-500/10 border-orange-500/30" },
  medium:   { label: "MEDIUM", badgeVariant: "warning", color: "text-amber-400 bg-amber-500/10 border-amber-500/30" },
  low:      { label: "LOW", badgeVariant: "info", color: "text-sky-400 bg-sky-500/10 border-sky-500/30" },
};

export default function AiAnalysisPanel({ analysis, isLoading }: AiAnalysisPanelProps) {
  const [copied, setCopied] = useState(false);

  if (isLoading || (analysis && analysis.status === "analyzing")) {
    return (
      <Card className="border-brand-blue/20 bg-card/60 backdrop-blur-md relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-brand-blue/5 to-transparent animate-pulse" />
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2 text-brand-blue">
            <Sparkles className="w-5 h-5 animate-spin" />
            <CardTitle className="text-base font-semibold">Google Gemini AI Analysis in Progress…</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 rounded-lg bg-white/[0.02] border border-white/[0.06] space-y-3">
            <div className="h-4 bg-white/10 rounded w-3/4 animate-pulse" />
            <div className="h-4 bg-white/10 rounded w-5/6 animate-pulse" />
            <div className="h-4 bg-white/10 rounded w-2/3 animate-pulse" />
          </div>
          <div className="flex items-center justify-center py-6 gap-3 text-sm text-muted-foreground">
            <Loader2 className="w-4 h-4 animate-spin text-brand-blue" />
            <span>Analyzing log traces, identifying error signatures & formulating root cause…</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!analysis) {
    return (
      <Card className="border-dashed border-white/10 bg-card/40">
        <CardContent className="py-12 text-center text-muted-foreground space-y-2">
          <BrainCircuit className="w-8 h-8 mx-auto text-muted-foreground/40" />
          <p className="text-sm font-medium">No Log File Selected for Analysis</p>
          <p className="text-xs text-muted-foreground/80 max-w-sm mx-auto">
            Upload a server log file above or pick a historical log analysis from the sidebar to inspect AI insights.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (analysis.status === "error") {
    return (
      <Card className="border-rose-500/30 bg-rose-500/5">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2 text-rose-400">
            <AlertTriangle className="w-5 h-5" />
            <CardTitle className="text-base font-semibold">AI Analysis Error</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="text-xs text-rose-300 font-mono bg-black/30 p-3 rounded-lg border border-rose-500/20">
          {analysis.ai_error || "An unexpected error occurred while analyzing the log file."}
        </CardContent>
      </Card>
    );
  }

  const severityKey = (analysis.severity || "low").toLowerCase();
  const sevConfig = severityBadges[severityKey] || severityBadges.low;
  const confidencePercent = Math.round((analysis.confidence_score || 0) * 100);

  const handleCopy = () => {
    const textToCopy = `
CloudPulse AI Log Analysis Report
File: ${analysis.filename}
Severity: ${analysis.severity?.toUpperCase() || "UNKNOWN"}
Confidence: ${confidencePercent}%

[EXECUTIVE SUMMARY]
${analysis.executive_summary || "N/A"}

[ROOT CAUSE ANALYSIS]
${analysis.root_cause || "N/A"}

[RECOMMENDED FIXES]
${analysis.recommended_fixes || "N/A"}

[PREVENTIVE MEASURES]
${analysis.preventive_measures || "N/A"}
    `.trim();

    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className="border-brand-blue/20 bg-card/80 backdrop-blur-md space-y-0">
      <CardHeader className="pb-4 border-b border-white/[0.06]">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-brand-gradient text-white shadow-lg shadow-brand-blue/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <CardTitle className="text-base font-bold flex items-center gap-2">
                AI Root Cause Analysis
                <span className="text-xs font-normal text-muted-foreground font-mono">({analysis.filename})</span>
              </CardTitle>
              <p className="text-xs text-muted-foreground">Powered by Google Gemini 3.6 SRE Engine</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              className="gap-1.5 text-xs h-8 bg-bg-elevated border-white/[0.08] hover:bg-white/[0.08]"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? "Copied" : "Copy AI Response"}</span>
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => exportAnalysisToPdf(analysis)}
              className="gap-1.5 text-xs h-8 bg-brand-blue/10 border-brand-blue/30 text-brand-blue hover:bg-brand-blue/20"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PDF</span>
            </Button>
          </div>
        </div>

        {/* Severity & Confidence Summary Row */}
        <div className="mt-4 pt-3 border-t border-white/[0.04] grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.04]">
            <span className="text-[10px] uppercase tracking-wider text-muted-foreground block">Severity Level</span>
            <div className="mt-1">
              <Badge variant={sevConfig.badgeVariant} className={cn("text-xs px-2.5 py-0.5", sevConfig.color)}>
                {sevConfig.label}
              </Badge>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.04]">
            <span className="text-[10px] uppercase tracking-wider text-muted-foreground block">AI Confidence Score</span>
            <div className="mt-1 flex items-center gap-1.5 font-semibold text-sm">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>{confidencePercent}%</span>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.04]">
            <span className="text-[10px] uppercase tracking-wider text-muted-foreground block">Total Error Traces</span>
            <div className="mt-1 font-semibold text-sm text-rose-400 font-mono">
              {analysis.error_count + analysis.critical_count} <span className="text-xs text-muted-foreground font-sans">entries</span>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-white/[0.02] border border-white/[0.04]">
            <span className="text-[10px] uppercase tracking-wider text-muted-foreground block">Log Lines Scanned</span>
            <div className="mt-1 font-semibold text-sm font-mono">
              {analysis.total_lines} <span className="text-xs text-muted-foreground font-sans">lines</span>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-4 space-y-5">
        {/* Executive Summary */}
        <div className="space-y-1.5">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-brand-blue flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5" />
            Executive Summary
          </h4>
          <div className="p-3.5 rounded-lg bg-brand-blue/5 border border-brand-blue/15 text-sm leading-relaxed text-foreground/90">
            {analysis.executive_summary || "No executive summary available."}
          </div>
        </div>

        {/* Root Cause */}
        <div className="space-y-1.5">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" />
            Root Cause Analysis
          </h4>
          <div className="p-3.5 rounded-lg bg-rose-500/5 border border-rose-500/20 text-sm leading-relaxed text-rose-200 font-mono text-xs whitespace-pre-wrap">
            {analysis.root_cause || "No root cause explanation generated."}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Recommended Fixes */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <Wrench className="w-3.5 h-3.5" />
              Recommended Fixes
            </h4>
            <div className="p-3.5 rounded-lg bg-emerald-500/5 border border-emerald-500/20 text-xs leading-relaxed text-emerald-200 whitespace-pre-wrap">
              {analysis.recommended_fixes || "No recommended fixes available."}
            </div>
          </div>

          {/* Preventive Measures */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-sky-400 flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Preventive Measures
            </h4>
            <div className="p-3.5 rounded-lg bg-sky-500/5 border border-sky-500/20 text-xs leading-relaxed text-sky-200 whitespace-pre-wrap">
              {analysis.preventive_measures || "No preventive measures available."}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
