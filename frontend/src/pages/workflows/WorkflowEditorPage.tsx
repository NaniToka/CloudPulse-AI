import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Save, Play, Plus, Zap, UserCheck, Sparkles, AlertTriangle, ShieldCheck, Box, RefreshCw, Loader2 } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import WorkflowCanvas from "@/components/workflows/WorkflowCanvas";
import WorkflowNodeProperties from "@/components/workflows/WorkflowNodeProperties";
import WorkflowExecutionDrawer from "@/components/workflows/WorkflowExecutionDrawer";
import { useWorkflowDetails, useWorkflowMutations } from "@/hooks/useWorkflows";
import type { WorkflowExecutionItem } from "@/services/workflowService";

export default function WorkflowEditorPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNew = id === "new";

  const { data: workflow, isLoading } = useWorkflowDetails(isNew ? undefined : id);
  const { createWorkflow, updateWorkflow, executeWorkflow, isExecuting } = useWorkflowMutations();

  const [name, setName] = useState("New Automated Workflow");
  const [nodes, setNodes] = useState<any[]>([
    { id: "node-1", type: "trigger", label: "Incident Created Trigger", position: { x: 100, y: 150 }, config: { action_type: "incident_created" } },
    { id: "node-2", type: "ai", label: "Gemini AI Log Diagnosis", position: { x: 350, y: 150 }, config: { action_type: "gemini_diagnosis" } },
    { id: "node-3", type: "action", label: "Dispatch Slack Notification", position: { x: 600, y: 150 }, config: { action_type: "slack_message" } },
  ]);
  const [edges, setEdges] = useState<any[]>([
    { id: "e1-2", source: "node-1", target: "node-2" },
    { id: "e2-3", source: "node-2", target: "node-3" },
  ]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [executionRun, setExecutionRun] = useState<WorkflowExecutionItem | null>(null);

  useEffect(() => {
    if (workflow) {
      setName(workflow.name);
      if (workflow.nodes?.length) setNodes(workflow.nodes);
      if (workflow.edges?.length) setEdges(workflow.edges);
    }
  }, [workflow]);

  const selectedNode = nodes.find((n) => n.id === selectedNodeId) || null;

  const handleAddNode = (type: string, label: string) => {
    const newId = `node-${nodes.length + 1}`;
    const newNode = { id: newId, type, label, position: { x: 100 * (nodes.length + 1), y: 150 } };
    setNodes([...nodes, newNode]);
    if (nodes.length > 0) {
      const lastNode = nodes[nodes.length - 1];
      setEdges([...edges, { id: `e-${lastNode.id}-${newId}`, source: lastNode.id, target: newId }]);
    }
  };

  const handleSave = async () => {
    try {
      if (isNew) {
        const created = await createWorkflow({
          name,
          nodes,
          edges,
          trigger_type: nodes[0]?.config?.action_type || "manual",
          status: "active",
          tags: ["workflow", "automation"],
        });
        navigate(`/workflows/builder/${created.id}`);
      } else if (id) {
        await updateWorkflow({
          id,
          payload: { name, nodes, edges },
        });
        alert("Workflow saved successfully!");
      }
    } catch (e) {
      alert("Failed to save workflow");
    }
  };

  const handleTestRun = async () => {
    if (isNew || !id) {
      alert("Please save the workflow before running test execution.");
      return;
    }
    try {
      const res = await executeWorkflow(id);
      setExecutionRun(res);
    } catch (e) {
      alert("Failed to run workflow");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate("/workflows")} className="gap-1 text-xs">
            <ArrowLeft className="h-4 w-4" /> Back
          </Button>
          <div>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="h-8 font-mono text-sm font-bold text-foreground border-white/10 bg-transparent w-72"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={handleTestRun} disabled={isExecuting} className="gap-1.5 text-xs text-emerald-400 border-emerald-500/30">
            {isExecuting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
            Test Run
          </Button>
          <Button size="sm" onClick={handleSave} className="gap-1.5 bg-brand-blue hover:bg-brand-blue/90 text-white text-xs">
            <Save className="h-3.5 w-3.5" /> Save Workflow
          </Button>
        </div>
      </div>

      {/* Action & Trigger Palette bar */}
      <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-950 p-3 overflow-x-auto text-xs">
        <span className="text-[10px] uppercase font-mono text-muted-foreground mr-2 font-bold">Add Step:</span>
        <Button size="xs" variant="outline" onClick={() => handleAddNode("trigger", "Webhook Trigger")} className="gap-1 text-amber-400 border-amber-500/30 text-[11px]">
          <Zap className="h-3 w-3" /> + Trigger
        </Button>
        <Button size="xs" variant="outline" onClick={() => handleAddNode("action", "Scale K8s Deployment")} className="gap-1 text-sky-400 border-sky-500/30 text-[11px]">
          <Play className="h-3 w-3" /> + K8s Action
        </Button>
        <Button size="xs" variant="outline" onClick={() => handleAddNode("ai", "Gemini AI Synthesis")} className="gap-1 text-emerald-400 border-emerald-500/30 text-[11px]">
          <Sparkles className="h-3 w-3" /> + Gemini AI
        </Button>
        <Button size="xs" variant="outline" onClick={() => handleAddNode("approval", "SRE Approval Gate")} className="gap-1 text-purple-400 border-purple-500/30 text-[11px]">
          <UserCheck className="h-3 w-3" /> + Approval Gate
        </Button>
      </div>

      {/* Main Canvas Area */}
      <div className="flex gap-6">
        <div className="flex-1">
          <WorkflowCanvas
            nodes={nodes}
            edges={edges}
            selectedNodeId={selectedNodeId}
            onSelectNode={(id) => setSelectedNodeId(id)}
          />
        </div>

        {/* Node Properties Panel */}
        {selectedNode && (
          <WorkflowNodeProperties node={selectedNode} onClose={() => setSelectedNodeId(null)} />
        )}
      </div>

      {/* Execution Drawer */}
      <WorkflowExecutionDrawer execution={executionRun} onClose={() => setExecutionRun(null)} />
    </div>
  );
}
