/** Shared glassmorphic tooltip used by all Recharts charts. */

interface ChartTooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; color: string; unit?: string }>;
  label?: string;
  unit?: string;
  formatter?: (value: number) => string;
}

export default function ChartTooltip({ active, payload, label, unit = "", formatter }: ChartTooltipProps) {
  if (!active || !payload?.length) return null;
  const fmt = formatter ?? ((v: number) => `${v}${unit}`);

  return (
    <div className="glass rounded-lg border border-white/10 p-3 text-xs shadow-lg min-w-[140px]">
      {label && <p className="font-semibold text-foreground mb-2">{label}</p>}
      {payload.map((p) => (
        <div key={p.name} className="flex items-center justify-between gap-4 py-0.5">
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <span className="h-1.5 w-1.5 rounded-full shrink-0" style={{ background: p.color }} />
            {p.name}
          </div>
          <span className="font-semibold text-foreground tabular-nums">{fmt(p.value)}</span>
        </div>
      ))}
    </div>
  );
}
