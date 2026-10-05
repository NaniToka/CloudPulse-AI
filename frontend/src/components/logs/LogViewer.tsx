import React, { useState } from "react";
import { Search, Filter, Terminal, FileCode2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ParsedLogEntry, LogStats } from "@/types/log_analysis";
import { cn } from "@/lib/utils";

interface LogViewerProps {
  entries: ParsedLogEntry[];
  stats?: LogStats;
  filename?: string;
}

const levelStyles: Record<string, { badgeVariant: "danger" | "warning" | "info" | "muted"; lineBg: string; textStyle: string }> = {
  CRITICAL: { badgeVariant: "danger",  lineBg: "bg-purple-500/10 hover:bg-purple-500/15 border-l-2 border-purple-500", textStyle: "text-purple-300 font-semibold" },
  ERROR:    { badgeVariant: "danger",  lineBg: "bg-rose-500/10 hover:bg-rose-500/15 border-l-2 border-rose-500",     textStyle: "text-rose-300 font-medium" },
  WARNING:  { badgeVariant: "warning", lineBg: "bg-amber-500/5 hover:bg-amber-500/10 border-l-2 border-amber-500",   textStyle: "text-amber-300" },
  WARN:     { badgeVariant: "warning", lineBg: "bg-amber-500/5 hover:bg-amber-500/10 border-l-2 border-amber-500",   textStyle: "text-amber-300" },
  INFO:     { badgeVariant: "info",    lineBg: "hover:bg-white/[0.02]",                                               textStyle: "text-slate-300" },
  DEBUG:    { badgeVariant: "muted",   lineBg: "hover:bg-white/[0.02]",                                               textStyle: "text-slate-500" },
  UNKNOWN:  { badgeVariant: "muted",   lineBg: "hover:bg-white/[0.02]",                                               textStyle: "text-slate-400" },
};

const filterLevels = ["ALL", "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] as const;

export default function LogViewer({ entries, stats, filename }: LogViewerProps) {
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState<string>("ALL");

  const filteredEntries = entries.filter((entry) => {
    const matchesSearch =
      entry.message.toLowerCase().includes(search.toLowerCase()) ||
      (entry.service && entry.service.toLowerCase().includes(search.toLowerCase())) ||
      entry.raw.toLowerCase().includes(search.toLowerCase());

    const normLevel = (entry.level || "").toUpperCase();
    let matchesFilter = true;
    if (activeFilter !== "ALL") {
      if (activeFilter === "WARNING") {
        matchesFilter = normLevel === "WARNING" || normLevel === "WARN";
      } else {
        matchesFilter = normLevel === activeFilter;
      }
    }

    return matchesSearch && matchesFilter;
  });

  return (
    <Card className="border-white/[0.08] bg-card/80 backdrop-blur-md">
      <CardHeader className="pb-3 border-b border-white/[0.06]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-brand-blue" />
            <CardTitle className="text-sm font-semibold">
              Syntax-Highlighted Log Viewer
              {filename && <span className="text-muted-foreground font-mono text-xs ml-2">({filename})</span>}
            </CardTitle>
          </div>

          {stats && (
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
                {stats.error_count} ERR
              </span>
              <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                {stats.warning_count} WARN
              </span>
              <span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                {stats.critical_count} CRIT
              </span>
              <span className="px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                {stats.info_count} INFO
              </span>
            </div>
          )}
        </div>

        {/* Search & Filter Toolbar */}
        <div className="mt-3 flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
            <Input
              placeholder="Search log messages, services, or raw lines…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 h-8 text-xs bg-bg-elevated border-white/[0.08]"
            />
          </div>

          <div className="flex gap-1 overflow-x-auto pb-1 sm:pb-0">
            {filterLevels.map((lvl) => (
              <button
                key={lvl}
                onClick={() => setActiveFilter(lvl)}
                className={cn(
                  "px-2.5 py-1 rounded text-[11px] font-medium transition-colors whitespace-nowrap",
                  activeFilter === lvl
                    ? "bg-brand-gradient text-white shadow-sm"
                    : "bg-white/[0.03] text-muted-foreground hover:bg-white/[0.08] hover:text-foreground"
                )}
              >
                {lvl}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <div className="font-mono text-[11px] max-h-[480px] overflow-y-auto divide-y divide-white/[0.03]">
          {filteredEntries.map((entry) => {
            const levelUpper = (entry.level || "UNKNOWN").toUpperCase();
            const config = levelStyles[levelUpper] || levelStyles.UNKNOWN;

            return (
              <div
                key={entry.line_number}
                className={cn(
                  "flex items-start gap-3 px-4 py-2 transition-colors",
                  config.lineBg
                )}
              >
                <span className="text-muted-foreground/40 shrink-0 w-10 text-right select-none font-mono">
                  {entry.line_number}
                </span>

                {entry.timestamp && (
                  <span className="text-slate-400 shrink-0 w-36 truncate select-none">
                    {entry.timestamp}
                  </span>
                )}

                <Badge variant={config.badgeVariant} className="shrink-0 text-[9px] px-1.5 py-0 h-4">
                  {entry.level}
                </Badge>

                {entry.service && (
                  <span className="text-brand-blue/90 shrink-0 font-semibold truncate max-w-[120px]">
                    [{entry.service}]
                  </span>
                )}

                <span className={cn("flex-1 break-all whitespace-pre-wrap leading-relaxed", config.textStyle)}>
                  {entry.message}
                </span>
              </div>
            );
          })}

          {filteredEntries.length === 0 && (
            <div className="py-12 text-center text-xs text-muted-foreground space-y-1">
              <FileCode2 className="w-6 h-6 mx-auto text-muted-foreground/40" />
              <p>No log lines match current search/filter criteria.</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
