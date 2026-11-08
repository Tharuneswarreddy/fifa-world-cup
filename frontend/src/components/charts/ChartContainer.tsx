import type { ReactNode } from "react";
import { Card } from "@/components/ui/primitives";
import { DataSourceLabel } from "@/components/ui/misc";
import type { Provenance } from "@/types/api";

export const CHART_COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
  "hsl(var(--chart-6))",
];

export const AXIS_COLOR = "hsl(var(--muted))";
export const GRID_COLOR = "hsl(var(--border))";

export function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-elevated px-3 py-2 text-xs shadow-pop">
      {label !== undefined && <div className="mb-1 font-semibold text-fg">{label}</div>}
      {payload.map((p: any, i: number) => (
        <div key={i} className="flex items-center gap-2 text-muted">
          <span className="h-2 w-2 rounded-full" style={{ background: p.color }} />
          <span>{p.name}:</span>
          <span className="font-medium text-fg tabular-nums">{p.value}</span>
        </div>
      ))}
    </div>
  );
}

export function ChartContainer({
  title,
  subtitle,
  children,
  provenance,
  height = 280,
  actions,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  provenance?: Provenance | null;
  height?: number;
  actions?: ReactNode;
}) {
  return (
    <Card className="p-4">
      <div className="mb-3 flex items-start justify-between gap-2">
        <div>
          <h3 className="font-semibold text-fg">{title}</h3>
          {subtitle && <p className="text-xs text-muted">{subtitle}</p>}
        </div>
        {actions}
      </div>
      <div style={{ width: "100%", height }}>{children}</div>
      {provenance && <DataSourceLabel provenance={provenance} className="mt-3" />}
    </Card>
  );
}
