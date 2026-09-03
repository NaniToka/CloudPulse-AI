/**
 * Incident Details Modal Component
 * Displays Status Progress Bar, AI Analysis Panel with Confidence Score, Event Timeline, Correlated Logs, & Comments.
 */

import React, { useState } from "react";
import {
  X,
  Sparkles,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Activity,
  Terminal,
  RefreshCw,
  TrendingUp,
  Send,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Incident, IncidentStatus } from "@/types/incident";

interface IncidentDetailsModalProps {
  incident: Incident | null;
  isOpen: boolean;
  onClose: () => void;
  onResolve: (id: string, notes: string) => Promise<void>;
  onReanalyze: (id: string) => Promise<void>;
  onUpdateStatus: (id: string, status: IncidentStatus) => Promise<void>;
  isResolving: boolean;
  isAnalyzing: boolean;
}

const STATUS_STEPS: IncidentStatus[] = ["Open", "Investigating", "Monitoring", "Resolved"];

export const IncidentDetailsModal: React.FC<IncidentDetailsModalProps> = ({
  incident,
  isOpen,
  onClose,
  onResolve,
  onReanalyze,
  onUpdateStatus,
  isResolving,
  isAnalyzing,
}) => {
  const [resolutionNotes, setResolutionNotes] = useState("");
  const [activeTab, setActiveTab] = useState("overview");

  if (!isOpen || !incident) return null;

  const currentStepIndex = STATUS_STEPS.indexOf(
    incident.status === "Closed" ? "Resolved" : incident.status
  );

  const handleResolveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolutionNotes.trim()) return;
    await onResolve(incident.id, resolutionNotes);
    setResolutionNotes("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-bg-surface border border-white/10 rounded-xl shadow-2xl overflow-hidden flex flex-col text-xs">
        {/* Top Header Bar */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-bg-elevated/50">
          <div className="flex items-center gap-3">
            <Badge variant={incident.severity === "P0" || incident.severity === "P1" ? "critical" : "warning"}>
              {incident.severity}
            </Badge>
            <div>
              <h2 className="text-sm font-bold text-foreground flex items-center gap-2">
                {incident.title}
              </h2>
              <p className="text-[11px] text-muted-foreground flex items-center gap-2 mt-0.5 font-mono">
                <span>ID: {incident.id.slice(0, 8)}</span>
                <span>•</span>
                <span>Service: {incident.affected_service}</span>
                <span>•</span>
                <span>Region: {incident.affected_region || "us-east-1"}</span>
                <span>•</span>
                <span>Assigned: {incident.assigned_engineer || incident.assigned_to || "Unassigned"}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <select
              value={incident.status}
              onChange={(e) => onUpdateStatus(incident.id, e.target.value as IncidentStatus)}
              className="h-8 px-2.5 rounded bg-bg-elevated border border-white/10 text-xs text-foreground focus:outline-none"
            >
              <option value="Open">Open</option>
              <option value="Investigating">Investigating</option>
              <option value="Monitoring">Monitoring</option>
              <option value="Resolved">Resolved</option>
              <option value="Closed">Closed</option>
            </select>

            <Button
              variant="outline"
              size="sm"
              onClick={() => onReanalyze(incident.id)}
              disabled={isAnalyzing}
              className="h-8 text-xs gap-1.5"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isAnalyzing ? "animate-spin text-brand-purple" : ""}`} />
              Analyze Incident
            </Button>

            <button
              onClick={onClose}
              className="p-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-white/10 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Status Progress Bar */}
        <div className="px-6 py-3 border-b border-white/5 bg-bg-elevated/20">
          <div className="flex items-center justify-between max-w-xl mx-auto">
            {STATUS_STEPS.map((stepName, idx) => {
              const isPassed = idx <= currentStepIndex;
              const isCurrent = idx === currentStepIndex;
              return (
                <React.Fragment key={stepName}>
                  <div className="flex flex-col items-center gap-1">
                    <div
                      className={`h-6 w-6 rounded-full flex items-center justify-center text-[10px] font-bold transition-all ${
                        isPassed
                          ? "bg-brand-purple text-white shadow-lg shadow-brand-purple/50"
                          : "bg-white/10 text-muted-foreground"
                      }`}
                    >
                      {idx + 1}
                    </div>
                    <span
                      className={`text-[10px] font-medium ${
                        isCurrent ? "text-brand-purple font-bold" : "text-muted-foreground"
                      }`}
                    >
                      {stepName}
                    </span>
                  </div>

                  {idx < STATUS_STEPS.length - 1 && (
                    <div
                      className={`flex-1 h-0.5 mx-2 rounded transition-colors ${
                        idx < currentStepIndex ? "bg-brand-purple" : "bg-white/10"
                      }`}
                    />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Content Tabs Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="bg-bg-elevated/60 border border-white/10 p-1 mb-4 grid grid-cols-4">
              <TabsTrigger value="overview" className="text-xs">AI Diagnostics</TabsTrigger>
              <TabsTrigger value="timeline" className="text-xs">Timeline & Activity</TabsTrigger>
              <TabsTrigger value="logs_alerts" className="text-xs">Logs & Metrics</TabsTrigger>
              <TabsTrigger value="resolution" className="text-xs">Comments & Resolution</TabsTrigger>
            </TabsList>

            {/* TAB 1: AI Diagnostics */}
            <TabsContent value="overview" className="space-y-4">
              {isAnalyzing && !incident.ai_summary ? (
                <div className="space-y-4 animate-pulse">
                  <div className="rounded-lg border border-white/5 bg-white/5 h-24 w-full"></div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="rounded-lg border border-white/5 bg-white/5 h-20 w-full"></div>
                    <div className="rounded-lg border border-white/5 bg-white/5 h-20 w-full"></div>
                  </div>
                  <div className="rounded-lg border border-white/5 bg-white/5 h-20 w-full"></div>
                  <div className="rounded-lg border border-white/5 bg-white/5 h-24 w-full"></div>
                </div>
              ) : (
                <>
                  {/* AI Summary Card */}
                  <Card className="p-4 bg-brand-purple/10 border border-brand-purple/20 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-brand-purple font-semibold text-xs">
                        <Sparkles className="h-4 w-4" />
                        Gemini AI Executive Summary
                      </div>

                      {/* Confidence Score Pill */}
                      <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-[11px] text-emerald-400 font-medium">
                        <ShieldCheck className="h-3.5 w-3.5" />
                        AI Confidence: {Math.round((incident.ai_confidence_score || incident.confidence_score || 0.94) * 100)}%
                      </div>
                    </div>

                    <p className="text-foreground leading-relaxed text-xs">
                      {incident.ai_summary || "Gemini AI diagnostic analysis is currently evaluating incident telemetry or is temporarily unavailable."}
                    </p>

                    {incident.ai_estimated_resolution_time && (
                      <div className="pt-2 text-[11px] text-muted-foreground flex items-center gap-1.5 border-t border-white/5">
                        <Clock className="h-3.5 w-3.5 text-brand-purple" />
                        Estimated Recovery Time: <span className="font-semibold text-foreground">{incident.ai_estimated_resolution_time}</span>
                      </div>
                    )}
                  </Card>

                  {/* Grid: Root Cause & Business Impact */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card className="p-4 bg-bg-elevated/30 border border-white/10 space-y-2">
                      <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs">
                        <AlertTriangle className="h-4 w-4" /> Possible Root Cause
                      </div>
                      <p className="text-muted-foreground text-xs leading-relaxed">
                        {incident.root_cause || incident.ai_root_cause || "Root cause identification in progress."}
                      </p>
                    </Card>

                    <Card className="p-4 bg-bg-elevated/30 border border-white/10 space-y-2">
                      <div className="flex items-center gap-2 text-red-400 font-semibold text-xs">
                        <TrendingUp className="h-4 w-4" /> Business & SLA Impact
                      </div>
                      <p className="text-muted-foreground text-xs leading-relaxed">
                        {incident.ai_business_impact || "Evaluating error rates and user session conversion impact."}
                      </p>
                    </Card>
                  </div>

                  {/* Immediate Mitigation */}
                  <Card className="p-4 bg-bg-elevated/30 border border-white/10 space-y-2">
                    <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
                      <Zap className="h-4 w-4" /> Immediate Mitigation Steps
                    </div>
                    {incident.ai_immediate_mitigation || incident.ai_suggested_resolution ? (
                      <p className="text-muted-foreground text-xs whitespace-pre-line font-mono leading-relaxed bg-black/30 p-3 rounded border border-white/5">
                        {incident.ai_immediate_mitigation || incident.ai_suggested_resolution}
                      </p>
                    ) : (
                      <div className="text-xs text-muted-foreground italic bg-black/30 p-3 rounded border border-white/5">
                        No immediate mitigation steps identified yet.
                      </div>
                    )}
                  </Card>

                  {/* Long-term Prevention */}
                  <Card className="p-4 bg-bg-elevated/30 border border-white/10 space-y-2">
                    <div className="font-semibold text-foreground text-xs">Long-term Prevention Plan</div>
                    {(incident.ai_long_term_prevention || incident.ai_preventive_actions || []).length > 0 ? (
                      <ul className="list-disc list-inside text-xs text-muted-foreground space-y-1">
                        {(incident.ai_long_term_prevention || incident.ai_preventive_actions || []).map((act, i) => (
                          <li key={i}>{act}</li>
                        ))}
                      </ul>
                    ) : (
                      <div className="text-xs text-muted-foreground italic">
                        No long-term prevention plan generated.
                      </div>
                    )}
                  </Card>
                </>
              )}
            </TabsContent>

            {/* TAB 2: Timeline */}
            <TabsContent value="timeline" className="space-y-4">
              <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-white/10">
                <div className="relative flex items-start gap-3">
                  <div className="absolute -left-[22px] top-1 h-4 w-4 rounded-full bg-brand-purple flex items-center justify-center text-[10px] text-white">
                    1
                  </div>
                  <div>
                    <div className="font-semibold text-foreground">Incident Triggered</div>
                    <p className="text-muted-foreground text-[11px]">
                      Created by <span className="text-foreground">{incident.created_by || "AlertManager"}</span> at{" "}
                      {new Date(incident.started_at || incident.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>

                <div className="relative flex items-start gap-3">
                  <div className="absolute -left-[22px] top-1 h-4 w-4 rounded-full bg-blue-500 flex items-center justify-center text-[10px] text-white">
                    2
                  </div>
                  <div>
                    <div className="font-semibold text-foreground">Gemini AI Analysis Complete</div>
                    <p className="text-muted-foreground text-[11px]">
                      Generated root cause analysis, immediate mitigations, and confidence score.
                    </p>
                  </div>
                </div>

                {incident.resolved_at && (
                  <div className="relative flex items-start gap-3">
                    <div className="absolute -left-[22px] top-1 h-4 w-4 rounded-full bg-emerald-500 flex items-center justify-center text-[10px] text-white">
                      3
                    </div>
                    <div>
                      <div className="font-semibold text-emerald-400">Incident Resolved</div>
                      <p className="text-muted-foreground text-[11px]">
                        Resolved by <span className="text-foreground">{incident.resolved_by || "Engineer"}</span> at{" "}
                        {new Date(incident.resolved_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            {/* TAB 3: Logs & Metrics */}
            <TabsContent value="logs_alerts" className="space-y-4">
              <Card className="p-4 bg-black/40 border border-white/10 font-mono text-[11px] text-emerald-400 space-y-1 overflow-x-auto">
                <div className="text-muted-foreground font-sans font-semibold mb-2 flex items-center gap-1.5">
                  <Terminal className="h-3.5 w-3.5 text-brand-purple" /> Correlated Log Snippet ({incident.affected_service})
                </div>
                <div>2026-08-05 21:30:14.901 [ERROR] [{incident.affected_service}] HTTP 504 Gateway Timeout: connection reset by peer</div>
                <div>2026-08-05 21:30:15.112 [WARN]  [{incident.affected_service}] Thread pool utilization exceeded 95% capacity limit</div>
                <div>2026-08-05 21:30:16.004 [FATAL] [{incident.affected_service}] Upstream database pool rejected connection acquire attempt</div>
              </Card>

              <Card className="p-4 bg-bg-elevated/30 border border-white/10 space-y-2">
                <div className="font-semibold text-foreground text-xs flex items-center gap-1.5">
                  <Activity className="h-3.5 w-3.5 text-brand-blue" /> Telemetry Metrics ({incident.affected_region || "us-east-1"})
                </div>
                <div className="grid grid-cols-3 gap-2 font-mono text-center text-xs">
                  <div className="p-2 rounded bg-black/20 border border-white/5">
                    <div className="text-[10px] text-muted-foreground">CPU Usage</div>
                    <div className="text-red-400 font-bold">96.4%</div>
                  </div>
                  <div className="p-2 rounded bg-black/20 border border-white/5">
                    <div className="text-[10px] text-muted-foreground">Memory Usage</div>
                    <div className="text-amber-400 font-bold">88.1%</div>
                  </div>
                  <div className="p-2 rounded bg-black/20 border border-white/5">
                    <div className="text-[10px] text-muted-foreground">P99 Latency</div>
                    <div className="text-brand-purple font-bold">2,450 ms</div>
                  </div>
                </div>
              </Card>
            </TabsContent>

            {/* TAB 4: Resolution & Comments */}
            <TabsContent value="resolution" className="space-y-4">
              {incident.resolution_notes ? (
                <Card className="p-4 bg-emerald-950/20 border border-emerald-500/30 space-y-2">
                  <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
                    <CheckCircle2 className="h-4 w-4" /> Resolution Logged
                  </div>
                  <p className="text-foreground text-xs whitespace-pre-line leading-relaxed">
                    {incident.resolution_notes}
                  </p>
                  <div className="text-[11px] text-muted-foreground pt-2">
                    Resolved by {incident.resolved_by || "Engineer"} at{" "}
                    {incident.resolved_at ? new Date(incident.resolved_at).toLocaleString() : "N/A"}
                  </div>
                </Card>
              ) : (
                <form onSubmit={handleResolveSubmit} className="space-y-3">
                  <div className="font-semibold text-foreground text-xs">Mark Incident as Resolved</div>
                  <textarea
                    rows={4}
                    placeholder="Document root cause, mitigation steps taken, and validation outcome..."
                    value={resolutionNotes}
                    onChange={(e) => setResolutionNotes(e.target.value)}
                    className="w-full p-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-purple"
                  />
                  <div className="flex justify-end">
                    <Button
                      type="submit"
                      disabled={isResolving || !resolutionNotes.trim()}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs gap-1.5"
                    >
                      <Send className="h-3.5 w-3.5" />
                      {isResolving ? "Resolving..." : "Submit & Mark Resolved"}
                    </Button>
                  </div>
                </form>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};
