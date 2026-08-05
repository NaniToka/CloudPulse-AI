/**
 * Create Incident Modal Form Component
 * Modern dialog with validation, engineer assignment, priority, severity, and affected service select.
 */

import React, { useState } from "react";
import { ShieldAlert, Sparkles, X, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import type { IncidentCreatePayload, SeverityLevel, PriorityLevel, IncidentStatus } from "@/types/incident";

interface CreateIncidentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: IncidentCreatePayload) => Promise<void>;
  isSubmitting: boolean;
}

export const CreateIncidentModal: React.FC<CreateIncidentModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
}) => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState<SeverityLevel>("P2");
  const [priority, setPriority] = useState<PriorityLevel>("High");
  const [status, setStatus] = useState<IncidentStatus>("Open");
  const [affectedService, setAffectedService] = useState("api-gateway");
  const [assignedEngineer, setAssignedEngineer] = useState("");
  const [autoAnalyze, setAutoAnalyze] = useState(true);
  const [errors, setErrors] = useState<Record<string, string>>({});

  if (!isOpen) return null;

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!title.trim() || title.length < 3) {
      errs.title = "Title must be at least 3 characters long.";
    }
    if (!affectedService.trim()) {
      errs.affectedService = "Please specify an affected service.";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    await onSubmit({
      title,
      description,
      severity,
      priority,
      status,
      affected_service: affectedService,
      assigned_engineer: assignedEngineer || undefined,
      auto_analyze: autoAnalyze,
    });

    // Reset form
    setTitle("");
    setDescription("");
    setSeverity("P2");
    setPriority("High");
    setAffectedService("api-gateway");
    setAssignedEngineer("");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-bg-surface border border-white/10 rounded-xl shadow-2xl overflow-hidden text-xs">
        {/* Header */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-bg-elevated/40">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-brand-purple/20 text-brand-purple border border-brand-purple/30">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-foreground">Open New Incident</h2>
              <p className="text-[11px] text-muted-foreground">
                Trigger incident triage with automated Gemini AI diagnostic analysis
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-white/10 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Title */}
          <div>
            <label className="block text-foreground font-medium mb-1">
              Incident Title <span className="text-red-400">*</span>
            </label>
            <Input
              type="text"
              placeholder="e.g. Latency Spike on Auth Token Verification"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="bg-bg-elevated/60 border-white/10 text-xs focus:border-brand-purple"
            />
            {errors.title && <p className="text-red-400 text-[11px] mt-1">{errors.title}</p>}
          </div>

          {/* Description */}
          <div>
            <label className="block text-foreground font-medium mb-1">Description / Error Log Context</label>
            <textarea
              rows={3}
              placeholder="Provide symptoms, stack trace snippets, or anomaly details..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-purple"
            />
          </div>

          {/* Grid fields */}
          <div className="grid grid-cols-2 gap-4">
            {/* Severity */}
            <div>
              <label className="block text-foreground font-medium mb-1">Severity</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value as SeverityLevel)}
                className="w-full h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-purple"
              >
                <option value="P0">P0 — Critical Outage</option>
                <option value="P1">P1 — Severe Degradation</option>
                <option value="P2">P2 — Moderate Impact</option>
                <option value="P3">P3 — Low Severity</option>
              </select>
            </div>

            {/* Priority */}
            <div>
              <label className="block text-foreground font-medium mb-1">Priority</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as PriorityLevel)}
                className="w-full h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-purple"
              >
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Affected Service */}
            <div>
              <label className="block text-foreground font-medium mb-1">Affected Service</label>
              <select
                value={affectedService}
                onChange={(e) => setAffectedService(e.target.value)}
                className="w-full h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-purple"
              >
                <option value="api-gateway">api-gateway</option>
                <option value="auth-service">auth-service</option>
                <option value="payment-service">payment-service</option>
                <option value="database-cluster">database-cluster</option>
                <option value="storage-service">storage-service</option>
                <option value="kafka-ingestion">kafka-ingestion</option>
              </select>
            </div>

            {/* Assign Engineer */}
            <div>
              <label className="block text-foreground font-medium mb-1">Assign Engineer</label>
              <input
                type="text"
                placeholder="e.g. Sarah Chen (SRE)"
                value={assignedEngineer}
                onChange={(e) => setAssignedEngineer(e.target.value)}
                className="w-full h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-purple"
              />
            </div>
          </div>

          {/* AI Toggle */}
          <div className="p-3 rounded-lg bg-brand-purple/10 border border-brand-purple/20 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-brand-purple" />
              <div>
                <span className="font-semibold text-foreground">Google Gemini Auto-Analysis</span>
                <p className="text-[10px] text-muted-foreground">Generates root cause & resolution plan immediately</p>
              </div>
            </div>
            <input
              type="checkbox"
              checked={autoAnalyze}
              onChange={(e) => setAutoAnalyze(e.target.checked)}
              className="h-4 w-4 rounded accent-brand-purple cursor-pointer"
            />
          </div>

          {/* Footer */}
          <div className="pt-2 flex items-center justify-end gap-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting} className="bg-brand-purple hover:bg-brand-purple/90 text-white gap-1.5">
              {isSubmitting ? (
                <>Creating & Analyzing...</>
              ) : (
                <>
                  <Plus className="h-3.5 w-3.5" /> Create Incident
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
