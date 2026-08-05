/**
 * Auto Remediation Center & AI Runbook Generator — Main Dashboard Page
 */

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Sparkles,
  BookOpen,
  Play,
  CheckCircle2,
  Clock,
  ShieldCheck,
  Search,
  Filter,
  Download,
  Printer,
  FileText,
  Plus,
  Zap,
  Activity,
  AlertTriangle,
} from "lucide-react";

import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/useToast";

import { runbookService } from "@/services/runbookService";
import { RunbookStepList } from "@/components/runbooks/RunbookStepList";
import { RunbookExecutionTimeline } from "@/components/runbooks/RunbookExecutionTimeline";
import type { Runbook, RunbookGeneratePayload } from "@/types/runbook";

export default function RunbookDashboardPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [search, setSearch] = useState("");
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [selectedRunbook, setSelectedRunbook] = useState<Runbook | null>(null);

  // Generate Dialog State
  const [isGenerateOpen, setIsGenerateOpen] = useState(false);
  const [genService, setGenService] = useState("api-gateway");
  const [genSeverity, setGenSeverity] = useState<"P0" | "P1" | "P2" | "P3">("P1");
  const [genTitle, setGenTitle] = useState("");

  // Fetch Runbooks Query
  const { data, isLoading } = useQuery({
    queryKey: ["runbooks", search, selectedSeverity, selectedStatus],
    queryFn: () =>
      runbookService.getRunbooks({
        search: search || undefined,
        severity: selectedSeverity !== "ALL" ? selectedSeverity : undefined,
        status: selectedStatus !== "ALL" ? selectedStatus : undefined,
        size: 50,
      }),
  });

  // Generate Runbook Mutation
  const generateMutation = useMutation({
    mutationFn: (payload: RunbookGeneratePayload) => runbookService.generateRunbook(payload),
    onSuccess: (newRb) => {
      queryClient.invalidateQueries({ queryKey: ["runbooks"] });
      setIsGenerateOpen(false);
      setSelectedRunbook(newRb);
      toast({
        title: "AI Runbook Generated",
        description: `Runbook '${newRb.title}' generated successfully with ${newRb.steps.length} automation steps.`,
      });
    },
  });

  // Approve Mutation
  const approveMutation = useMutation({
    mutationFn: (id: string) => runbookService.approveRunbook(id),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["runbooks"] });
      setSelectedRunbook(updated);
      toast({
        title: "Runbook Approved",
        description: "Runbook approved for automated SRE execution.",
      });
    },
  });

  // Execute Mutation
  const executeMutation = useMutation({
    mutationFn: (id: string) => runbookService.executeRunbook(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["runbooks"] });
      if (selectedRunbook) {
        runbookService.getRunbookById(selectedRunbook.id).then(setSelectedRunbook);
      }
      toast({
        title: "Remediation Executed",
        description: "Automated CLI & Kubernetes steps executed successfully.",
      });
    },
  });

  const runbooks = data?.items || [];

  const handleExportMarkdown = (rb: Runbook) => {
    let md = `# ${rb.title}\n\n`;
    md += `**Service:** ${rb.service_name} | **Severity:** ${rb.severity} | **Status:** ${rb.status}\n\n`;
    md += `## Executive Summary\n${rb.executive_summary}\n\n`;
    md += `## Root Cause\n${rb.root_cause}\n\n`;
    md += `## Automated Steps\n`;
    rb.steps.forEach((s) => {
      md += `### Step ${s.step_number}: ${s.title}\n`;
      md += `${s.description}\n\`\`\`bash\n${s.command}\n\`\`\`\n\n`;
    });
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `runbook_${rb.service_name}_${Date.now()}.md`;
    a.click();
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="AI Runbook Generator & Auto Remediation Center"
        subtitle="Google SRE & Datadog style automated incident recovery runbooks with executable CLI, K8s, & Terraform steps"
        actions={
          <Button
            onClick={() => setIsGenerateOpen(true)}
            className="bg-brand-purple hover:bg-brand-purple/90 text-white gap-2 text-xs font-bold shadow-lg"
          >
            <Sparkles className="h-4 w-4" /> Generate AI Runbook
          </Button>
        }
      />

      {/* Top Stat KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Runbooks"
          value={String(data?.total || 3)}
          subValue="+100% SRE coverage"
        />
        <StatCard
          label="Active Executions"
          value="1 In-Progress"
          subValue="Automated step runner"
        />
        <StatCard
          label="Auto Mitigation Rate"
          value="94.2%"
          subValue="+12.5% success rate"
        />
        <StatCard
          label="MTTR Saved"
          value="24.5 mins"
          subValue="-45% downtime reduction"
        />
      </div>

      {/* Search & Filter Bar */}
      <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md">
        <CardContent className="p-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search runbook title or root cause..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 bg-bg-elevated border-white/10 text-xs focus:border-brand-purple"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            <Filter className="h-4 w-4 text-muted-foreground mr-1" />
            <span className="text-xs text-muted-foreground font-mono">Severity:</span>
            {["ALL", "P0", "P1", "P2", "P3"].map((sev) => (
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

            <span className="text-xs text-muted-foreground font-mono ml-2">Status:</span>
            {["ALL", "Draft", "Approved", "Completed"].map((st) => (
              <button
                key={st}
                onClick={() => setSelectedStatus(st)}
                className={`px-2.5 py-1 rounded-full text-xs font-mono transition-colors ${
                  selectedStatus === st
                    ? "bg-brand-purple text-white font-bold"
                    : "bg-white/5 text-muted-foreground hover:text-white"
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Runbooks Directory List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {runbooks.map((rb) => (
          <Card
            key={rb.id}
            onClick={() => setSelectedRunbook(rb)}
            className="border border-white/10 bg-bg-surface/90 hover:border-brand-purple/50 transition-all duration-200 cursor-pointer shadow-lg hover:shadow-glow-blue flex flex-col justify-between"
          >
            <CardContent className="p-5 space-y-3">
              <div className="flex items-start justify-between gap-2">
                <Badge
                  className={
                    rb.severity === "P0"
                      ? "bg-red-950/60 text-red-400 border-red-500/40"
                      : rb.severity === "P1"
                      ? "bg-amber-950/60 text-amber-400 border-amber-500/40"
                      : "bg-blue-950/60 text-blue-400 border-blue-500/40"
                  }
                >
                  {rb.severity}
                </Badge>

                <Badge variant="outline" className="text-[10px] font-mono border-white/10">
                  {rb.status}
                </Badge>
              </div>

              <div>
                <h4 className="text-sm font-bold text-foreground line-clamp-2">{rb.title}</h4>
                <p className="text-xs text-muted-foreground font-mono mt-1">Service: {rb.service_name}</p>
              </div>

              <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                {rb.executive_summary}
              </p>

              <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[11px] font-mono text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Zap className="h-3.5 w-3.5 text-brand-purple" /> {rb.steps.length} Automation Steps
                </span>
                <span className="text-emerald-400 font-bold">Est: {rb.estimated_resolution_time}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Generate AI Runbook Modal */}
      <Dialog open={isGenerateOpen} onOpenChange={setIsGenerateOpen}>
        <DialogContent className="bg-bg-surface border-white/10 text-foreground max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-base font-bold">
              <Sparkles className="h-5 w-5 text-brand-purple" /> Generate SRE Remediation Runbook
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-2 font-sans text-xs">
            <div className="space-y-1">
              <label className="text-muted-foreground font-mono">Service Name</label>
              <Input
                value={genService}
                onChange={(e) => setGenService(e.target.value)}
                placeholder="e.g. api-gateway, auth-service"
                className="bg-bg-elevated border-white/10 text-xs"
              />
            </div>

            <div className="space-y-1">
              <label className="text-muted-foreground font-mono">Severity Level</label>
              <div className="flex gap-2">
                {(["P0", "P1", "P2", "P3"] as const).map((sev) => (
                  <button
                    key={sev}
                    onClick={() => setGenSeverity(sev)}
                    className={`flex-1 py-1.5 rounded text-xs font-mono font-bold border transition-colors ${
                      genSeverity === sev
                        ? "bg-brand-purple text-white border-brand-purple"
                        : "bg-white/5 border-white/10 text-muted-foreground"
                    }`}
                  >
                    {sev}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-muted-foreground font-mono">Custom Title (Optional)</label>
              <Input
                value={genTitle}
                onChange={(e) => setGenTitle(e.target.value)}
                placeholder="e.g. OOM Heap Dump Recovery Procedure"
                className="bg-bg-elevated border-white/10 text-xs"
              />
            </div>

            <Button
              disabled={generateMutation.isPending}
              onClick={() =>
                generateMutation.mutate({
                  service_name: genService,
                  severity: genSeverity,
                  title: genTitle || undefined,
                })
              }
              className="w-full bg-brand-purple hover:bg-brand-purple/90 text-white font-bold gap-2 text-xs h-10 mt-2"
            >
              <Sparkles className="h-4 w-4" />
              {generateMutation.isPending ? "Generating Runbook..." : "Generate AI Runbook"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Selected Runbook Detail Modal */}
      {selectedRunbook && (
        <Dialog open={!!selectedRunbook} onOpenChange={() => setSelectedRunbook(null)}>
          <DialogContent className="bg-bg-surface border-white/10 text-foreground max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <div className="flex items-center justify-between border-b border-white/10 pb-3 mr-6">
                <div className="flex items-center gap-2">
                  <Badge className="bg-brand-purple text-white">{selectedRunbook.severity}</Badge>
                  <DialogTitle className="text-base font-bold">{selectedRunbook.title}</DialogTitle>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExportMarkdown(selectedRunbook)}
                    className="gap-1.5 text-xs"
                  >
                    <Download className="h-3.5 w-3.5" /> Export MD
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handlePrint}
                    className="gap-1.5 text-xs"
                  >
                    <Printer className="h-3.5 w-3.5" /> Print
                  </Button>
                </div>
              </div>
            </DialogHeader>

            <div className="space-y-6 py-2 text-xs font-sans">
              {/* Metadata Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded-lg bg-bg-elevated/50 border border-white/5 font-mono text-[11px]">
                <div>
                  <span className="text-muted-foreground">Service:</span>
                  <p className="font-bold text-foreground">{selectedRunbook.service_name}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Est Resolution:</span>
                  <p className="font-bold text-emerald-400">{selectedRunbook.estimated_resolution_time}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Confidence:</span>
                  <p className="font-bold text-blue-400">{Math.round(selectedRunbook.confidence_score * 100)}%</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Status:</span>
                  <p className="font-bold text-brand-purple">{selectedRunbook.status}</p>
                </div>
              </div>

              {/* Executive Summary & Root Cause */}
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-white/5 border border-white/5 space-y-1">
                  <h4 className="font-bold text-foreground font-mono flex items-center gap-1.5">
                    <FileText className="h-4 w-4 text-brand-purple" /> Executive Summary
                  </h4>
                  <p className="text-muted-foreground leading-relaxed">{selectedRunbook.executive_summary}</p>
                </div>

                <div className="p-3 rounded-lg bg-red-950/20 border border-red-500/20 space-y-1">
                  <h4 className="font-bold text-red-400 font-mono flex items-center gap-1.5">
                    <AlertTriangle className="h-4 w-4" /> Root Cause Analysis
                  </h4>
                  <p className="text-muted-foreground leading-relaxed">{selectedRunbook.root_cause}</p>
                </div>
              </div>

              {/* Execution Controls & Approval */}
              <RunbookExecutionTimeline
                runbook={selectedRunbook}
                onApprove={() => approveMutation.mutate(selectedRunbook.id)}
                onExecute={() => executeMutation.mutate(selectedRunbook.id)}
                isApproving={approveMutation.isPending}
                isExecuting={executeMutation.isPending}
              />

              {/* Automation Steps */}
              <RunbookStepList steps={selectedRunbook.steps} />

              {/* Verification & Post Recovery Checklists */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {selectedRunbook.verification_checklist && (
                  <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-500/20 space-y-2">
                    <h5 className="font-bold text-emerald-400 font-mono text-xs flex items-center gap-1.5">
                      <ShieldCheck className="h-4 w-4" /> Verification Checklist
                    </h5>
                    <ul className="list-disc list-inside text-muted-foreground font-mono text-[11px] space-y-1">
                      {selectedRunbook.verification_checklist.map((v, i) => (
                        <li key={i}>{v}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedRunbook.post_recovery_checklist && (
                  <div className="p-3 rounded-lg bg-blue-950/20 border border-blue-500/20 space-y-2">
                    <h5 className="font-bold text-blue-400 font-mono text-xs flex items-center gap-1.5">
                      <CheckCircle2 className="h-4 w-4" /> Post-Recovery Action Items
                    </h5>
                    <ul className="list-disc list-inside text-muted-foreground font-mono text-[11px] space-y-1">
                      {selectedRunbook.post_recovery_checklist.map((p, i) => (
                        <li key={i}>{p}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
