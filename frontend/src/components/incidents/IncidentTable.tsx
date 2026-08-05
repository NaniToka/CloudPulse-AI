/**
 * Enterprise Incident Table Component
 * Features: filters, search, sorting, severity/status badges, pagination, quick actions.
 */

import React from "react";
import {
  Search,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  User,
  Sparkles,
  AlertCircle,
  Edit3,
  CheckCircle,
  Eye,
  Globe,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Incident } from "@/types/incident";

interface IncidentTableProps {
  incidents: Incident[];
  total: number;
  page: number;
  pages: number;
  isLoading: boolean;
  search: string;
  onSearchChange: (val: string) => void;
  severityFilter: string;
  onSeverityFilterChange: (val: string) => void;
  statusFilter: string;
  onStatusFilterChange: (val: string) => void;
  serviceFilter: string;
  onServiceFilterChange: (val: string) => void;
  sortBy: string;
  sortDir: string;
  onSortChange: (field: string) => void;
  onPageChange: (newPage: number) => void;
  onSelectIncident: (incident: Incident) => void;
  onEditIncident: (incident: Incident) => void;
  onQuickResolve: (incident: Incident) => void;
}

const severityBadgeMap: Record<string, "critical" | "danger" | "warning" | "info"> = {
  P0: "critical",
  P1: "danger",
  P2: "warning",
  P3: "info",
};

const statusBadgeMap: Record<string, "danger" | "warning" | "purple" | "success" | "muted"> = {
  Open: "danger",
  Investigating: "warning",
  Monitoring: "purple",
  Resolved: "success",
  Closed: "muted",
};

export const IncidentTable: React.FC<IncidentTableProps> = ({
  incidents,
  total,
  page,
  pages,
  isLoading,
  search,
  onSearchChange,
  severityFilter,
  onSeverityFilterChange,
  statusFilter,
  onStatusFilterChange,
  serviceFilter,
  onServiceFilterChange,
  sortBy,
  sortDir,
  onSortChange,
  onPageChange,
  onSelectIncident,
  onEditIncident,
  onQuickResolve,
}) => {
  return (
    <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md shadow-2xl">
      <CardHeader className="p-4 border-b border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <CardTitle className="text-base font-semibold text-foreground flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-brand-purple animate-pulse" />
            Live Incident Directory
          </CardTitle>
          <p className="text-xs text-muted-foreground mt-0.5">
            Showing {incidents.length} of {total} total incidents
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px] md:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search ID, title, service, engineer..."
              value={search}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-9 h-9 text-xs bg-bg-elevated/60 border-white/10 focus:border-brand-purple"
            />
          </div>

          {/* Severity filter */}
          <select
            value={severityFilter}
            onChange={(e) => onSeverityFilterChange(e.target.value)}
            className="h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-purple"
          >
            <option value="">All Severities</option>
            <option value="P0">P0 — Critical</option>
            <option value="P1">P1 — High</option>
            <option value="P2">P2 — Medium</option>
            <option value="P3">P3 — Low</option>
          </select>

          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            className="h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-purple"
          >
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Investigating">Investigating</option>
            <option value="Monitoring">Monitoring</option>
            <option value="Resolved">Resolved</option>
            <option value="Closed">Closed</option>
          </select>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-white/10 text-muted-foreground bg-bg-elevated/40">
                <th className="px-4 py-3 text-left font-mono font-medium">ID</th>
                <th
                  onClick={() => onSortChange("severity")}
                  className="px-4 py-3 text-left font-medium cursor-pointer hover:text-foreground transition-colors"
                >
                  <div className="flex items-center gap-1">
                    Severity <ArrowUpDown className="h-3 w-3 opacity-60" />
                  </div>
                </th>
                <th
                  onClick={() => onSortChange("title")}
                  className="px-4 py-3 text-left font-medium cursor-pointer hover:text-foreground transition-colors"
                >
                  <div className="flex items-center gap-1">
                    Title & Context <ArrowUpDown className="h-3 w-3 opacity-60" />
                  </div>
                </th>
                <th
                  onClick={() => onSortChange("status")}
                  className="px-4 py-3 text-left font-medium cursor-pointer hover:text-foreground transition-colors"
                >
                  Status
                </th>
                <th className="px-4 py-3 text-left font-medium">Service & Region</th>
                <th className="px-4 py-3 text-left font-medium">Assigned Engineer</th>
                <th
                  onClick={() => onSortChange("created_at")}
                  className="px-4 py-3 text-left font-medium cursor-pointer hover:text-foreground transition-colors"
                >
                  Started Time
                </th>
                <th className="px-4 py-3 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="border-b border-white/5 animate-pulse">
                    <td className="px-4 py-4"><div className="h-4 w-12 bg-white/10 rounded" /></td>
                    <td className="px-4 py-4"><div className="h-5 w-10 bg-white/10 rounded" /></td>
                    <td className="px-4 py-4"><div className="h-4 w-48 bg-white/10 rounded" /></td>
                    <td className="px-4 py-4"><div className="h-5 w-20 bg-white/10 rounded" /></td>
                    <td className="px-4 py-4"><div className="h-4 w-24 bg-white/10 rounded" /></td>
                    <td className="px-4 py-4"><div className="h-4 w-28 bg-white/10 rounded" /></td>
                    <td className="px-4 py-4"><div className="h-4 w-20 bg-white/10 rounded" /></td>
                    <td className="px-4 py-4 text-right"><div className="h-4 w-16 bg-white/10 rounded ml-auto" /></td>
                  </tr>
                ))
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-muted-foreground">
                    <AlertCircle className="h-8 w-8 mx-auto mb-2 text-muted-foreground/50" />
                    No incidents match your active filters.
                  </td>
                </tr>
              ) : (
                incidents.map((inc) => (
                  <tr
                    key={inc.id}
                    className="border-b border-white/5 hover:bg-white/[0.04] transition-all group"
                  >
                    {/* Incident ID */}
                    <td
                      onClick={() => onSelectIncident(inc)}
                      className="px-4 py-3 font-mono text-[11px] text-brand-purple cursor-pointer hover:underline"
                    >
                      {inc.id.slice(0, 8)}
                    </td>

                    {/* Severity Badge */}
                    <td className="px-4 py-3 font-mono font-medium">
                      <Badge variant={severityBadgeMap[inc.severity] || "default"}>
                        {inc.severity}
                      </Badge>
                    </td>

                    {/* Title */}
                    <td
                      onClick={() => onSelectIncident(inc)}
                      className="px-4 py-3 max-w-xs md:max-w-md truncate cursor-pointer"
                    >
                      <div className="font-semibold text-foreground group-hover:text-brand-purple transition-colors truncate">
                        {inc.title}
                      </div>
                      {inc.description && (
                        <div className="text-[11px] text-muted-foreground truncate mt-0.5">
                          {inc.description}
                        </div>
                      )}
                    </td>

                    {/* Status */}
                    <td className="px-4 py-3">
                      <Badge variant={statusBadgeMap[inc.status] || "default"}>
                        {inc.status}
                      </Badge>
                    </td>

                    {/* Affected Service & Region */}
                    <td className="px-4 py-3 font-mono text-muted-foreground">
                      <div className="flex items-center gap-1.5">
                        <span className="px-2 py-0.5 rounded bg-bg-elevated border border-white/5">
                          {inc.affected_service || "api-gateway"}
                        </span>
                        <span className="text-[10px] text-muted-foreground flex items-center gap-0.5">
                          <Globe className="h-3 w-3" /> {inc.affected_region || "us-east-1"}
                        </span>
                      </div>
                    </td>

                    {/* Engineer */}
                    <td className="px-4 py-3 text-muted-foreground">
                      <div className="flex items-center gap-1.5">
                        <User className="h-3 w-3 text-brand-purple/70" />
                        <span className="truncate max-w-[130px]">
                          {inc.assigned_engineer || inc.assigned_to || "Unassigned"}
                        </span>
                      </div>
                    </td>

                    {/* Started Time */}
                    <td className="px-4 py-3 text-muted-foreground font-mono text-[11px]">
                      {new Date(inc.started_at || inc.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </td>

                    {/* Actions */}
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => onSelectIncident(inc)}
                          title="View Details"
                          className="h-7 w-7 text-muted-foreground hover:text-foreground"
                        >
                          <Eye className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => onEditIncident(inc)}
                          title="Edit Incident"
                          className="h-7 w-7 text-muted-foreground hover:text-brand-blue"
                        >
                          <Edit3 className="h-3.5 w-3.5" />
                        </Button>
                        {inc.status !== "Resolved" && inc.status !== "Closed" && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => onQuickResolve(inc)}
                            title="Quick Resolve"
                            className="h-7 w-7 text-muted-foreground hover:text-emerald-400"
                          >
                            <CheckCircle className="h-3.5 w-3.5" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="p-3 border-t border-white/10 flex items-center justify-between text-xs text-muted-foreground bg-bg-elevated/20">
          <div>
            Page <span className="font-semibold text-foreground">{page}</span> of{" "}
            <span className="font-semibold text-foreground">{pages}</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1 || isLoading}
              onClick={() => onPageChange(page - 1)}
              className="h-8 px-2 text-xs"
            >
              <ChevronLeft className="h-3.5 w-3.5 mr-1" /> Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= pages || isLoading}
              onClick={() => onPageChange(page + 1)}
              className="h-8 px-2 text-xs"
            >
              Next <ChevronRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
