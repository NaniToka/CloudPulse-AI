import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-bg-elevated text-foreground border border-white/10",
        success: "bg-success/15 text-success border border-success/20",
        warning: "bg-warning/15 text-warning border border-warning/20",
        danger: "bg-danger/15 text-danger border border-danger/20",
        critical: "bg-critical/15 text-critical border border-critical/20",
        info: "bg-brand-blue/15 text-brand-blue border border-brand-blue/20",
        purple: "bg-brand-purple/15 text-brand-purple border border-brand-purple/20",
        muted: "bg-bg-surface text-muted-foreground border border-white/6",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
