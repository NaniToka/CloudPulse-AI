import { Plus, RefreshCw, AlertOctagon } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { incidents, incidentTimeline } from "@/lib/mockData";
import IncidentTimeline from "@/components/dashboard/IncidentTimeline";
import { cn } from "@/lib/utils";

const severityBadge = { P0: "danger", P1: "danger", P2: "warning", P3: "info" } as const;
const statusColor   = { Investigating: "text-warning", Mitigating: "text-brand-blue", Resolved: "text-success", Open: "text-muted-foreground" };

export default function IncidentsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Incident Center"
        subtitle="Active incidents and resolution timeline"
        actions={
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2"><RefreshCw className="h-3.5 w-3.5" />Refresh</Button>
            <Button size="sm" className="gap-2"><Plus className="h-3.5 w-3.5" />Create Incident</Button>
          </div>
        }
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="P0 Incidents" value="1" subValue="Critical — active now" />
        <StatCard label="P1 Incidents" value="2" subValue="High severity"         />
        <StatCard label="P2 Incidents" value="4" subValue="Medium severity"       />
        <StatCard label="Resolved Today" value="8" subValue="avg MTTR: 28 min"   />
      </div>

      <IncidentTimeline />

      <Card>
        <CardHeader>
          <CardTitle className="text-foreground text-sm font-semibold">All Active Incidents</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/[0.06] text-xs text-muted-foreground">
                  {["ID","Severity","Title","Service","Status","Time"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {incidents.map((inc) => (
                  <tr key={inc.id} className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors cursor-pointer">
                    <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{inc.id}</td>
                    <td className="px-4 py-3"><Badge variant={severityBadge[inc.severity]}>{inc.severity}</Badge></td>
                    <td className="px-4 py-3 text-xs text-foreground max-w-[300px] truncate">{inc.title}</td>
                    <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{inc.service}</td>
                    <td className={cn("px-4 py-3 text-xs font-medium", statusColor[inc.status])}>{inc.status}</td>
                    <td className="px-4 py-3 text-xs text-muted-foreground">{inc.timeAgo}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
