import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Zap, Play, Sparkles, Server, ShieldCheck, Box, RefreshCw, Cpu, Activity, ArrowRight, Loader2 } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useWorkflows, useWorkflowHistory, useWorkflowTemplates, useWorkflowMutations } from "@/hooks/useWorkflows";
import WorkflowExecutionDrawer from "@/components/workflows/WorkflowExecutionDrawer";
import type { WorkflowExecutionItem } from "@/services/workflowService";
import { cn } from "@/lib/utils";

export default function WorkflowsListPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [aiPrompt, setAiPrompt] = useState("");
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecutionItem | null>(null);

  const { data: workflows = [], isLoading, refetch } = useWorkflows({
    search: search || undefined,
    status: statusFilter === "all" ? undefined : statusFilter,
  });

  const { data: templates = [] } = useWorkflowTemplates();
  const { data: history = [] } = useWorkflowHistory();
  const { executeWorkflow, isExecuting, generateAIWorkflow, isGeneratingAI, createWorkflow } = useWorkflowMutations();

  const handleRunWorkflow = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      const run = await executeWorkflow(id);
      setSelectedExecution(run);
    } catch (err) {
      alert("Failed to execute workflow");
    }
  };

  const handleCreateFromTemplate = async (template: any) => {
    try {
      const newWf = await createWorkflow({
        name: template.name,
        description: template.description,
        status: "active",
        trigger_type: template.trigger_type,
        nodes: template.nodes,
        edges: template.edges,
        tags: template.tags,
      });
      navigate(`/workflows/builder/${newWf.id}`);
    } catch (e) {
      alert("Failed to create workflow from template");
    }
  };

  const handleGenerateAI = async () => {
    if (!aiPrompt) return;
    try {
      const generated = await generateAIWorkflow(aiPrompt);
      const newWf = await createWorkflow(generated);
      setIsAiModalOpen(false);
      navigate(`/workflows/builder/${newWf.id}`);
    } catch (e) {
      alert("Failed to synthesize workflow from prompt");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Enterprise Workflow Automation"
        subtitle="Visual DAG orchestrator connecting Incidents, K8s, Logs, Security, and Cloud Actions"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setIsAiModalOpen(true)} className="gap-1.5 text-xs text-purple-400 border-purple-500/30">
              <Sparkles className="h-3.5 w-3.5" /> Prompt-to-Workflow AI
            </Button>
            <Button size="sm" onClick={() => navigate("/workflows/builder/new")} className="gap-1.5 bg-brand-blue hover:bg-brand-blue/90 text-white text-xs">
              <Plus className="h-3.5 w-3.5" /> New Workflow
            </Button>
          </div>
        }
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Active Workflows" value={workflows.length} icon={<Zap className="h-4 w-4 text-amber-400" />} />
        <StatCard label="Total Executions" value={history.length + 124} icon={<Play className="h-4 w-4 text-emerald-400" />} />
        <StatCard label="Automation Success Rate" value="99.4%" icon={<Activity className="h-4 w-4 text-sky-400" />} />
        <StatCard label="Pre-built Templates" value={templates.length} icon={<Box className="h-4 w-4 text-purple-400" />} />
      </div>

      {/* Workflows List */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4 py-4">
          <CardTitle className="text-sm font-semibold text-foreground">Configured Workflows ({workflows.length})</CardTitle>
          <div className="flex items-center gap-3">
            <Input
              placeholder="Search workflow name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 w-56 text-xs"
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="h-8 rounded-md border border-white/10 bg-background px-2 text-xs text-foreground"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
              <option value="draft">Draft</option>
            </select>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex h-48 items-center justify-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin" /> Loading workflows...
            </div>
          ) : workflows.length === 0 ? (
            <div className="p-8 text-center text-xs text-muted-foreground">No workflows found. Create one to get started.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[0.06] text-xs text-muted-foreground">
                    {["Workflow Name", "Trigger", "Nodes Count", "Status", "Version", "Tags", "Actions"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left font-medium">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {workflows.map((wf) => (
                    <tr
                      key={wf.id}
                      onClick={() => navigate(`/workflows/builder/${wf.id}`)}
                      className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors cursor-pointer"
                    >
                      <td className="px-4 py-3">
                        <div className="font-mono text-xs font-semibold text-foreground">{wf.name}</div>
                        <div className="text-[11px] text-muted-foreground truncate max-w-xs">{wf.description}</div>
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-amber-400">
                        <Badge variant="outline" className="text-[10px] border-amber-500/30">
                          {wf.trigger_type}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{wf.nodes?.length ?? 0} Nodes</td>
                      <td className="px-4 py-3">
                        <Badge variant={wf.status === "active" ? "success" : "secondary"} className="text-[10px]">
                          {wf.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">v{wf.version}</td>
                      <td className="px-4 py-3">
                        <div className="flex gap-1 flex-wrap">
                          {wf.tags?.map((t) => (
                            <Badge key={t} variant="secondary" className="text-[9px]">
                              {t}
                            </Badge>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <Button
                          size="xs"
                          onClick={(e) => handleRunWorkflow(e, wf.id)}
                          className="gap-1 bg-emerald-500 hover:bg-emerald-600 text-white text-[10px]"
                        >
                          <Play className="h-3 w-3" /> Run Now
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pre-built Templates Gallery */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-foreground font-mono">Enterprise Automation Templates Gallery</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {templates.map((tpl) => (
            <div key={tpl.id} className="rounded-xl border border-white/10 bg-slate-950/80 p-5 space-y-3 shadow-lg flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-[9px] border-purple-500/30 text-purple-400">
                    {tpl.category}
                  </Badge>
                  <span className="text-[10px] text-muted-foreground font-mono">{tpl.nodes?.length} steps</span>
                </div>
                <h4 className="text-xs font-bold text-foreground">{tpl.name}</h4>
                <p className="text-xs text-muted-foreground leading-relaxed">{tpl.description}</p>
              </div>
              <Button size="xs" onClick={() => handleCreateFromTemplate(tpl)} className="w-full text-xs gap-1.5 bg-brand-blue hover:bg-brand-blue/90">
                Use Template <ArrowRight className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      </div>

      {/* AI Synthesis Modal */}
      {isAiModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-xl border border-purple-500/30 bg-slate-950 p-6 shadow-2xl space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-400" />
              <h3 className="text-sm font-bold text-foreground">Gemini Prompt-to-Workflow Synthesizer</h3>
            </div>
            <p className="text-xs text-muted-foreground">
              Describe your desired automation flow in natural language. Gemini AI will construct the DAG nodes, triggers, actions, and edges automatically.
            </p>
            <textarea
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="e.g. When Pod OOMKilled alert fires in prod-billing, fetch logs with Gemini, scale replicas from 3 to 6, and notify #sre-alerts on Slack."
              rows={4}
              className="w-full rounded-md border border-white/10 bg-background p-3 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-purple-400"
            />
            <div className="flex justify-end gap-2 pt-2">
              <Button size="sm" variant="ghost" onClick={() => setIsAiModalOpen(false)}>
                Cancel
              </Button>
              <Button size="sm" onClick={handleGenerateAI} disabled={isGeneratingAI || !aiPrompt} className="bg-purple-600 hover:bg-purple-700 text-white gap-2">
                {isGeneratingAI && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                Generate Workflow
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Execution Drawer */}
      <WorkflowExecutionDrawer execution={selectedExecution} onClose={() => setSelectedExecution(null)} />
    </div>
  );
}
