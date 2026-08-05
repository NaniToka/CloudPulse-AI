/**
 * OrganizationSwitcher Component — Navbar dropdown selector for Organization & Workspace Project.
 */

import React, { useState } from "react";
import { Building2, ChevronDown, Check, FolderKanban, Plus } from "lucide-react";
import type { Organization, Project } from "@/types/tenant";

interface OrganizationSwitcherProps {
  organizations: Organization[];
  selectedOrg: Organization | null;
  onSelectOrg: (org: Organization) => void;
  projects?: Project[];
  selectedProject?: Project | null;
  onSelectProject?: (proj: Project) => void;
}

export const OrganizationSwitcher: React.FC<OrganizationSwitcherProps> = ({
  organizations,
  selectedOrg,
  onSelectOrg,
  projects = [],
  selectedProject,
  onSelectProject,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative font-sans text-xs">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-bg-surface/90 border border-white/10 hover:border-brand-purple/50 transition-all text-foreground shadow-sm"
      >
        <div className="h-6 w-6 rounded-lg bg-brand-purple/20 border border-brand-purple/30 text-brand-purple flex items-center justify-center font-bold font-mono">
          {selectedOrg?.name?.charAt(0) || "C"}
        </div>
        <div className="flex flex-col items-start text-left">
          <span className="font-bold text-xs leading-none truncate max-w-[130px]">
            {selectedOrg?.name || "Global Organization"}
          </span>
          <span className="text-[10px] text-muted-foreground font-mono mt-0.5 leading-none">
            {selectedProject ? selectedProject.name : "All Projects"}
          </span>
        </div>
        <ChevronDown className="h-3.5 w-3.5 text-muted-foreground ml-1" />
      </button>

      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          className="fixed inset-0 z-40"
        />
      )}

      {isOpen && (
        <div className="absolute left-0 mt-2 w-64 rounded-xl bg-bg-surface border border-white/10 shadow-2xl z-50 p-2 space-y-2">
          {/* Organizations Header */}
          <div className="px-2 py-1 text-[10px] font-mono text-muted-foreground uppercase tracking-wider">
            Organizations
          </div>
          <div className="space-y-1">
            {organizations.map((org) => {
              const isSelected = selectedOrg?.id === org.id;
              return (
                <button
                  key={org.id}
                  onClick={() => {
                    onSelectOrg(org);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg transition-colors text-left ${
                    isSelected ? "bg-brand-purple/20 text-brand-purple font-bold" : "hover:bg-white/5 text-muted-foreground"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Building2 className="h-3.5 w-3.5" />
                    <span className="truncate">{org.name}</span>
                  </div>
                  {isSelected && <Check className="h-3.5 w-3.5 text-brand-purple" />}
                </button>
              );
            })}
          </div>

          {/* Workspace Projects Header */}
          {projects.length > 0 && (
            <>
              <div className="border-t border-white/10 my-1" />
              <div className="px-2 py-1 text-[10px] font-mono text-muted-foreground uppercase tracking-wider">
                Workspace Projects
              </div>
              <div className="space-y-1">
                {projects.map((proj) => {
                  const isSelected = selectedProject?.id === proj.id;
                  return (
                    <button
                      key={proj.id}
                      onClick={() => {
                        onSelectProject?.(proj);
                        setIsOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg transition-colors text-left ${
                        isSelected ? "bg-emerald-950/40 text-emerald-400 font-bold" : "hover:bg-white/5 text-muted-foreground"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <FolderKanban className="h-3.5 w-3.5" />
                        <span className="truncate">{proj.name}</span>
                      </div>
                      {isSelected && <Check className="h-3.5 w-3.5 text-emerald-400" />}
                    </button>
                  );
                })}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};
