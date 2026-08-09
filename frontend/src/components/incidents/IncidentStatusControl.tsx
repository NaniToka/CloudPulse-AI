import React, { useState } from "react";
import {
  CheckCircle2,
  Clock,
  Eye,
  Flame,
  RotateCcw,
  Search,
  ShieldCheck,
  Wrench,
  XCircle,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import type { IncidentStatus } from "@/types/incident";

interface Props {
  status: IncidentStatus | string;
  onAcknowledge?: () => void;
  onStatusChange?: (newStatus: string) => void;
  onResolve?: (notes: string) => void;
  isLoading?: boolean;
}

export function IncidentStatusControl({
  status,
  onAcknowledge,
  onStatusChange,
  onResolve,
  isLoading = false,
}: Props) {
  const [isResolveModalOpen, setIsResolveModalOpen] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState("");

  const norm = String(status).toUpperCase();

  const getStatusBadge = () => {
    switch (norm) {
      case "DETECTED":
        return (
          <Badge className="bg-red-500/15 text-red-400 border-red-500/30 text-xs font-mono flex items-center gap-1.5">
            <Flame className="w-3.5 h-3.5" /> DETECTED
          </Badge>
        );
      case "INVESTIGATING":
      case "OPEN":
        return (
          <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 text-xs font-mono flex items-center gap-1.5">
            <Search className="w-3.5 h-3.5" /> INVESTIGATING
          </Badge>
        );
      case "IDENTIFIED":
        return (
          <Badge className="bg-cyan-500/15 text-cyan-400 border-cyan-500/30 text-xs font-mono flex items-center gap-1.5">
            <Eye className="w-3.5 h-3.5" /> ROOT CAUSE IDENTIFIED
          </Badge>
        );
      case "MITIGATING":
      case "MONITORING":
        return (
          <Badge className="bg-blue-500/15 text-blue-400 border-blue-500/30 text-xs font-mono flex items-center gap-1.5">
            <Wrench className="w-3.5 h-3.5" /> MITIGATING
          </Badge>
        );
      case "RESOLVED":
        return (
          <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 text-xs font-mono flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" /> RESOLVED
          </Badge>
        );
      case "CLOSED":
        return (
          <Badge className="bg-slate-500/15 text-slate-400 border-slate-500/30 text-xs font-mono flex items-center gap-1.5">
            <XCircle className="w-3.5 h-3.5" /> CLOSED
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const handleConfirmResolve = () => {
    if (!resolutionNotes.trim() || !onResolve) return;
    onResolve(resolutionNotes.trim());
    setIsResolveModalOpen(false);
    setResolutionNotes("");
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      {/* Current Status Pill */}
      {getStatusBadge()}

      {/* Action Buttons based on lifecycle */}
      {norm === "DETECTED" && onAcknowledge && (
        <Button
          size="sm"
          onClick={onAcknowledge}
          disabled={isLoading}
          className="h-8 text-xs font-mono bg-amber-600 hover:bg-amber-500 text-white"
        >
          <Search className="w-3.5 h-3.5 mr-1" />
          Acknowledge & Investigate
        </Button>
      )}

      {(norm === "INVESTIGATING" || norm === "IDENTIFIED" || norm === "OPEN") && onStatusChange && (
        <Button
          size="sm"
          onClick={() => onStatusChange("MITIGATING")}
          disabled={isLoading}
          className="h-8 text-xs font-mono bg-blue-600 hover:bg-blue-500 text-white"
        >
          <Wrench className="w-3.5 h-3.5 mr-1" />
          Start Mitigation
        </Button>
      )}

      {norm !== "RESOLVED" && norm !== "CLOSED" && onResolve && (
        <Button
          size="sm"
          onClick={() => setIsResolveModalOpen(true)}
          disabled={isLoading}
          className="h-8 text-xs font-mono bg-emerald-600 hover:bg-emerald-500 text-white"
        >
          <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
          Resolve Incident
        </Button>
      )}

      {norm === "RESOLVED" && onStatusChange && (
        <Button
          size="sm"
          variant="outline"
          onClick={() => onStatusChange("CLOSED")}
          disabled={isLoading}
          className="h-8 text-xs font-mono border-white/20 text-muted-foreground hover:text-white"
        >
          <XCircle className="w-3.5 h-3.5 mr-1" />
          Close Incident
        </Button>
      )}

      {/* Resolve Dialog */}
      <Dialog open={isResolveModalOpen} onOpenChange={setIsResolveModalOpen}>
        <DialogContent className="sm:max-w-[480px] bg-bg-surface border-white/[0.1] text-white">
          <DialogHeader>
            <DialogTitle className="text-base font-mono flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Resolve Incident
            </DialogTitle>
            <DialogDescription className="text-xs text-muted-foreground font-mono">
              Provide resolution summary, fix actions applied, and preventive notes for post-mortem analysis.
            </DialogDescription>
          </DialogHeader>

          <div className="my-2">
            <Textarea
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
              placeholder="e.g. Scaled PostgreSQL connection pool to 500 and restarted leaking worker pods. p99 latency returned to <120ms baseline."
              className="text-xs font-mono min-h-[100px] bg-bg-surface border-white/[0.1]"
            />
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsResolveModalOpen(false)}
              className="border-white/[0.1] text-xs font-mono"
            >
              Cancel
            </Button>
            <Button
              size="sm"
              disabled={!resolutionNotes.trim() || isLoading}
              onClick={handleConfirmResolve}
              className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono"
            >
              Submit Resolution
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
