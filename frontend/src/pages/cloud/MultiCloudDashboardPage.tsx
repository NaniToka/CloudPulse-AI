import { RefreshCw, Cloud, Server, DollarSign, ShieldAlert, Sparkles, Activity, Globe, Loader2 } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import CloudTopologyMap from "@/components/cloud/CloudTopologyMap";
import { useCloudHealth, useCloudCost, useCloudSecurity, useCloudSync } from "@/hooks/useCloudObservability";
import { cn } from "@/lib/utils";

export default function MultiCloudDashboardPage() {
  const { data: health, isLoading: healthLoading } = useCloudHealth();
  const { data: cost, isLoading: costLoading } = useCloudCost();
  const { data: security, isLoading: secLoading } = useCloudSecurity();
  const { triggerSync, isSyncing } = useCloudSync();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Multi-Cloud Observability"
        subtitle="Unified AWS, Microsoft Azure & Google Cloud Infrastructure"
        actions={
          <Button
            variant="outline"
            size="sm"
            onClick={() => triggerSync()}
            disabled={isSyncing}
            className="gap-2 text-xs"
          >
            <RefreshCw className={cn("h-3.5 w-3.5", isSyncing && "animate-spin")} />
            Sync Multi-Cloud Telemetry
          </Button>
        }
      />

      {/* Provider Overview Header Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card className="border-amber-500/20 bg-amber-500/[0.03]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-bold text-amber-400 font-mono tracking-wider">AWS CLOUD</CardTitle>
            <Badge variant="outline" className="border-amber-500/30 text-amber-400 text-[10px]">
              Connected
            </Badge>
          </CardHeader>
          <CardContent className="space-y-1">
            <div className="text-2xl font-bold text-foreground">$4,620<span className="text-xs text-muted-foreground font-normal">/mo</span></div>
            <p className="text-xs text-muted-foreground">4 Monitored Services (EKS, EC2, RDS, S3)</p>
          </CardContent>
        </Card>

        <Card className="border-sky-500/20 bg-sky-500/[0.03]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-bold text-sky-400 font-mono tracking-wider">GOOGLE CLOUD</CardTitle>
            <Badge variant="outline" className="border-sky-500/30 text-sky-400 text-[10px]">
              Connected
            </Badge>
          </CardHeader>
          <CardContent className="space-y-1">
            <div className="text-2xl font-bold text-foreground">$2,520<span className="text-xs text-muted-foreground font-normal">/mo</span></div>
            <p className="text-xs text-muted-foreground">3 Monitored Services (GKE, Cloud SQL, Functions)</p>
          </CardContent>
        </Card>

        <Card className="border-purple-500/20 bg-purple-500/[0.03]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-bold text-purple-400 font-mono tracking-wider">AZURE CLOUD</CardTitle>
            <Badge variant="outline" className="border-purple-500/30 text-purple-400 text-[10px]">
              Connected
            </Badge>
          </CardHeader>
          <CardContent className="space-y-1">
            <div className="text-2xl font-bold text-foreground">$1,060<span className="text-xs text-muted-foreground font-normal">/mo</span></div>
            <p className="text-xs text-muted-foreground">2 Monitored Services (Azure VM, Blob Storage)</p>
          </CardContent>
        </Card>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="Total Discovered Resources"
          value={health?.total_resources ?? 9}
          icon={<Server className="h-4 w-4" />}
        />
        <StatCard
          label="Multi-Cloud Health Score"
          value={`${health?.health_score_percent ?? 88.9}%`}
          icon={<Activity className="h-4 w-4 text-emerald-400" />}
          trend={{ value: "Operational", direction: "up", positive: true }}
        />
        <StatCard
          label="Total Monthly Burn"
          value={`$${cost?.total_monthly_spend?.toLocaleString() ?? "8,200"}`}
          icon={<DollarSign className="h-4 w-4 text-amber-400" />}
        />
        <StatCard
          label="Security Compliance"
          value={`${security?.overall_compliance_score ?? 82}%`}
          icon={<ShieldAlert className="h-4 w-4 text-purple-400" />}
        />
      </div>

      {/* Interactive Topology Graph */}
      <CloudTopologyMap />

      {/* Gemini AI Multi-Cloud Architecture Recommendations */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-purple-400" />
            <CardTitle className="text-sm font-semibold text-foreground">
              Gemini AI Multi-Cloud Architecture Recommendations
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {healthLoading ? (
            <div className="flex h-24 items-center justify-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Synthesizing multi-cloud Insights...
            </div>
          ) : (
            health?.ai_insights?.map((item, idx) => (
              <div
                key={idx}
                className="flex items-start justify-between rounded-lg border border-white/10 bg-white/[0.02] p-3 hover:bg-white/[0.04] transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <p className="text-xs font-semibold text-foreground">{item.title}</p>
                    <Badge
                      variant={
                        item.severity === "critical"
                          ? "danger"
                          : item.severity === "high"
                          ? "warning"
                          : "secondary"
                      }
                      className="text-[10px]"
                    >
                      {item.category}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
                <Button size="xs" variant="outline" className="text-[10px] shrink-0">
                  Apply Patch
                </Button>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
