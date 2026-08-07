import { useState } from "react";
import { Bell, CheckCheck, Loader2 } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { useNotificationsQuery } from "@/hooks/useDashboardQuery";

const typeConfig: Record<string, { badge: "danger" | "warning" | "purple" | "info" | "muted"; label: string }> = {
  incident: { badge: "danger", label: "Incident" },
  alert: { badge: "warning", label: "Alert" },
  ai: { badge: "purple", label: "AI" },
  cost: { badge: "info", label: "Cost" },
  system: { badge: "muted", label: "System" },
  warning: { badge: "warning", label: "Warning" },
  error: { badge: "danger", label: "Error" },
  info: { badge: "info", label: "Info" },
};

export default function NotificationsPage() {
  const [unreadOnly, setUnreadOnly] = useState(false);
  const { data: notifications = [], isLoading, markRead, markAllRead } = useNotificationsQuery({
    unread_only: unreadOnly,
  });

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Notifications"
        subtitle={`${unreadCount} unread notifications`}
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant={unreadOnly ? "default" : "outline"}
              size="sm"
              onClick={() => setUnreadOnly(!unreadOnly)}
              className="text-xs"
            >
              {unreadOnly ? "Showing Unread Only" : "Show All"}
            </Button>
            <Button variant="outline" size="sm" onClick={() => markAllRead()} className="gap-2 text-xs">
              <CheckCheck className="h-3.5 w-3.5" />
              Mark all read
            </Button>
          </div>
        }
      />
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex h-48 items-center justify-center gap-2 text-muted-foreground text-sm">
              <Loader2 className="h-5 w-5 animate-spin" /> Loading notifications...
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground text-sm">No notifications found.</div>
          ) : (
            notifications.map((n) => {
              const cfg = typeConfig[n.category || n.type] || typeConfig.info;
              return (
                <div
                  key={n.id}
                  onClick={() => !n.is_read && markRead(n.id)}
                  className={`flex items-start gap-4 border-b border-white/[0.04] px-4 py-4 transition-colors hover:bg-white/[0.02] cursor-pointer ${
                    !n.is_read ? "bg-brand-blue/[0.04]" : ""
                  }`}
                >
                  {!n.is_read ? (
                    <div className="mt-2 h-2 w-2 shrink-0 rounded-full bg-brand-blue animate-pulse" />
                  ) : (
                    <div className="mt-2 h-2 w-2 shrink-0" />
                  )}
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-foreground">{n.title}</p>
                      <Badge variant={cfg.badge} className="text-[10px]">
                        {cfg.label}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{n.message}</p>
                  </div>
                  <span className="text-xs text-muted-foreground shrink-0 font-mono">
                    {new Date(n.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
              );
            })
          )}
        </CardContent>
      </Card>
    </div>
  );
}
