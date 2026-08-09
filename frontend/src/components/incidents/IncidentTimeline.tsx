import React, { useState } from "react";
import { format } from "date-fns";
import {
  Activity,
  AlertTriangle,
  Bot,
  CheckCircle2,
  Clock,
  Flame,
  MessageSquare,
  Network,
  Plus,
  Send,
  ShieldAlert,
  Terminal,
  Wrench,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { TimelineEvent } from "@/types/incident";

interface Props {
  events: TimelineEvent[];
  onAddEvent?: (payload: { title: string; event_type: string; description?: string }) => void;
  isSubmitting?: boolean;
}

export function IncidentTimeline({ events = [], onAddEvent, isSubmitting = false }: Props) {
  const [newNote, setNewNote] = useState("");
  const [selectedFilter, setSelectedFilter] = useState<string>("ALL");

  const sortedEvents = [...events].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  const filteredEvents = sortedEvents.filter((evt) => {
    if (selectedFilter === "ALL") return true;
    if (selectedFilter === "ALERTS") return evt.event_type.includes("alert") || evt.event_type.includes("anomaly");
    if (selectedFilter === "RCA") return evt.event_type.includes("rca") || evt.event_type.includes("remediation");
    if (selectedFilter === "NOTES") return evt.event_type === "engineer_note";
    return true;
  });

  const handleAddNote = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim() || !onAddEvent) return;
    onAddEvent({
      title: "Engineer Note",
      description: newNote.trim(),
      event_type: "engineer_note",
    });
    setNewNote("");
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case "metric_anomaly":
        return <Activity className="w-3.5 h-3.5 text-amber-400" />;
      case "alert_triggered":
        return <AlertTriangle className="w-3.5 h-3.5 text-orange-400" />;
      case "trace_failure":
        return <Network className="w-3.5 h-3.5 text-red-400" />;
      case "log_error":
        return <Terminal className="w-3.5 h-3.5 text-rose-400" />;
      case "incident_created":
        return <Flame className="w-3.5 h-3.5 text-red-500" />;
      case "rca_identified":
        return <Bot className="w-3.5 h-3.5 text-cyan-400" />;
      case "remediation_recommended":
      case "remediation_executed":
        return <Wrench className="w-3.5 h-3.5 text-emerald-400" />;
      case "status_changed":
        return <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />;
      case "engineer_note":
        return <MessageSquare className="w-3.5 h-3.5 text-purple-400" />;
      default:
        return <Clock className="w-3.5 h-3.5 text-muted-foreground" />;
    }
  };

  const getBadgeColor = (type: string) => {
    switch (type) {
      case "metric_anomaly":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      case "alert_triggered":
        return "bg-orange-500/10 text-orange-400 border-orange-500/30";
      case "trace_failure":
        return "bg-red-500/10 text-red-400 border-red-500/30";
      case "log_error":
        return "bg-rose-500/10 text-rose-400 border-rose-500/30";
      case "rca_identified":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
      case "remediation_recommended":
      case "remediation_executed":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "engineer_note":
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      default:
        return "bg-slate-500/10 text-slate-400 border-slate-500/30";
    }
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Filter Chips */}
      <div className="flex items-center justify-between gap-2 border-b border-white/[0.06] pb-3">
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs">
          {["ALL", "ALERTS", "RCA", "NOTES"].map((f) => (
            <button
              key={f}
              onClick={() => setSelectedFilter(f)}
              className={cn(
                "px-2.5 py-1 rounded-md text-xs font-mono font-medium transition-all",
                selectedFilter === f
                  ? "bg-brand-500/20 text-brand-300 border border-brand-500/40"
                  : "text-muted-foreground hover:bg-white/[0.04] border border-transparent"
              )}
            >
              {f}
            </button>
          ))}
        </div>
        <span className="text-[11px] text-muted-foreground font-mono">
          {filteredEvents.length} events
        </span>
      </div>

      {/* Timeline Stream */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-[2px] before:bg-gradient-to-b before:from-brand-500/40 before:via-white/10 before:to-transparent overflow-y-auto max-h-[420px] pr-2">
        {filteredEvents.length === 0 ? (
          <div className="text-center py-8 text-sm text-muted-foreground">
            No timeline events recorded for this filter.
          </div>
        ) : (
          filteredEvents.map((evt, idx) => {
            let formattedTime = "12:00";
            let formattedDate = "";
            try {
              const d = new Date(evt.timestamp);
              formattedTime = format(d, "HH:mm:ss");
              formattedDate = format(d, "MMM dd");
            } catch {
              // fallback
            }

            return (
              <div key={evt.id || idx} className="relative group">
                {/* Timeline Dot with Icon */}
                <div className="absolute -left-[30px] top-0.5 flex h-6 w-6 items-center justify-center rounded-full border border-white/20 bg-bg-surface shadow-md group-hover:scale-110 group-hover:border-brand-400 transition-transform">
                  {getEventIcon(evt.event_type)}
                </div>

                {/* Content Box */}
                <div className="rounded-lg border border-white/[0.08] bg-white/[0.02] p-3 hover:border-white/[0.18] transition-colors">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-white tracking-wide">
                        {evt.title}
                      </span>
                      <Badge
                        variant="outline"
                        className={cn("text-[10px] uppercase font-mono px-1.5 py-0", getBadgeColor(evt.event_type))}
                      >
                        {evt.event_type.replace("_", " ")}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-1.5 text-[11px] font-mono text-muted-foreground">
                      <span>{formattedDate}</span>
                      <span className="text-brand-400 font-semibold">{formattedTime}</span>
                    </div>
                  </div>

                  {evt.description && (
                    <p className="mt-1.5 text-xs text-muted-foreground leading-relaxed">
                      {evt.description}
                    </p>
                  )}

                  <div className="mt-2 flex items-center justify-between text-[10px] text-muted-foreground/80 font-mono">
                    <span>Source: {evt.source}</span>
                    {evt.created_by && <span>By: {evt.created_by}</span>}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Add Engineer Note Input */}
      {onAddEvent && (
        <form onSubmit={handleAddNote} className="pt-2 border-t border-white/[0.08] flex items-center gap-2">
          <Input
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Add triage note or observation to timeline..."
            className="text-xs bg-bg-surface border-white/[0.1] h-9"
          />
          <Button
            type="submit"
            size="sm"
            disabled={!newNote.trim() || isSubmitting}
            className="h-9 px-3 bg-brand-600 hover:bg-brand-500 text-white shrink-0"
          >
            <Send className="w-3.5 h-3.5 mr-1" />
            Note
          </Button>
        </form>
      )}
    </div>
  );
}
