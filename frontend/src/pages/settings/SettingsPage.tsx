import { User, Bell, Shield, Palette, Globe } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/store/authStore";

const sections = [
  { icon: User,    label: "Profile"       },
  { icon: Bell,    label: "Notifications" },
  { icon: Shield,  label: "Security"      },
  { icon: Globe,   label: "Integrations"  },
  { icon: Palette, label: "Appearance"    },
];

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="space-y-6">
      <PageHeader title="Settings" subtitle="Manage your account and workspace preferences" />

      <div className="flex gap-6">
        {/* Sidebar nav */}
        <nav className="hidden sm:flex flex-col gap-1 w-44 shrink-0">
          {sections.map((s, i) => (
            <button
              key={s.label}
              className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors ${i === 0 ? "bg-brand-gradient text-white" : "text-muted-foreground hover:bg-bg-overlay hover:text-foreground"}`}
            >
              <s.icon className="h-4 w-4" />
              {s.label}
            </button>
          ))}
        </nav>

        {/* Profile form */}
        <div className="flex-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-foreground text-sm font-semibold">Profile Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">First Name</label>
                  <Input defaultValue={user?.first_name ?? ""} />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Last Name</label>
                  <Input defaultValue={user?.last_name ?? ""} />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Email Address</label>
                <Input defaultValue={user?.email ?? ""} type="email" disabled />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Role</label>
                <Input defaultValue={user?.role ?? "member"} disabled />
              </div>
              <Separator />
              <div className="flex justify-end">
                <Button size="sm">Save Changes</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
