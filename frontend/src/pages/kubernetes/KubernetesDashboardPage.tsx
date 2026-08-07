import { useState } from "react";
import { RefreshCw, Server, Box, Cpu, AlertTriangle, Sparkles, Activity, ShieldAlert, Loader2 } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import K8sClusterTopology from "@/components/kubernetes/K8sClusterTopology";
import K8sNodeHeatmap from "@/components/kubernetes/K8sNodeHeatmap";
import { useK8sClusters, useK8sNodes, useK8sPods, useK8sAnalyze } from "@/hooks/useKubernetes";
import { cn } from "@/lib/utils";

export default function KubernetesDashboardPage() {
  const { data: clusters = [], isLoading: clustersLoading, refetch: refetchClusters } = useK8sClusters();
  const { data: nodes = [] } = useK8sNodes();
  const { data: pods = [] } = useK8sPods();
  const { analyzeCluster, isAnalyzing } = useK8sAnalyze();
  const [analysis, setAnalysis] = useState<any>(null);

  const runningPods = pods.filter((p) => p.status === "Running").length;
  const failedPods = pods.filter((p) => p.status === "CrashLoopBackOff" || p.status === "OOMKilled").length;

  const handleRunAnalysis = async () => {
    try {
      const res = await analyzeCluster();
      setAnalysis(res);
    } catch (e) {
      alert("Failed to run AI analysis");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Kubernetes & Container Intelligence"
        subtitle="GKE, AWS EKS, Azure AKS & Hybrid Cluster Observability"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => refetchClusters()} className="gap-2 text-xs">
              <RefreshCw className="h-3.5 w-3.5" /> Refresh Clusters
            </Button>
            <Button size="sm" onClick={handleRunAnalysis} disabled={isAnalyzing} className="gap-2 bg-brand-blue hover:bg-brand-blue/90 text-white text-xs">
              <Sparkles className={cn("h-3.5 w-3.5", isAnalyzing && "animate-spin")} />
              Run Gemini Diagnostic
            </Button>
          </div>
        }
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Active Clusters" value={clusters.length} icon={<Server className="h-4 w-4" />} />
        <StatCard
          label="Running Pods"
          value={runningPods}
          icon={<Box className="h-4 w-4 text-emerald-400" />}
          trend={{ value: `${failedPods} failing`, direction: "down", positive: false }}
        />
        <StatCard label="Cluster Nodes" value={nodes.length} icon={<Cpu className="h-4 w-4 text-sky-400" />} />
        <StatCard label="Pod Failure Alerts" value={failedPods} icon={<AlertTriangle className="h-4 w-4 text-rose-400" />} />
      </div>

      {/* Node Heatmap */}
      <K8sNodeHeatmap nodes={nodes} />

      {/* Interactive Topology Graph */}
      <K8sClusterTopology />

      {/* Gemini AI Root Cause Analysis Result */}
      {analysis && (
        <Card className="border-purple-500/30 bg-purple-500/[0.03]">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-400" />
              <CardTitle className="text-sm font-semibold text-foreground">
                Gemini AI Root Cause Analysis (Health Score: {analysis.cluster_health_score}/100)
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {analysis.root_cause_analysis?.map((item: any, idx: number) => (
              <div key={idx} className="rounded-lg border border-white/10 bg-background/80 p-3 space-y-1 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-foreground">{item.pod_name}</span>
                  <Badge variant="danger" className="text-[10px]">
                    {item.issue}
                  </Badge>
                </div>
                <p className="text-muted-foreground"><span className="text-foreground font-semibold">Root Cause:</span> {item.root_cause}</p>
                <p className="text-emerald-400"><span className="text-foreground font-semibold">Recommendation:</span> {item.recommendation}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
