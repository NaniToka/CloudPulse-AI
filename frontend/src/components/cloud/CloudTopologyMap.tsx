import React from "react";
import { Server, Database, Cloud, ShieldAlert, Cpu, Network, HardDrive, Zap } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export interface TopologyNode {
  id: string;
  name: string;
  provider: "AWS" | "Azure" | "GCP" | string;
  type: string;
  service: string;
  status: "healthy" | "warning" | "critical" | string;
  region: string;
  connections: string[];
}

const mockTopologyNodes: TopologyNode[] = [
  {
    id: "node-aws-vpc",
    name: "aws-vpc-us-east-1",
    provider: "AWS",
    type: "networking",
    service: "VPC",
    status: "healthy",
    region: "us-east-1",
    connections: ["node-aws-eks", "node-aws-rds"],
  },
  {
    id: "node-aws-eks",
    name: "aws-eks-production",
    provider: "AWS",
    type: "kubernetes_cluster",
    service: "EKS Cluster",
    status: "healthy",
    region: "us-east-1",
    connections: ["node-aws-rds", "node-s3"],
  },
  {
    id: "node-aws-rds",
    name: "aws-rds-postgres",
    provider: "AWS",
    type: "database",
    service: "RDS Postgres",
    status: "healthy",
    region: "us-east-1",
    connections: [],
  },
  {
    id: "node-s3",
    name: "aws-s3-telemetry",
    provider: "AWS",
    type: "storage",
    service: "S3 Bucket",
    status: "warning",
    region: "us-east-1",
    connections: [],
  },
  {
    id: "node-gcp-gke",
    name: "gcp-gke-analytics",
    provider: "GCP",
    type: "kubernetes_cluster",
    service: "GKE",
    status: "warning",
    region: "us-central1",
    connections: ["node-gcp-sql"],
  },
  {
    id: "node-gcp-sql",
    name: "gcp-cloudsql-master",
    provider: "GCP",
    type: "database",
    service: "Cloud SQL",
    status: "healthy",
    region: "us-central1",
    connections: [],
  },
  {
    id: "node-azure-vm",
    name: "azure-vm-worker-02",
    provider: "Azure",
    type: "virtual_machine",
    service: "Azure VM",
    status: "critical",
    region: "eastus",
    connections: ["node-azure-blob"],
  },
  {
    id: "node-azure-blob",
    name: "azure-blob-storage",
    provider: "Azure",
    type: "storage",
    service: "Blob Storage",
    status: "healthy",
    region: "eastus",
    connections: [],
  },
];

const providerStyles: Record<string, { border: string; bg: string; text: string }> = {
  AWS: { border: "border-amber-500/40", bg: "bg-amber-500/10", text: "text-amber-400" },
  GCP: { border: "border-sky-500/40", bg: "bg-sky-500/10", text: "text-sky-400" },
  Azure: { border: "border-purple-500/40", bg: "bg-purple-500/10", text: "text-purple-400" },
};

const statusDot: Record<string, string> = {
  healthy: "bg-emerald-400",
  warning: "bg-amber-400 animate-pulse",
  critical: "bg-rose-500 animate-ping",
};

export default function CloudTopologyMap() {
  return (
    <div className="rounded-xl border border-white/10 bg-slate-950/80 p-5 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div>
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <Network className="h-4 w-4 text-brand-blue" />
            Interactive Multi-Cloud Topology Map
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            Cross-cloud dependency visualization across AWS, GCP, and Azure
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-[10px] border-amber-500/40 text-amber-400">
            AWS us-east-1
          </Badge>
          <Badge variant="outline" className="text-[10px] border-sky-500/40 text-sky-400">
            GCP us-central1
          </Badge>
          <Badge variant="outline" className="text-[10px] border-purple-500/40 text-purple-400">
            Azure eastus
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
        {["AWS", "GCP", "Azure"].map((provider) => {
          const providerNodes = mockTopologyNodes.filter((n) => n.provider === provider);
          const style = providerStyles[provider];
          return (
            <div key={provider} className={cn("rounded-lg border p-4 space-y-4", style.border, style.bg)}>
              <div className="flex items-center justify-between">
                <span className={cn("text-xs font-bold font-mono tracking-wider", style.text)}>
                  {provider} CLOUD ENVIRONMENT
                </span>
                <span className="text-[10px] text-muted-foreground">{providerNodes.length} Nodes Connected</span>
              </div>

              <div className="space-y-3">
                {providerNodes.map((node) => (
                  <div
                    key={node.id}
                    className="group relative flex items-center justify-between rounded-md border border-white/10 bg-background/80 p-3 shadow-md hover:border-white/20 transition-all cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn("h-2.5 w-2.5 rounded-full shrink-0", statusDot[node.status] || "bg-slate-400")} />
                      <div>
                        <p className="text-xs font-semibold text-foreground font-mono leading-tight">{node.name}</p>
                        <p className="text-[10px] text-muted-foreground">
                          {node.service} · {node.region}
                        </p>
                      </div>
                    </div>
                    {node.connections.length > 0 && (
                      <span className="text-[9px] font-mono bg-white/5 px-2 py-0.5 rounded text-muted-foreground">
                        ➜ {node.connections.length} linked
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
