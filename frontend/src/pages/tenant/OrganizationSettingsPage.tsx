/**
 * OrganizationSettingsPage — Main Enterprise Multi-Tenant SaaS Workspace & Team Management Page.
 */

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Building2,
  Users,
  UserPlus,
  Shield,
  FolderKanban,
  CheckCircle2,
  Lock,
  Sparkles,
} from "lucide-react";

import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/useToast";

import { tenantService } from "@/services/tenantService";
import { PermissionMatrix } from "@/components/tenant/PermissionMatrix";
import { InviteMemberModal } from "@/components/tenant/InviteMemberModal";
import { TeamManagementCard } from "@/components/tenant/TeamManagementCard";
import { AuditLogTimeline } from "@/components/tenant/AuditLogTimeline";

export default function OrganizationSettingsPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);

  // Fetch User Organizations
  const { data: orgs = [] } = useQuery({
    queryKey: ["organizations"],
    queryFn: () => tenantService.getOrganizations(),
  });

  const currentOrg = orgs[0] || null;
  const orgId = currentOrg?.id || "";

  // Queries for details
  const { data: members = [] } = useQuery({
    queryKey: ["members", orgId],
    queryFn: () => tenantService.getMembers(orgId),
    enabled: !!orgId,
  });

  const { data: teams = [] } = useQuery({
    queryKey: ["teams", orgId],
    queryFn: () => tenantService.getTeams(orgId),
    enabled: !!orgId,
  });

  const { data: projects = [] } = useQuery({
    queryKey: ["projects", orgId],
    queryFn: () => tenantService.getProjects(orgId),
    enabled: !!orgId,
  });

  const { data: auditLogs = [] } = useQuery({
    queryKey: ["audit-logs", orgId],
    queryFn: () => tenantService.getAuditLogs(orgId),
    enabled: !!orgId,
  });

  const { data: permMatrix } = useQuery({
    queryKey: ["permissions-matrix"],
    queryFn: () => tenantService.getPermissionsMatrix(),
  });

  // Mutations
  const inviteMutation = useMutation({
    mutationFn: ({ email, role }: { email: string; role: string }) =>
      tenantService.inviteMember(orgId, email, role),
    onSuccess: (inv) => {
      queryClient.invalidateQueries({ queryKey: ["audit-logs", orgId] });
      setIsInviteModalOpen(false);
      toast({
        title: "Member Invitation Sent",
        description: `Invitation sent to '${inv.email}' with role '${inv.role}'.`,
      });
    },
  });

  const createTeamMutation = useMutation({
    mutationFn: ({ name, desc }: { name: string; desc?: string }) =>
      tenantService.createTeam(orgId, name, desc),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["teams", orgId] });
      toast({ title: "Team Created", description: "New team created successfully." });
    },
  });

  const createProjMutation = useMutation({
    mutationFn: ({ name, provider, env }: { name: string; provider: string; env: string }) =>
      tenantService.createProject(orgId, name, provider, env),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects", orgId] });
      toast({ title: "Project Created", description: "New workspace project created successfully." });
    },
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Organization & Workspace Settings"
        subtitle="Manage multi-tenant SaaS organization structure, teams, workspace projects, invitations, and RBAC permission matrices"
        actions={
          <Button
            onClick={() => setIsInviteModalOpen(true)}
            className="bg-brand-purple hover:bg-brand-purple/90 text-white gap-2 text-xs font-bold shadow-lg"
          >
            <UserPlus className="h-4 w-4" /> Invite Team Member
          </Button>
        }
      />

      {/* Top Stat KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Organization Name"
          value={currentOrg?.name || "CloudPulse Global Corp"}
          subValue={`Slug: ${currentOrg?.slug || "cloudpulse"}`}
        />
        <StatCard
          label="Active Plan"
          value={currentOrg?.plan || "Enterprise"}
          subValue="SaaS License"
        />
        <StatCard
          label="Total Members"
          value={String(members.length || 1)}
          subValue="Active Users"
        />
        <StatCard
          label="Workspace Projects"
          value={String(projects.length || 1)}
          subValue="Isolated Clusters"
        />
      </div>

      {/* Organization Members Directory */}
      <div className="p-5 rounded-2xl bg-bg-surface/90 border border-white/10 shadow-2xl space-y-4 font-sans text-xs">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-brand-purple" />
            <h3 className="text-sm font-bold text-foreground">Organization Members Directory</h3>
          </div>
          <Badge variant="outline" className="font-mono text-[10px]">
            {members.length} Members
          </Badge>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse font-mono text-xs">
            <thead>
              <tr className="border-b border-white/10 text-muted-foreground text-left">
                <th className="py-2 px-3">User Email</th>
                <th className="py-2 px-3">Name</th>
                <th className="py-2 px-3">RBAC Role</th>
                <th className="py-2 px-3">Joined Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {members.map((m) => (
                <tr key={m.id} className="hover:bg-white/5 transition-colors">
                  <td className="py-2.5 px-3 font-bold text-foreground">{m.email}</td>
                  <td className="py-2.5 px-3 text-muted-foreground">
                    {m.first_name} {m.last_name}
                  </td>
                  <td className="py-2.5 px-3">
                    <Badge
                      className={
                        m.role === "Owner"
                          ? "bg-brand-purple/20 text-brand-purple border-brand-purple/30"
                          : m.role === "Admin"
                          ? "bg-emerald-950/60 text-emerald-400 border-emerald-500/40"
                          : "bg-blue-950/60 text-blue-400 border-blue-500/40"
                      }
                    >
                      {m.role}
                    </Badge>
                  </td>
                  <td className="py-2.5 px-3 text-muted-foreground">
                    {new Date(m.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Permission Matrix */}
      <PermissionMatrix matrix={permMatrix} />

      {/* Teams & Workspace Projects */}
      <TeamManagementCard
        teams={teams}
        projects={projects}
        onCreateTeam={(name, desc) => createTeamMutation.mutate({ name, desc })}
        onCreateProject={(name, provider, env) => createProjMutation.mutate({ name, provider, env })}
      />

      {/* Audit Log Timeline */}
      <AuditLogTimeline logs={auditLogs} />

      {/* Invite Member Modal */}
      <InviteMemberModal
        isOpen={isInviteModalOpen}
        onClose={() => setIsInviteModalOpen(false)}
        onInvite={(email, role) => inviteMutation.mutate({ email, role })}
        isInviting={inviteMutation.isPending}
      />
    </div>
  );
}
