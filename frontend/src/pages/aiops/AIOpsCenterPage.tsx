/**
 * Autonomous AIOps Agent & AI Operations Center — Main Dashboard Page
 */

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Sparkles,
  Bot,
  Brain,
  CheckCircle2,
  AlertTriangle,
  Search,
  Filter,
  Activity,
  Zap,
  Play,
  ShieldCheck,
} from "lucide-react";

import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/useToast";

import { aiopsService } from "@/services/aiopsService";
import { AIOpsAgentLoopCard } from "@/components/aiops/AIOpsAgentLoopCard";
import { AIOpsActionApprovalPanel } from "@/components/aiops/AIOpsActionApprovalPanel";
import type { AgentRecommendation } from "@/types/aiops";

export default function AIOpsCenterPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [selectedPriority, setSelectedPriority] = useState("ALL");
  const [selectedStatus, setSelectedStatus] = useState("ALL");
  const [selectedRec, setSelectedRec] = useState<AgentRecommendation | null>(null);

  // Queries
  const { data: agentStatus } = useQuery({
    queryKey: ["aiops-status"],
    queryFn: () => aiopsService.getAgentStatus(),
    refetchInterval: 5000,
  });

  const { data: recsData, isLoading } = useQuery({
    queryKey: ["aiops-recommendations", search, selectedCategory, selectedPriority, selectedStatus],
    queryFn: () =>
      aiopsService.getRecommendations({
        search: search || undefined,
        category: selectedCategory !== "ALL" ? selectedCategory : undefined,
        priority: selectedPriority !== "ALL" ? selectedPriority : undefined,
        status: selectedStatus !== "ALL" ? selectedStatus : undefined,
        size: 50,
      }),
  });

  // Trigger Analysis Mutation
  const analyzeMutation = useMutation({
    mutationFn: (target: string) => aiopsService.triggerAnalysis(target),
    onSuccess: (newRec) => {
      queryClient.invalidateQueries({ queryKey: ["aiops-recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["aiops-status"] });
      setSelectedRec(newRec);
      toast({
        title: "Agent Loop Executed",
        description: `New recommendation '${newRec.title}' generated with ${Math.round(newRec.confidence_score * 100)}% confidence.`,
      });
    },
  });

  // Approve / Reject Mutation
  const approveMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: "Approve" | "Reject" }) =>
      aiopsService.approveOrReject(id, action),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["aiops-recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["aiops-status"] });
      setSelectedRec(null);
      toast({
        title: updated.status === "Executed" ? "Action Executed" : "Action Rejected",
        description: `Recommendation '${updated.title}' is now ${updated.status}.`,
      });
    },
  });

  const recs = recsData?.items || [];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Autonomous AIOps Agent Center"
        subtitle="Continuous 6-phase autonomous observability loop (Observe ➔ Detect ➔ Analyze ➔ Plan ➔ Recommend ➔ Verify) with Explainable AI"
        actions={
          <Button
            disabled={analyzeMutation.isPending}
            onClick={() => analyzeMutation.mutate("All")}
            className="bg-brand-purple hover:bg-brand-purple/90 text-white gap-2 text-xs font-bold shadow-lg"
          >
            <Sparkles className={`h-4 w-4 ${analyzeMutation.isPending ? "animate-spin" : ""}`} />
            {analyzeMutation.isPending ? "Running Agent Loop..." : "Run Autonomous Cycle"}
          </Button>
        }
      />

      {/* Top Stat KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Live Agent Status"
          value={agentStatus?.status || "Autonomous"}
          subValue={`Current Phase: ${agentStatus?.current_phase || "Observe"}`}
        />
        <StatCard
          label="Pending Approvals"
          value={String(agentStatus?.pending_approvals || 2)}
          subValue="Action Queue"
        />
        <StatCard
          label="Total Insights"
          value={String(recsData?.total || 3)}
          subValue="Cross-Correlated Signals"
        />
        <StatCard
          label="Active Automations"
          value={String(agentStatus?.active_automations || 1)}
          subValue="Executed Actions"
        />
      </div>

      {/* 6-Phase Agent Loop Interactive Card */}
      <AIOpsAgentLoopCard
        status={agentStatus}
        onTriggerLoop={() => analyzeMutation.mutate("All")}
        isAnalyzing={analyzeMutation.isPending}
      />

      {/* Search & Filter Bar */}
      <Card className="border border-white/10 bg-bg-surface/80 backdrop-blur-md">
        <CardContent className="p-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search recommendations or root cause..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 bg-bg-elevated border-white/10 text-xs focus:border-brand-purple"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            <Filter className="h-4 w-4 text-muted-foreground mr-1" />
            <span className="text-xs text-muted-foreground font-mono">Priority:</span>
            {["ALL", "P0", "P1", "P2", "P3"].map((prio) => (
              <button
                key={prio}
                onClick={() => setSelectedPriority(prio)}
                className={`px-2.5 py-1 rounded-full text-xs font-mono transition-colors ${
                  selectedPriority === prio
                    ? "bg-brand-purple text-white font-bold"
                    : "bg-white/5 text-muted-foreground hover:text-white"
                }`}
              >
                {prio}
              </button>
            ))}

            <span className="text-xs text-muted-foreground font-mono ml-2">Status:</span>
            {["ALL", "Pending_Approval", "Executed"].map((st) => (
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

      {/* Recommendations Directory List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 font-sans text-xs">
        {recs.map((r) => (
          <Card
            key={r.id}
            onClick={() => setSelectedRec(r)}
            className="border border-white/10 bg-bg-surface/90 hover:border-brand-purple/50 transition-all duration-200 cursor-pointer shadow-lg hover:shadow-glow-blue flex flex-col justify-between"
          >
            <CardContent className="p-5 space-y-3">
              <div className="flex items-start justify-between gap-2">
                <Badge
                  className={
                    r.priority === "P0"
                      ? "bg-red-950/60 text-red-400 border-red-500/40"
                      : r.priority === "P1"
                      ? "bg-amber-950/60 text-amber-400 border-amber-500/40"
                      : "bg-blue-950/60 text-blue-400 border-blue-500/40"
                  }
                >
                  {r.priority}
                </Badge>

                <Badge
                  variant="outline"
                  className={
                    r.status === "Executed"
                      ? "bg-emerald-950/40 text-emerald-400 border-emerald-500/30"
                      : "bg-amber-950/40 text-amber-400 border-amber-500/30"
                  }
                >
                  {r.status}
                </Badge>
              </div>

              <div>
                <h4 className="text-sm font-bold text-foreground line-clamp-2">{r.title}</h4>
                <p className="text-xs text-muted-foreground font-mono mt-1">Category: {r.category}</p>
              </div>

              <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                {r.executive_summary}
              </p>

              <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[11px] font-mono text-muted-foreground">
                <span className="flex items-center gap-1 text-emerald-400 font-bold">
                  <Brain className="h-3.5 w-3.5" /> Confidence: {Math.round(r.confidence_score * 100)}%
                </span>
                <span>Est Fix: {r.expected_recovery_time}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Action Approval Drawer */}
      <AIOpsActionApprovalPanel
        recommendation={selectedRec}
        onClose={() => setSelectedRec(null)}
        onApprove={(id) => approveMutation.mutate({ id, action: "Approve" })}
        onReject={(id) => approveMutation.mutate({ id, action: "Reject" })}
        isProcessing={approveMutation.isPending}
      />
    </div>
  );
}
