import { Sparkles, DollarSign, Zap, Shield, Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { aiInsights } from "@/lib/mockData";
import { cn } from "@/lib/utils";
import type { AiInsight } from "@/types/dashboard";

const categoryConfig: Record<AiInsight["category"], {
  icon: React.ElementType;
  badge: "warning" | "info" | "danger" | "purple";
  color: string;
}> = {
  Cost: { icon: DollarSign, badge: "warning", color: "border-l-warning" },
  Performance: { icon: Zap, badge: "info", color: "border-l-brand-blue" },
  Security: { icon: Shield, badge: "danger", color: "border-l-danger" },
  Reliability: { icon: Activity, badge: "purple", color: "border-l-brand-purple" },
};

function InsightItem({ insight }: { insight: AiInsight }) {
  const cfg = categoryConfig[insight.category];
  const Icon = cfg.icon;

  return (
    <div className={cn("rounded-lg border-l-2 bg-bg-elevated/50 px-3 py-3 space-y-2.5", cfg.color)}>
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Icon className="h-3.5 w-3.5 text-muted-foreground" />
          <Badge variant={cfg.badge}>{insight.category}</Badge>
        </div>
        <span className="text-[10px] text-muted-foreground shrink-0">
          {insight.confidence}% confidence
        </span>
      </div>
      <p className="text-xs text-foreground/90 leading-relaxed">{insight.text}</p>
      <div className="flex items-center gap-2">
        <Button size="sm" className="h-7 px-3 text-xs">
          {insight.action}
        </Button>
        <Button size="sm" variant="ghost" className="h-7 px-3 text-xs">
          Dismiss
        </Button>
      </div>
    </div>
  );
}

export default function AiInsightsPanel() {
  return (
    <Card className="flex flex-col h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-brand-gradient">
              <Sparkles className="h-3.5 w-3.5 text-white" />
            </div>
            <CardTitle className="text-foreground text-sm font-semibold">AI Recommendations</CardTitle>
          </div>
          <Badge variant="purple">{aiInsights.length} new</Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto px-4 pb-4">
        <div className="space-y-3">
          {aiInsights.map((insight) => (
            <InsightItem key={insight.id} insight={insight} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
