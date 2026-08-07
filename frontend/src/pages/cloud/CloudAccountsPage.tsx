import { useState } from "react";
import { Plus, Cloud, CheckCircle2, AlertTriangle, ShieldCheck, Key, Loader2, X } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useCloudAccounts } from "@/hooks/useCloudObservability";
import { cn } from "@/lib/utils";

export default function CloudAccountsPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [provider, setProvider] = useState<"AWS" | "GCP" | "Azure">("AWS");
  const [name, setName] = useState("");
  const [accountId, setAccountId] = useState("");
  const [metaKey, setMetaKey] = useState("");

  const { data: accounts = [], isLoading, connectAccount, isConnecting } = useCloudAccounts();

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !accountId) return;
    try {
      await connectAccount({
        name,
        provider,
        account_id: accountId,
        credentials_type: provider === "AWS" ? "role_arn" : provider === "GCP" ? "service_account_key" : "service_principal",
        credentials_meta: { key: metaKey },
        default_region: provider === "AWS" ? "us-east-1" : provider === "GCP" ? "us-central1" : "eastus",
        environment: "production",
      });
      setModalOpen(false);
      setName("");
      setAccountId("");
      setMetaKey("");
    } catch (e) {
      alert("Failed to connect cloud account");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Cloud Accounts & Onboarding"
        subtitle="Manage connected AWS IAM Roles, Azure Subscriptions & GCP Projects"
        actions={
          <Button size="sm" onClick={() => setModalOpen(true)} className="gap-2 bg-brand-blue hover:bg-brand-blue/90 text-white">
            <Plus className="h-3.5 w-3.5" /> Connect Cloud Account
          </Button>
        }
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <StatCard label="Connected Accounts" value={accounts.length} icon={<Cloud className="h-4 w-4" />} />
        <StatCard
          label="Active Sync Status"
          value="Healthy"
          icon={<CheckCircle2 className="h-4 w-4 text-emerald-400" />}
          trend={{ value: "All synced", direction: "up", positive: true }}
        />
        <StatCard label="Role Security Level" value="IAM Enforced" icon={<ShieldCheck className="h-4 w-4 text-purple-400" />} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-semibold text-foreground">Cloud Account Registry</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex h-36 items-center justify-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading cloud accounts...
            </div>
          ) : accounts.length === 0 ? (
            <div className="p-8 text-center text-xs text-muted-foreground">
              No cloud accounts connected. Click "Connect Cloud Account" to launch the wizard.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[0.06] text-xs text-muted-foreground">
                    {["Account Name", "Provider", "Account / Project ID", "Region", "Environment", "Status", "Last Synced"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left font-medium">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {accounts.map((acc) => (
                    <tr key={acc.id} className="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-3 font-semibold text-xs text-foreground">{acc.name}</td>
                      <td className="px-4 py-3 text-xs font-mono font-bold text-amber-400">{acc.provider}</td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{acc.account_id}</td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{acc.default_region}</td>
                      <td className="px-4 py-3 text-xs text-muted-foreground capitalize">{acc.environment}</td>
                      <td className="px-4 py-3">
                        <Badge variant="success" className="text-[10px]">
                          {acc.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">
                        {acc.last_synced_at ? new Date(acc.last_synced_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "Just now"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Cloud Onboarding Wizard Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-xl border border-white/10 bg-slate-950 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                <Key className="h-4 w-4 text-brand-blue" /> Cloud Onboarding Wizard
              </h3>
              <button onClick={() => setModalOpen(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleConnect} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="text-muted-foreground">Select Cloud Provider</label>
                <div className="grid grid-cols-3 gap-2">
                  {(["AWS", "GCP", "Azure"] as const).map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setProvider(p)}
                      className={cn(
                        "py-2 rounded-md border text-xs font-bold font-mono transition-colors",
                        provider === p ? "border-brand-blue bg-brand-blue/10 text-brand-blue" : "border-white/10 bg-background text-muted-foreground"
                      )}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-muted-foreground">Account Name</label>
                <Input
                  placeholder="e.g. AWS Production Workloads"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="h-8 text-xs"
                />
              </div>

              <div className="space-y-1">
                <label className="text-muted-foreground">
                  {provider === "AWS" ? "AWS Account ID" : provider === "GCP" ? "GCP Project ID" : "Azure Subscription ID"}
                </label>
                <Input
                  placeholder={provider === "AWS" ? "1234-5678-9012" : provider === "GCP" ? "my-gcp-project-123" : "0a9f87c1-..."}
                  value={accountId}
                  onChange={(e) => setAccountId(e.target.value)}
                  className="h-8 text-xs font-mono"
                />
              </div>

              <div className="space-y-1">
                <label className="text-muted-foreground">
                  {provider === "AWS" ? "Cross-Account IAM Role ARN" : provider === "GCP" ? "Service Account Email / Key" : "Tenant ID & Client Secret"}
                </label>
                <Input
                  placeholder={provider === "AWS" ? "arn:aws:iam::123456789012:role/CloudPulseRole" : "sa@project.iam.gserviceaccount.com"}
                  value={metaKey}
                  onChange={(e) => setMetaKey(e.target.value)}
                  className="h-8 text-xs font-mono"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/10">
                <Button type="button" variant="outline" size="sm" onClick={() => setModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" size="sm" disabled={isConnecting} className="bg-brand-blue hover:bg-brand-blue/90 text-white">
                  {isConnecting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Verify & Connect"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
