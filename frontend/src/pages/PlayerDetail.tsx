import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, StatCard } from "@/components/ui/primitives";
import { ErrorState, Skeleton } from "@/components/ui/states";
import { Flag } from "@/components/ui/TeamBadge";
import { AXIS_COLOR, CHART_COLORS, ChartContainer, ChartTooltip, GRID_COLOR } from "@/components/charts/ChartContainer";

export default function PlayerDetail() {
  const { id } = useParams();
  const q = useQuery({ queryKey: ["player", Number(id)], queryFn: () => api.player(Number(id)) });

  if (q.isLoading) return <Skeleton className="h-64 w-full rounded-2xl" />;
  if (q.isError || !q.data) return <ErrorState onRetry={() => q.refetch()} />;
  const p = q.data;
  const chartData = p.goals_by_edition.map((g) => ({ year: g.year, goals: g.goals }));

  return (
    <div className="space-y-6">
      <PageHeader title={p.name} subtitle={p.primary_team ? `Goals for ${p.primary_team.name}` : undefined} />

      <Card className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center">
        <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-elevated text-2xl font-black text-muted">
          {p.name.split(/\s+/).map((w) => w[0]).slice(0, 2).join("").toUpperCase()}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            {p.primary_team && (
              <Link to={`/teams/${p.primary_team.id}`} className="flex items-center gap-2 hover:text-accent">
                <Flag team={p.primary_team} size={22} />
                <span className="text-sm font-medium text-fg">{p.primary_team.name}</span>
              </Link>
            )}
          </div>
          <p className="mt-1 text-xs text-muted">
            World Cup span: {p.first_year ?? "—"}{p.last_year && p.last_year !== p.first_year ? `–${p.last_year}` : ""}
          </p>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        <StatCard label="Goals" value={p.total_goals} accent />
        <StatCard label="Tournaments" value={p.tournaments ?? 0} />
        <StatCard label="Penalties" value={p.penalties} />
        <StatCard label="Own goals" value={p.own_goals} />
        <StatCard label="Appearances" value="Not recorded" hint="not in open source" />
      </div>

      {chartData.length > 0 && (
        <ChartContainer
          title="Goals by tournament"
          subtitle="World Cup finals goals per edition"
          provenance={p.provenance}
          height={260}
        >
          <ResponsiveContainer>
            <BarChart data={chartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
              <CartesianGrid stroke={GRID_COLOR} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="year" stroke={AXIS_COLOR} tick={{ fontSize: 11 }} />
              <YAxis stroke={AXIS_COLOR} tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: "hsl(var(--elevated))" }} />
              <Bar dataKey="goals" fill={CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      )}

      <Card className="p-4">
        <p className="text-xs text-muted">
          Player profiles (date of birth, position, club history, appearances) are not available from the
          open martj42 dataset. Only verified goal events are shown. Fields without data are labelled
          “Not recorded” rather than estimated.
        </p>
      </Card>
    </div>
  );
}
