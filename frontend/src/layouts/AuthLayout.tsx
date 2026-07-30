import { Outlet } from "react-router-dom";
import { Zap } from "lucide-react";

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-bg-void flex">
      {/* Aurora background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full bg-brand-blue/8 blur-[120px] animate-aurora" />
        <div className="absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full bg-brand-violet/8 blur-[100px] animate-aurora [animation-delay:4s]" />
      </div>

      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 relative flex-col p-12 justify-between">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-gradient shadow-glow-blue">
            <Zap className="h-4 w-4 text-white" />
          </div>
          <span className="font-bold text-lg gradient-text">CloudPulse AI</span>
        </div>

        <div className="space-y-6">
          <blockquote className="text-2xl font-light text-muted-foreground italic leading-relaxed max-w-md">
            "The single pane of glass for modern infrastructure."
          </blockquote>
          <div className="flex gap-6 text-xs text-muted-foreground">
            {["SOC 2 Type II", "GDPR", "ISO 27001"].map((badge) => (
              <div key={badge} className="flex items-center gap-1.5">
                <div className="h-1.5 w-1.5 rounded-full bg-success" />
                {badge}
              </div>
            ))}
          </div>
        </div>

        <p className="text-xs text-muted-foreground">
          © {new Date().getFullYear()} CloudPulse AI. All rights reserved.
        </p>
      </div>

      {/* Right panel — form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 relative">
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
