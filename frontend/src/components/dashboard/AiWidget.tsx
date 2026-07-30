import { Sparkles, DollarSign, Zap, Shield, Activity, ChevronRight } from "lucide-react";
import { NavLink } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { aiInsights } from "@/lib/mockData";
import { cn } from "@/lib/utils";
import type { AiInsight } from "@/types/dashboard";

const categoryConfig: Record<AiInsight["category"], {
  icon: React.ElementType;
  badge: "warning" | "info" | "danger" | "purple";
  accent: string;
}> = {
  Cost:        { icon: DollarSign, badge: "warning", accent: "border-l-warning"      },
  Performance: { icon: Zap,        badge: "info",    accent: "border-l-brand-blue"   },
  Security:    { icon: Shield,     badge: "danger",  accent: "border-l-danger"       },
  Reliability: { icon: Activity,   badge: "purple",  accent: "border-l-brand-purple" },
};

function InsightItem({ insight }: { insight: AiInsight }) {
  const cfg = categoryConfig[insight.category];
  const Icon = cfg.icon;

  return (
    <div className={cn("rounded-lg border-l-2 bg-bg-elevated/40 px-3 py-2.5 space-y-2", cfg.accent)}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <Icon className="h-3 w-3 text-muted-foreground" />
          <Badge variant={cfg.badge} className="text-[10px]">{insight.category}</Badge>
        </div>
        <span className="text-[10px] text-muted-foreground shrink-0">{insight.confidence}% conf.</span>
      </div>
      <p className="text-xs text-foreground/90 leading-relaxed line-clamp-2">{insight.text}</p>
      <div className="flex items-center gap-2">
        <Button size="sm" className="h-6 px-2.5 text-[11px]">{insight.action}</Button>
        <Button size="sm" variant="ghost" className="h-6 px-2.5 text-[11px] text-muted-foreground">Dismiss</Button>
      </div>
    </div>
  );
}

export default function AiWidget() {
  return (
    <Card className="flex flex-col">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-brand-gradient">
              <Sparkles className="h-3.5 w-3.5 text-white" />
            </div>
            <CardTitle className="text-foreground text-sm font-semibold">AI Recommendations</CardTitle>
          </div>
          <NavLink to="/ai" className="flex items-center gap-1 text-xs text-brand-blue hover:underline">
            Open AI <ChevronRight className="h-3 w-3" />
          </NavLink>
        </div>
        <div className="flex items-center gap-2 mt-1">
          <Badge variant="purple">{aiInsights.length} new</Badge>
          <span className="text-[11px] text-muted-foreground">Updated 5 min ago</span>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto px-4 pb-4">
        <div className="space-y-2.5">
          {aiInsights.map((insight) => (
            <InsightItem key={insight.id} insight={insight} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
