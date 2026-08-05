/**
 * InviteMemberModal Component — User invitation modal dialog with RBAC role selector.
 */

import React, { useState } from "react";
import { UserPlus, Mail, Shield, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface InviteMemberModalProps {
  isOpen: boolean;
  onClose: () => void;
  onInvite: (email: string, role: string) => void;
  isInviting?: boolean;
}

const roles = [
  { name: "Admin", desc: "Full administrative access except billing ownership" },
  { name: "Manager", desc: "Access to incident management, log analytics & AI" },
  { name: "Engineer", desc: "Access to dashboards, metrics, traces, and incident response" },
  { name: "Viewer", desc: "Read-only access to monitoring dashboards and logs" },
];

export const InviteMemberModal: React.FC<InviteMemberModalProps> = ({
  isOpen,
  onClose,
  onInvite,
  isInviting,
}) => {
  const [email, setEmail] = useState("");
  const [selectedRole, setSelectedRole] = useState("Engineer");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    onInvite(email, selectedRole);
    setEmail("");
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-bg-surface border-white/10 text-foreground max-w-md font-sans text-xs">
        <DialogHeader>
          <div className="flex items-center gap-2.5 border-b border-white/10 pb-3 mr-6">
            <div className="h-8 w-8 rounded-lg bg-brand-purple/20 border border-brand-purple/30 text-brand-purple flex items-center justify-center">
              <UserPlus className="h-4 w-4" />
            </div>
            <DialogTitle className="text-base font-bold">Invite Team Member</DialogTitle>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          {/* Email Input */}
          <div className="space-y-1.5">
            <label className="text-xs font-mono text-muted-foreground">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                type="email"
                required
                placeholder="colleague@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-9 bg-bg-elevated border-white/10 text-xs focus:border-brand-purple"
              />
            </div>
          </div>

          {/* Role Selection */}
          <div className="space-y-2">
            <label className="text-xs font-mono text-muted-foreground">Select RBAC Role</label>
            <div className="space-y-1.5">
              {roles.map((r) => {
                const isSelected = selectedRole === r.name;
                return (
                  <button
                    key={r.name}
                    type="button"
                    onClick={() => setSelectedRole(r.name)}
                    className={`w-full p-2.5 rounded-xl border text-left flex items-start justify-between transition-all ${
                      isSelected
                        ? "bg-brand-purple/20 border-brand-purple text-foreground shadow-sm"
                        : "bg-white/5 border-white/5 text-muted-foreground hover:bg-white/10"
                    }`}
                  >
                    <div>
                      <p className="font-bold text-xs text-foreground font-mono">{r.name}</p>
                      <p className="text-[10px] text-muted-foreground">{r.desc}</p>
                    </div>
                    {isSelected && <Check className="h-4 w-4 text-brand-purple shrink-0 mt-0.5" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Buttons */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/10">
            <Button variant="outline" type="button" onClick={onClose} className="text-xs">
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isInviting || !email}
              className="bg-brand-purple hover:bg-brand-purple/90 text-white font-bold text-xs"
            >
              {isInviting ? "Sending Invite..." : "Send Member Invitation"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
