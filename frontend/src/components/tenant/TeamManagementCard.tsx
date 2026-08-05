/**
 * TeamManagementCard Component — Manages teams & projects within an Organization.
 */

import React, { useState } from "react";
import { Users, FolderKanban, Plus, Layers } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Team, Project } from "@/types/tenant";

interface TeamManagementCardProps {
  teams: Team[];
  projects: Project[];
  onCreateTeam: (name: string, description?: string) => void;
  onCreateProject: (name: string, provider: string, env: string) => void;
}

export const TeamManagementCard: React.FC<TeamManagementCardProps> = ({
  teams,
  projects,
  onCreateTeam,
  onCreateProject,
}) => {
  const [teamName, setTeamName] = useState("");
  const [teamDesc, setTeamDesc] = useState("");
  const [showTeamInput, setShowTeamInput] = useState(false);

  const [projName, setProjName] = useState("");
  const [projProvider, setProjProvider] = useState("AWS");
  const [projEnv, setProjEnv] = useState("Production");
  const [showProjInput, setShowProjInput] = useState(false);

  const handleCreateTeamSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!teamName) return;
    onCreateTeam(teamName, teamDesc);
    setTeamName("");
    setTeamDesc("");
    setShowTeamInput(false);
  };

  const handleCreateProjSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!projName) return;
    onCreateProject(projName, projProvider, projEnv);
    setProjName("");
    setShowProjInput(false);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 font-sans text-xs">
      {/* Teams Card */}
      <div className="p-5 rounded-2xl bg-bg-surface/90 border border-white/10 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-brand-purple" />
            <h3 className="text-sm font-bold text-foreground">Organization Teams</h3>
          </div>
          <Button
            size="sm"
            onClick={() => setShowTeamInput(!showTeamInput)}
            className="bg-white/10 hover:bg-white/20 text-foreground text-xs gap-1"
          >
            <Plus className="h-3.5 w-3.5" /> Add Team
          </Button>
        </div>

        {showTeamInput && (
          <form onSubmit={handleCreateTeamSubmit} className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
            <Input
              placeholder="Team Name (e.g. Platform SRE)"
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              className="bg-bg-elevated text-xs border-white/10"
            />
            <Input
              placeholder="Description (optional)"
              value={teamDesc}
              onChange={(e) => setTeamDesc(e.target.value)}
              className="bg-bg-elevated text-xs border-white/10"
            />
            <Button type="submit" className="w-full bg-brand-purple text-xs font-bold">
              Create Team
            </Button>
          </form>
        )}

        <div className="space-y-2">
          {teams.map((t) => (
            <div key={t.id} className="p-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between">
              <div>
                <p className="font-bold text-foreground font-mono">{t.name}</p>
                {t.description && <p className="text-[11px] text-muted-foreground">{t.description}</p>}
              </div>
              <Badge variant="outline" className="font-mono text-[10px]">
                Active Team
              </Badge>
            </div>
          ))}
        </div>
      </div>

      {/* Projects Card */}
      <div className="p-5 rounded-2xl bg-bg-surface/90 border border-white/10 shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2">
            <FolderKanban className="h-4 w-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-foreground">Workspace Projects</h3>
          </div>
          <Button
            size="sm"
            onClick={() => setShowProjInput(!showProjInput)}
            className="bg-white/10 hover:bg-white/20 text-foreground text-xs gap-1"
          >
            <Plus className="h-3.5 w-3.5" /> Add Project
          </Button>
        </div>

        {showProjInput && (
          <form onSubmit={handleCreateProjSubmit} className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
            <Input
              placeholder="Project Name (e.g. Microservices Gateway)"
              value={projName}
              onChange={(e) => setProjName(e.target.value)}
              className="bg-bg-elevated text-xs border-white/10"
            />
            <div className="flex gap-2">
              <select
                value={projProvider}
                onChange={(e) => setProjProvider(e.target.value)}
                className="bg-bg-elevated border border-white/10 rounded-lg p-2 text-xs text-foreground flex-1"
              >
                <option value="AWS">AWS</option>
                <option value="GCP">GCP</option>
                <option value="Azure">Azure</option>
              </select>

              <select
                value={projEnv}
                onChange={(e) => setProjEnv(e.target.value)}
                className="bg-bg-elevated border border-white/10 rounded-lg p-2 text-xs text-foreground flex-1"
              >
                <option value="Production">Production</option>
                <option value="Staging">Staging</option>
                <option value="Development">Development</option>
              </select>
            </div>
            <Button type="submit" className="w-full bg-emerald-600 hover:bg-emerald-500 text-xs font-bold text-white">
              Create Workspace Project
            </Button>
          </form>
        )}

        <div className="space-y-2">
          {projects.map((p) => (
            <div key={p.id} className="p-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between font-mono">
              <div>
                <p className="font-bold text-foreground">{p.name}</p>
                <p className="text-[10px] text-muted-foreground">Region: {p.region}</p>
              </div>
              <div className="flex items-center gap-1.5">
                <Badge className="bg-blue-950/60 text-blue-400 border-blue-500/40 text-[10px]">
                  {p.cloud_provider}
                </Badge>
                <Badge className="bg-emerald-950/60 text-emerald-400 border-emerald-500/40 text-[10px]">
                  {p.environment}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
