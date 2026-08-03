import React, { useState } from "react";
import { Search, Filter, Download, Server, FileText } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { exportToCsv } from "@/lib/csvExport";
import type { CloudCostItem } from "@/types/cost";
import { cn } from "@/lib/utils";

interface ResourceTableProps {
  resources: CloudCostItem[];
}

const statusBadges: Record<string, { label: string; badgeVariant: "info" | "warning" | "danger" | "muted" }> = {
  active:          { label: "ACTIVE",          badgeVariant: "info" },
  idle:            { label: "IDLE",            badgeVariant: "danger" },
  overprovisioned: { label: "OVERPROVISIONED", badgeVariant: "warning" },
};

export default function ResourceTable({ resources }: ResourceTableProps) {
  const [search, setSearch] = useState("");
  const [serviceFilter, setServiceFilter] = useState("all");
  const [envFilter, setEnvFilter] = useState("all");

  const services = ["all", ...Array.from(new Set(resources.map((r) => r.service)))];
  const environments = ["all", ...Array.from(new Set(resources.map((r) => r.environment)))];

  const filteredResources = resources.filter((r) => {
    const matchesSearch =
      r.resource_name.toLowerCase().includes(search.toLowerCase()) ||
      r.service.toLowerCase().includes(search.toLowerCase()) ||
      r.region.toLowerCase().includes(search.toLowerCase());

    const matchesService = serviceFilter === "all" || r.service === serviceFilter;
    const matchesEnv = envFilter === "all" || r.environment === envFilter;

    return matchesSearch && matchesService && matchesEnv;
  });

  const handleExportCsv = () => {
    const exportRows = filteredResources.map((r) => ({
      ResourceName: r.resource_name,
      Service: r.service,
      Provider: r.provider.toUpperCase(),
      Region: r.region,
      Environment: r.environment,
      MonthlyCost: r.cost,
      DailyCost: r.daily_cost,
      Status: r.status,
    }));
    exportToCsv("cloudpulse_cost_resources.csv", exportRows);
  };

  return (
    <Card className="border-white/[0.08] bg-card/80 backdrop-blur-md">
      <CardHeader className="pb-3 border-b border-white/[0.06]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-brand-blue" />
            <CardTitle className="text-sm font-semibold">Resource Cost Inventory</CardTitle>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleExportCsv}
            className="gap-2 text-xs bg-bg-elevated border-white/[0.08]"
          >
            <Download className="w-3.5 h-3.5" />
            Export CSV
          </Button>
        </div>

        {/* Controls Row */}
        <div className="mt-3 flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
            <Input
              placeholder="Search resource name, service, or region…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 h-8 text-xs bg-bg-elevated border-white/[0.08]"
            />
          </div>

          {/* Filter Dropdowns */}
          <div className="flex gap-2">
            <select
              value={serviceFilter}
              onChange={(e) => setServiceFilter(e.target.value)}
              className="h-8 px-2.5 rounded-md bg-bg-elevated border border-white/[0.08] text-xs text-foreground focus:outline-none"
            >
              {services.map((s) => (
                <option key={s} value={s}>
                  {s === "all" ? "All Services" : s}
                </option>
              ))}
            </select>

            <select
              value={envFilter}
              onChange={(e) => setEnvFilter(e.target.value)}
              className="h-8 px-2.5 rounded-md bg-bg-elevated border border-white/[0.08] text-xs text-foreground focus:outline-none"
            >
              {environments.map((e) => (
                <option key={e} value={e}>
                  {e === "all" ? "All Environments" : e}
                </option>
              ))}
            </select>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <div className="overflow-x-auto max-h-[420px]">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-white/[0.02] border-b border-white/[0.06] text-muted-foreground uppercase text-[10px] tracking-wider sticky top-0 bg-card z-10">
              <tr>
                <th className="px-4 py-3">Resource Name</th>
                <th className="px-4 py-3">Service</th>
                <th className="px-4 py-3">Region</th>
                <th className="px-4 py-3">Environment</th>
                <th className="px-4 py-3 text-right">Monthly Spend</th>
                <th className="px-4 py-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.03]">
              {filteredResources.map((res) => {
                const statusCfg = statusBadges[res.status] || statusBadges.active;

                return (
                  <tr key={res.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-4 py-2.5 font-semibold text-foreground truncate max-w-[220px]">
                      {res.resource_name}
                    </td>
                    <td className="px-4 py-2.5 text-brand-blue/90 font-sans">{res.service}</td>
                    <td className="px-4 py-2.5 text-slate-400">{res.region}</td>
                    <td className="px-4 py-2.5 text-muted-foreground capitalize">{res.environment}</td>
                    <td className="px-4 py-2.5 text-right font-bold text-foreground">
                      ${res.cost.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-2.5 text-center">
                      <Badge variant={statusCfg.badgeVariant} className="text-[9px] px-1.5 py-0">
                        {statusCfg.label}
                      </Badge>
                    </td>
                  </tr>
                );
              })}

              {filteredResources.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-xs text-muted-foreground">
                    <FileText className="w-6 h-6 mx-auto mb-1 text-muted-foreground/30" />
                    No cloud resources match current search/filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
