/**
 * Edit Incident Modal Form Component
 */

import React, { useState, useEffect } from "react";
import { Edit3, X, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Incident, IncidentUpdatePayload, SeverityLevel, PriorityLevel, IncidentStatus } from "@/types/incident";

interface EditIncidentModalProps {
  incident: Incident | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (id: string, payload: IncidentUpdatePayload) => Promise<void>;
  isSubmitting: boolean;
}

export const EditIncidentModal: React.FC<EditIncidentModalProps> = ({
  incident,
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
  const [affectedRegion, setAffectedRegion] = useState("us-east-1");
  const [assignedEngineer, setAssignedEngineer] = useState("");

  useEffect(() => {
    if (incident) {
      setTitle(incident.title || "");
      setDescription(incident.description || "");
      setSeverity(incident.severity || "P2");
      setPriority(incident.priority || "High");
      setStatus(incident.status || "Open");
      setAffectedService(incident.affected_service || "api-gateway");
      setAffectedRegion(incident.affected_region || "us-east-1");
      setAssignedEngineer(incident.assigned_engineer || incident.assigned_to || "");
    }
  }, [incident]);

  if (!isOpen || !incident) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(incident.id, {
      title,
      description,
      severity,
      priority,
      status,
      affected_service: affectedService,
      affected_region: affectedRegion,
      assigned_engineer: assignedEngineer || undefined,
      assigned_to: assignedEngineer || undefined,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-bg-surface border border-white/10 rounded-xl shadow-2xl overflow-hidden text-xs">
        {/* Header */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-bg-elevated/40">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-brand-blue/20 text-brand-blue border border-brand-blue/30">
              <Edit3 className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-foreground">Edit Incident Details</h2>
              <p className="text-[11px] text-muted-foreground">ID: {incident.id.slice(0, 8)}</p>
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
          <div>
            <label className="block text-foreground font-medium mb-1">Title</label>
            <Input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="bg-bg-elevated/60 border-white/10 text-xs focus:border-brand-blue"
            />
          </div>

          <div>
            <label className="block text-foreground font-medium mb-1">Description</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-blue"
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-foreground font-medium mb-1">Severity</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value as SeverityLevel)}
                className="w-full h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-blue"
              >
                <option value="P0">P0 — Critical</option>
                <option value="P1">P1 — High</option>
                <option value="P2">P2 — Medium</option>
                <option value="P3">P3 — Low</option>
              </select>
            </div>

            <div>
              <label className="block text-foreground font-medium mb-1">Priority</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as PriorityLevel)}
                className="w-full h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-blue"
              >
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-foreground font-medium mb-1">Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as IncidentStatus)}
                className="w-full h-9 px-3 rounded-md bg-bg-elevated/60 border border-white/10 text-xs text-foreground focus:outline-none focus:border-brand-blue"
              >
                <option value="Open">Open</option>
                <option value="Investigating">Investigating</option>
                <option value="Monitoring">Monitoring</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-foreground font-medium mb-1">Affected Service</label>
              <Input
                type="text"
                value={affectedService}
                onChange={(e) => setAffectedService(e.target.value)}
                className="bg-bg-elevated/60 border-white/10 text-xs focus:border-brand-blue"
              />
            </div>

            <div>
              <label className="block text-foreground font-medium mb-1">Region</label>
              <Input
                type="text"
                value={affectedRegion}
                onChange={(e) => setAffectedRegion(e.target.value)}
                className="bg-bg-elevated/60 border-white/10 text-xs focus:border-brand-blue"
              />
            </div>

            <div>
              <label className="block text-foreground font-medium mb-1">Assigned Engineer</label>
              <Input
                type="text"
                value={assignedEngineer}
                onChange={(e) => setAssignedEngineer(e.target.value)}
                className="bg-bg-elevated/60 border-white/10 text-xs focus:border-brand-blue"
              />
            </div>
          </div>

          <div className="pt-2 flex items-center justify-end gap-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isSubmitting} className="bg-brand-blue hover:bg-brand-blue/90 text-white gap-1.5">
              {isSubmitting ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
