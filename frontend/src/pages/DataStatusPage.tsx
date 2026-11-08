import { useQuery } from "@tanstack/react-query";
import { ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import { formatDate, num } from "@/lib/format";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, StatCard } from "@/components/ui/primitives";
import { ErrorState, Skeleton } from "@/components/ui/states";

export default function DataStatusPage() {
  const q = useQuery({ queryKey: ["data-status"], queryFn: () => api.dataStatus() });

  if (q.isLoading) return <Skeleton className="h-64 w-full rounded-2xl" />;
  if (q.isError || !q.data) return <ErrorState onRetry={() => q.refetch()} />;
  const d = q.data;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Status"
        subtitle="Provenance, coverage and freshness of the data powering this platform."
      />

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {Object.entries(d.totals).map(([k, v]) => (
          <StatCard key={k} label={k} value={num(v)} />
        ))}
      </div>

      <Card className="p-5">
        <h3 className="mb-3 font-semibold text-fg">Data sources</h3>
        <div className="space-y-3">
          {d.sources.map((s) => (
            <div key={s.key} className="rounded-xl border border-border bg-surface p-3">
              <div className="flex items-center justify-between">
                <div className="font-medium text-fg">{s.name}</div>
                {s.url && (
                  <a href={s.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-xs text-accent hover:underline">
                    source <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
              <div className="mt-1 text-xs text-muted">
                License: {s.license ?? "—"}
                {s.last_synced_at && ` · last synced ${formatDate(s.last_synced_at)}`}
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-5">
        <h3 className="mb-3 font-semibold text-fg">Competition coverage</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs uppercase text-muted">
              <th className="py-2">Competition</th>
              <th className="text-right">Editions loaded</th>
            </tr>
          </thead>
          <tbody>
            {d.competition_coverage.map((c) => (
              <tr key={c.competition} className="border-b border-border/50">
                <td className="py-2 text-fg">{c.name}</td>
                <td className="text-right tabular-nums">
                  {c.editions > 0 ? c.editions : <span className="text-muted">not yet loaded</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-3 text-xs text-muted">
          API-Football quota is checked on demand via the ingestion CLI (free plan: 100 requests/day) and is
          not called on every page load.
        </p>
      </Card>
    </div>
  );
}
