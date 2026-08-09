/**
 * RAG Chat Message Component — Displays question, answer, evidence citations, & followups.
 */

import React, { useState } from "react";
import {
  Sparkles,
  User,
  ShieldCheck,
  FileText,
  Copy,
  Check,
  AlertTriangle,
  Activity,
  Zap,
  ArrowRight,
  Database,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { RAGQueryResponse } from "@/types/ragChat";

interface RAGChatMessageProps {
  message: RAGQueryResponse;
  onSelectFollowup?: (prompt: string) => void;
}

const collectionBadgeMap: Record<string, string> = {
  logs: "bg-blue-950/40 text-blue-400 border-blue-500/30",
  incidents: "bg-red-950/40 text-red-400 border-red-500/30",
  metrics: "bg-amber-950/40 text-amber-400 border-amber-500/30",
  alerts: "bg-orange-950/40 text-orange-400 border-orange-500/30",
  traces: "bg-purple-950/40 text-purple-400 border-purple-500/30",
  ai_reports: "bg-emerald-950/40 text-emerald-400 border-emerald-500/30",
};

export const RAGChatMessage: React.FC<RAGChatMessageProps> = ({
  message,
  onSelectFollowup,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4 my-4 font-sans text-xs">
      {/* User Question */}
      <div className="flex justify-end">
        <div className="max-w-xl bg-brand-purple/20 border border-brand-purple/30 rounded-2xl rounded-tr-none px-4 py-3 text-foreground font-medium shadow-md flex items-start gap-2.5">
          <div className="flex-1">{message.question}</div>
          <User className="h-4 w-4 text-brand-purple shrink-0 mt-0.5" />
        </div>
      </div>

      {/* Assistant AI Answer */}
      <div className="flex justify-start">
        <div className="w-full max-w-3xl bg-bg-surface/90 border border-white/10 rounded-2xl rounded-tl-none p-5 space-y-4 shadow-xl">
          {/* Answer Header */}
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <div className="flex items-center gap-2 flex-wrap">
              <div className="h-6 w-6 rounded-lg bg-brand-purple/20 flex items-center justify-center text-brand-purple">
                <Sparkles className="h-3.5 w-3.5" />
              </div>
              <span className="font-bold text-foreground">CloudPulse AI Assistant</span>
              <span className="text-muted-foreground">•</span>
              <Badge
                variant="outline"
                className={`text-[10px] uppercase font-mono px-1.5 py-0.5 ${
                  message.provider?.includes("LIVE")
                    ? "bg-emerald-950/40 text-emerald-400 border-emerald-500/40"
                    : "bg-brand-blue/20 text-brand-blue border-brand-blue/30"
                }`}
              >
                {message.provider || "LOCAL DEMO AI"}
              </Badge>
              <span className="text-muted-foreground">•</span>
              <span className="text-emerald-400 font-mono text-[11px] flex items-center gap-1">
                <ShieldCheck className="h-3.5 w-3.5" /> RAG Confidence: {Math.round(message.confidence_score * 100)}%
              </span>
            </div>


            <button
              onClick={handleCopy}
              className="px-2 py-1 rounded text-muted-foreground hover:text-foreground hover:bg-white/10 transition-colors flex items-center gap-1 text-[11px]"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </button>
          </div>

          {/* Answer Body */}
          <div className="prose prose-invert max-w-none text-foreground leading-relaxed text-xs space-y-2 whitespace-pre-wrap font-sans">
            {message.answer}
          </div>

          {/* Evidence Source Citations */}
          {message.evidence_sources && message.evidence_sources.length > 0 && (
            <div className="pt-3 border-t border-white/10 space-y-2">
              <div className="flex items-center gap-1.5 text-muted-foreground font-mono text-[11px]">
                <FileText className="h-3.5 w-3.5 text-brand-purple" />
                <span>Retrieved Vector Evidence Sources ({message.evidence_sources.length}):</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {message.evidence_sources.map((src, i) => (
                  <div
                    key={i}
                    className="p-2.5 rounded-lg bg-bg-elevated/40 border border-white/5 space-y-1 text-[11px] font-mono"
                  >
                    <div className="flex items-center justify-between">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold border ${collectionBadgeMap[src.collection] || 'bg-white/10'}`}>
                        {src.collection}
                      </span>
                      <span className="text-emerald-400 text-[10px]">Match: {Math.round(src.relevance_score * 100)}%</span>
                    </div>
                    <p className="text-foreground truncate font-semibold">{src.title}</p>
                    <p className="text-muted-foreground line-clamp-2 text-[10px]">{src.snippet}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Actions */}
          {message.recommended_actions && message.recommended_actions.length > 0 && (
            <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/30 space-y-1.5">
              <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                <Zap className="h-3.5 w-3.5" /> Recommended Remediation Actions
              </div>
              <ul className="list-disc list-inside text-foreground font-mono text-[11px] space-y-1">
                {message.recommended_actions.map((act, idx) => (
                  <li key={idx}>{act}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggested Followup Questions */}
          {message.suggested_followup_questions && message.suggested_followup_questions.length > 0 && (
            <div className="pt-3 border-t border-white/10 space-y-2">
              <span className="text-muted-foreground text-[11px] font-mono">Suggested Follow-ups:</span>
              <div className="flex flex-wrap gap-2">
                {message.suggested_followup_questions.map((fq, i) => (
                  <button
                    key={i}
                    onClick={() => onSelectFollowup && onSelectFollowup(fq)}
                    className="px-2.5 py-1 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-brand-purple hover:text-white text-[11px] flex items-center gap-1 transition-all"
                  >
                    <span>{fq}</span>
                    <ArrowRight className="h-3 w-3" />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
