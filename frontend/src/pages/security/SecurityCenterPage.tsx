/**
 * AI Security & Cloud Compliance Center — Main Dashboard Page
 */

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Search,
  Filter,
  Download,
  Printer,
  RefreshCw,
  Award,
  AlertTriangle,
  Server,
  FileText,
  Lock,
} from "lucide-react";

import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/useToast";

import { securityService } from "@/services/securityService";
import { ComplianceScorecards } from "@/components/security/ComplianceScorecards";
import { SecurityRiskHeatmap } from "@/components/security/SecurityRiskHeatmap";
import { FindingDetailDrawer } from "@/components/security/FindingDetailDrawer";
import type { SecurityFinding } from "@/types/security";

export default function SecurityCenterPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [search, setSearch] = useState("");
  const [selectedSeverity, setSelectedSeverity] = useState("ALL");
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [selectedProvider, setSelectedProvider] = useState("ALL");
  const [selectedFinding, setSelectedFinding] = useState<SecurityFinding | null>(null);

  // Queries
  const { data: riskData } = useQuery({
    queryKey: ["security-risk-score"],
    queryFn: () => securityService.getRiskScore(),
  });

  const { data: complianceData } = useQuery({
    queryKey: ["security-compliance"],
    queryFn: () => securityService.getCompliance(),
  });

  const { data: findingsData, isLoading } = useQuery({
    queryKey: ["security-findings", search, selectedSeverity, selectedCategory, selectedProvider],
    queryFn: () =>
      securityService.getFindings({
        search: search || undefined,
        severity: selectedSeverity !== "ALL" ? selectedSeverity : undefined,
        category: selectedCategory !== "ALL" ? selectedCategory : undefined,
        provider: selectedProvider !== "ALL" ? selectedProvider : undefined,
        size: 50,
      }),
  });

  // Scan Mutation
  const scanMutation = useMutation({
    mutationFn: (provider: string) => securityService.triggerScan(provider),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["security-findings"] });
      queryClient.invalidateQueries({ queryKey: ["security-risk-score"] });
      toast({
        title: "CSPM Scan Completed",
        description: res.message,
      });
    },
  });

  const findings = findingsData?.items || [];
  const reports = complianceData || [];

  const handleExportCSV = () => {
    const headers = "ID,Scan Name,Provider,Severity,Category,Resource,Framework\n";
    const rows = findings
      .map(
        (f) =>
          `"${f.id}","${f.scan_name}","${f.provider}","${f.severity}","${f.category}","${f.resource}","${f.compliance_framework}"`
      )
      .join("\n");

    const blob = new Blob([headers + rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `security_findings_${Date.now()}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="AI Security & Cloud Compliance Center"
        subtitle="Continuous Cloud Security Posture Management (CSPM), compliance scorecards, & AI threat analysis (Wiz & Google Security Command Center style)"
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportCSV}
              disabled={findings.length === 0}
              className="gap-2 text-xs"
            >
              <Download className="h-3.5 w-3.5" /> Export CSV
            </Button>

            <Button
              disabled={scanMutation.isPending}
              onClick={() => scanMutation.mutate("AWS")}
              className="bg-brand-purple hover:bg-brand-purple/90 text-white gap-2 text-xs font-bold shadow-lg"
            >
              <RefreshCw className={`h-4 w-4 ${scanMutation.isPending ? "animate-spin" : ""}`} />
              {scanMutation.isPending ? "Scanning Cloud..." : "Trigger CSPM Scan"}
            </Button>
          </div>
        }
      />

      {/* Top Stat KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Overall Security Score"
          value={`${riskData?.overall_security_score || 88.5}%`}
          subValue="AWS, GCP, & Azure Posture"
        />
        <StatCard
          label="Compliance Score"
          value={`${riskData?.compliance_overall_percentage || 91.2}%`}
          subValue="7 Frameworks Assessed"
        />
        <StatCard
          label="Critical Findings"
          value={String(riskData?.critical_findings_count || 4)}
          subValue="Immediate Action Required"
        />
        <StatCard
          label="Resources at Risk"
          value={String(riskData?.resources_at_risk_count || 9)}
          subValue="Tracked Cloud Resources"
        />
      </div>

      {/* Search & Filter Bar */}
      <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md">
        <CardContent className="p-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search finding, resource, or rule..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 bg-bg-elevated border-white/10 text-xs focus:border-brand-purple"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            <Filter className="h-4 w-4 text-muted-foreground mr-1" />
            <span className="text-xs text-muted-foreground font-mono">Severity:</span>
            {["ALL", "Critical", "High", "Medium", "Low"].map((sev) => (
              <button
                key={sev}
                onClick={() => setSelectedSeverity(sev)}
                className={`px-2.5 py-1 rounded-full text-xs font-mono transition-colors ${
                  selectedSeverity === sev
                    ? "bg-brand-purple text-white font-bold"
                    : "bg-white/5 text-muted-foreground hover:text-white"
                }`}
              >
                {sev}
              </button>
            ))}

            <span className="text-xs text-muted-foreground font-mono ml-2">Provider:</span>
            {["ALL", "AWS", "GCP", "Azure"].map((prov) => (
              <button
                key={prov}
                onClick={() => setSelectedProvider(prov)}
                className={`px-2.5 py-1 rounded-full text-xs font-mono transition-colors ${
                  selectedProvider === prov
                    ? "bg-brand-purple text-white font-bold"
                    : "bg-white/5 text-muted-foreground hover:text-white"
                }`}
              >
                {prov}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Main Security Tabs */}
      <Tabs defaultValue="findings" className="w-full space-y-4">
        <TabsList className="bg-bg-surface border border-white/10 p-1">
          <TabsTrigger value="findings" className="gap-2 text-xs font-mono">
            <ShieldAlert className="h-3.5 w-3.5" /> Vulnerability Table ({findings.length})
          </TabsTrigger>
          <TabsTrigger value="compliance" className="gap-2 text-xs font-mono">
            <Award className="h-3.5 w-3.5" /> Compliance Scorecards ({reports.length})
          </TabsTrigger>
          <TabsTrigger value="heatmap" className="gap-2 text-xs font-mono">
            <Server className="h-3.5 w-3.5" /> Risk Heatmap
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Findings Vulnerability Table */}
        <TabsContent value="findings">
          <Card className="border border-white/10 bg-bg-surface/90 shadow-xl overflow-hidden">
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-left font-sans text-xs">
                  <thead>
                    <tr className="border-b border-white/10 bg-bg-elevated/50 text-muted-foreground font-mono text-[11px]">
                      <th className="py-3 px-4">Severity</th>
                      <th className="py-3 px-4">Finding Name</th>
                      <th className="py-3 px-4">Provider</th>
                      <th className="py-3 px-4">Category</th>
                      <th className="py-3 px-4">Resource</th>
                      <th className="py-3 px-4">Framework</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {findings.map((f) => (
                      <tr
                        key={f.id}
                        onClick={() => setSelectedFinding(f)}
                        className="hover:bg-white/5 transition-colors cursor-pointer"
                      >
                        <td className="py-3 px-4">
                          <Badge
                            className={
                              f.severity === "Critical"
                                ? "bg-red-950/60 text-red-400 border-red-500/40"
                                : f.severity === "High"
                                ? "bg-amber-950/60 text-amber-400 border-amber-500/40"
                                : "bg-blue-950/60 text-blue-400 border-blue-500/40"
                            }
                          >
                            {f.severity}
                          </Badge>
                        </td>

                        <td className="py-3 px-4 font-bold text-foreground max-w-xs truncate">
                          {f.scan_name}
                        </td>

                        <td className="py-3 px-4 font-mono">{f.provider}</td>
                        <td className="py-3 px-4 font-mono text-brand-purple">{f.category}</td>
                        <td className="py-3 px-4 font-mono text-muted-foreground max-w-xs truncate">
                          {f.resource}
                        </td>
                        <td className="py-3 px-4 font-mono text-emerald-400">{f.compliance_framework}</td>

                        <td className="py-3 px-4 text-right">
                          <Button size="sm" variant="ghost" className="h-7 text-[11px] font-mono text-brand-purple">
                            View AI Threat →
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Compliance Scorecards */}
        <TabsContent value="compliance">
          <ComplianceScorecards reports={reports} />
        </TabsContent>

        {/* Tab 3: Risk Heatmap */}
        <TabsContent value="heatmap">
          <SecurityRiskHeatmap findings={findings} />
        </TabsContent>
      </Tabs>

      {/* Selected Finding Detail Drawer */}
      <FindingDetailDrawer finding={selectedFinding} onClose={() => setSelectedFinding(null)} />
    </div>
  );
}
