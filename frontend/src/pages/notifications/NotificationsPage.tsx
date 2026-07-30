import { Bell, CheckCheck } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

const notifications = [
  { id: "1", type: "incident",  title: "P0 Incident Created: INC-1042",           body: "API Gateway elevated 5xx errors — investigation underway", time: "4 min ago",  read: false },
  { id: "2", type: "alert",     title: "Critical Alert: CPU > 90% on api-prod-01", body: "CPU utilization has exceeded 90% threshold for 5+ minutes",  time: "8 min ago",  read: false },
  { id: "3", type: "ai",        title: "AI identified $4,230/month savings",        body: "14 EC2 instances are idle >80% — right-sizing recommended",  time: "1h ago",     read: false },
  { id: "4", type: "cost",      title: "Monthly spend forecast updated",            body: "Forecasted EOMonth spend: $102,400 (+8.7% vs last month)",   time: "2h ago",     read: true  },
  { id: "5", type: "system",    title: "Alembic migration completed",               body: "Database migration 0001_initial_schema applied successfully", time: "3h ago",     read: true  },
  { id: "6", type: "incident",  title: "INC-1038 resolved",                         body: "Batch job processing delays resolved after pipeline restart", time: "5h ago",     read: true  },
  { id: "7", type: "alert",     title: "Certificate expiring in 14 days",           body: "TLS certificate for cdn-edge.cloudpulse.ai expires Jul 43",  time: "1d ago",     read: true  },
];

const typeConfig: Record<string, { badge: "danger" | "warning" | "purple" | "info" | "muted"; label: string }> = {
  incident: { badge: "danger",  label: "Incident" },
  alert:    { badge: "warning", label: "Alert"    },
  ai:       { badge: "purple",  label: "AI"       },
  cost:     { badge: "info",    label: "Cost"     },
  system:   { badge: "muted",   label: "System"   },
};

export default function NotificationsPage() {
  const unread = notifications.filter((n) => !n.read).length;
  return (
    <div className="space-y-6">
      <PageHeader
        title="Notifications"
        subtitle={`${unread} unread notifications`}
        actions={<Button variant="outline" size="sm" className="gap-2"><CheckCheck className="h-3.5 w-3.5" />Mark all read</Button>}
      />
      <Card>
        <CardContent className="p-0">
          {notifications.map((n) => {
            const cfg = typeConfig[n.type];
            return (
              <div key={n.id} className={`flex items-start gap-4 border-b border-white/[0.04] px-4 py-4 transition-colors hover:bg-white/[0.02] cursor-pointer ${!n.read ? "bg-brand-blue/[0.03]" : ""}`}>
                {!n.read && <div className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-blue" />}
                {n.read  && <div className="mt-2 h-1.5 w-1.5 shrink-0" />}
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-foreground">{n.title}</p>
                    <Badge variant={cfg.badge} className="text-[10px]">{cfg.label}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{n.body}</p>
                </div>
                <span className="text-xs text-muted-foreground shrink-0">{n.time}</span>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}
