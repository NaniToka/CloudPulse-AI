/**
 * PermissionMatrix Component — Renders granular RBAC Role vs Permission capability matrix.
 */

import React from "react";
import { Check, X, Shield, Lock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { PermissionMatrix as PermMatrixType } from "@/types/tenant";

interface PermissionMatrixProps {
  matrix: PermMatrixType | undefined;
}

const allPermissions = [
  "Dashboard.Read",
  "Dashboard.Write",
  "Incidents.Manage",
  "Logs.Read",
  "Tracing.Read",
  "Security.Manage",
  "AI.Use",
  "Billing.Manage",
  "Settings.Manage",
];

const roles = ["Owner", "Admin", "Manager", "Engineer", "Viewer"];

export const PermissionMatrix: React.FC<PermissionMatrixProps> = ({ matrix }) => {
  return (
    <div className="p-5 rounded-2xl bg-bg-surface/90 border border-white/10 shadow-2xl space-y-4 font-sans text-xs">
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-brand-purple/20 border border-brand-purple/30 text-brand-purple flex items-center justify-center font-bold">
            <Shield className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground">Granular Role & Permission Matrix</h3>
            <p className="text-[11px] text-muted-foreground font-mono">Fine-grained API authorization matrix</p>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse font-mono text-xs">
          <thead>
            <tr className="border-b border-white/10 text-muted-foreground text-left">
              <th className="py-2.5 px-3">Permission Key</th>
              {roles.map((r) => (
                <th key={r} className="py-2.5 px-3 text-center">
                  <Badge variant="outline" className="text-[10px] border-white/10">
                    {r}
                  </Badge>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {allPermissions.map((perm) => (
              <tr key={perm} className="hover:bg-white/5 transition-colors">
                <td className="py-2.5 px-3 font-bold text-foreground">{perm}</td>
                {roles.map((r) => {
                  const allowed = matrix?.[r]?.includes(perm);
                  return (
                    <td key={r} className="py-2.5 px-3 text-center">
                      {allowed ? (
                        <div className="inline-flex h-5 w-5 rounded-md bg-emerald-950/60 border border-emerald-500/40 text-emerald-400 items-center justify-center">
                          <Check className="h-3.5 w-3.5" />
                        </div>
                      ) : (
                        <div className="inline-flex h-5 w-5 rounded-md bg-white/5 border border-white/10 text-muted-foreground items-center justify-center opacity-40">
                          <X className="h-3.5 w-3.5" />
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
