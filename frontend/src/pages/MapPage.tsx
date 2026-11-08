import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Download, Info } from "lucide-react";
import { api } from "@/lib/api";
import { downloadCsv } from "@/lib/exportCsv";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, buttonClass } from "@/components/ui/primitives";
import { ErrorState, RowsSkeleton } from "@/components/ui/states";
import { Tabs } from "@/components/ui/misc";
import { Flag } from "@/components/ui/TeamBadge";

export default function MapPage() {
  const [sort, setSort] = useState<"appearances" | "titles">("appearances");
  const q = useQuery({ queryKey: ["map"], queryFn: () => api.mapParticipation() });

  const rows = useMemo(() => {
    const data = [...(q.data ?? [])];
    data.sort((a, b) => (sort === "titles" ? b.titles - a.titles || b.appearances - a.appearances : b.appearances - a.appearances));
    return data;
  }, [q.data, sort]);

  const maxApp = rows[0]?.appearances ?? 1;

  return (
    <div>
      <PageHeader
        title="World Participation Map"
        subtitle="World Cup participation and success by nation."
        actions={
          <button
            className={buttonClass("outline")}
            onClick={() =>
              downloadCsv(
                "wc_participation.csv",
                rows.map((r) => ({ team: r.name, appearances: r.appearances, titles: r.titles, best_finish: r.best_finish })),
              )
            }
          >
            <Download className="h-4 w-4" /> Export CSV
          </button>
        }
      />

      <Card className="mb-5 flex items-start gap-2 p-3 text-xs text-muted">
        <Info className="mt-0.5 h-4 w-4 shrink-0" />
        <span>
          This is the accessible participation view (tiles scaled by number of appearances). A geographic
          choropleth using open map geometry is a planned enhancement; the data below is the same either way.
        </span>
      </Card>

      <div className="mb-4">
        <Tabs
          tabs={[
            { key: "appearances", label: "By appearances" },
            { key: "titles", label: "By titles" },
          ]}
          active={sort}
          onChange={(k) => setSort(k as "appearances" | "titles")}
        />
      </div>

      {q.isLoading ? (
        <RowsSkeleton rows={10} />
      ) : q.isError ? (
        <ErrorState onRetry={() => q.refetch()} />
      ) : (
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
          {rows.map((r) => {
            const intensity = 0.12 + 0.6 * (r.appearances / maxApp);
            return (
              <Link
                key={r.team_id}
                to={`/teams/${r.team_id}`}
                className="group relative overflow-hidden rounded-xl border border-border p-3 transition hover:border-accent/50"
                style={{ background: `hsl(var(--accent) / ${intensity})` }}
              >
                <div className="flex items-center gap-2">
                  <Flag team={{ id: r.team_id, name: r.name, slug: "", iso2: r.iso2, flag_url: r.flag_url, is_defunct: false }} size={22} />
                  <span className="truncate text-sm font-semibold text-fg">{r.name}</span>
                </div>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className="text-fg/80">{r.appearances} apps</span>
                  {r.titles > 0 && <span className="font-bold text-fg">★ {r.titles}</span>}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
