import { useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ArrowRight, Goal, Medal, Trophy, Users } from "lucide-react";
import { api } from "@/lib/api";
import { formatDate, num } from "@/lib/format";
import { Badge, Card, StatCard, buttonClass } from "@/components/ui/primitives";
import { CardGridSkeleton, ErrorState, RowsSkeleton } from "@/components/ui/states";
import { TeamBadge } from "@/components/ui/TeamBadge";
import { MatchRow } from "@/components/matches/MatchRow";
import { AXIS_COLOR, CHART_COLORS, ChartContainer, ChartTooltip, GRID_COLOR } from "@/components/charts/ChartContainer";

export default function Home() {
  const navigate = useNavigate();
  const editionsQ = useQuery({ queryKey: ["tournaments", "all"], queryFn: () => api.tournaments({ page_size: 40 }) });
  const editions = editionsQ.data?.items ?? [];
  const featured = editions.find((e) => e.status !== "upcoming") ?? editions[0];

  const overviewQ = useQuery({
    queryKey: ["tournament", featured?.id],
    queryFn: () => api.tournament(featured!.id),
    enabled: !!featured,
  });
  const recentQ = useQuery({
    queryKey: ["matches", "featured", featured?.id],
    queryFn: () => api.matches({ edition: featured!.id, page_size: 6 }),
    enabled: !!featured,
  });

  const goalsByYear = useMemo(
    () =>
      [...editions]
        .filter((e) => (e.num_matches ?? 0) > 0)
        .sort((a, b) => a.year - b.year)
        .map((e) => ({ year: e.year, goals: e.total_goals ?? 0 })),
    [editions],
  );

  if (editionsQ.isError) return <ErrorState onRetry={() => editionsQ.refetch()} />;

  const ov = overviewQ.data;

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="hero-gradient relative overflow-hidden rounded-2xl border border-border p-6 sm:p-8">
        {editionsQ.isLoading || !featured ? (
          <div className="space-y-3">
            <div className="skeleton h-6 w-40 rounded" />
            <div className="skeleton h-10 w-72 rounded" />
          </div>
        ) : (
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-xl">
              <div className="mb-2 flex items-center gap-2">
                <Badge tone="accent">FIFA World Cup</Badge>
                <Badge tone={featured.status === "completed" ? "muted" : "success"}>{featured.status}</Badge>
              </div>
              <h1 className="text-3xl font-black tracking-tight text-fg sm:text-4xl">{featured.name}</h1>
              <p className="mt-2 text-sm text-muted">
                Hosted by {featured.host_name ?? "—"} · {num(featured.num_teams)} teams ·{" "}
                {num(featured.num_matches)} matches · {num(featured.total_goals)} goals
              </p>
              {featured.champion && (
                <div className="mt-4 flex items-center gap-3 rounded-xl border border-border bg-surface/70 p-3">
                  <Trophy className="h-6 w-6 text-accent" />
                  <div>
                    <div className="text-xs uppercase tracking-wide text-muted">Champions</div>
                    <TeamBadge team={featured.champion} size={22} className="text-base" />
                  </div>
                </div>
              )}
              <div className="mt-5 flex flex-wrap gap-2">
                <Link to={`/tournaments/${featured.id}`} className={buttonClass("primary")}>
                  Explore tournament <ArrowRight className="h-4 w-4" />
                </Link>
                <Link to="/records" className={buttonClass("outline")}>
                  All-time records
                </Link>
              </div>
            </div>

            {/* Year selector */}
            <Card className="w-full max-w-xs p-4">
              <label className="text-xs font-medium uppercase tracking-wide text-muted">Jump to a World Cup</label>
              <select
                className="mt-2 w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-fg focus:border-accent"
                defaultValue={featured.id}
                onChange={(e) => navigate(`/tournaments/${e.target.value}`)}
              >
                {editions.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.year} — {e.host_name}
                  </option>
                ))}
              </select>
              <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                <div>
                  <div className="text-lg font-bold text-fg">{editions.length}</div>
                  <div className="text-[10px] uppercase text-muted">Editions</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-fg">{ov?.teams.length ?? "—"}</div>
                  <div className="text-[10px] uppercase text-muted">Teams</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-fg">{num(featured.total_goals)}</div>
                  <div className="text-[10px] uppercase text-muted">Goals</div>
                </div>
              </div>
            </Card>
          </div>
        )}
      </section>

      {/* Stat cards */}
      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Teams" value={featured ? num(featured.num_teams) : "—"} hint={<span className="inline-flex items-center gap-1"><Users className="h-3 w-3" />this edition</span>} />
        <StatCard label="Matches" value={featured ? num(featured.num_matches) : "—"} />
        <StatCard label="Goals" value={featured ? num(featured.total_goals) : "—"} accent hint={<span className="inline-flex items-center gap-1"><Goal className="h-3 w-3" />scored</span>} />
        <StatCard label="Top scorer" value={ov?.top_scorers[0]?.goals ?? "—"} hint={ov?.top_scorers[0]?.name} />
      </section>

      {/* Chart + top scorers */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ChartContainer
            title="Goals per tournament"
            subtitle="Total goals scored at each World Cup finals"
            provenance={{ source: "martj42", license: "CC0" }}
          >
            <ResponsiveContainer>
              <BarChart data={goalsByYear} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                <CartesianGrid stroke={GRID_COLOR} strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="year" stroke={AXIS_COLOR} tick={{ fontSize: 11 }} interval="preserveStartEnd" />
                <YAxis stroke={AXIS_COLOR} tick={{ fontSize: 11 }} />
                <Tooltip content={<ChartTooltip />} cursor={{ fill: "hsl(var(--elevated))" }} />
                <Bar dataKey="goals" radius={[4, 4, 0, 0]}>
                  {goalsByYear.map((d, i) => (
                    <Cell key={i} fill={CHART_COLORS[0]} opacity={featured && d.year === featured.year ? 1 : 0.55} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </div>

        <Card className="p-4">
          <div className="mb-3 flex items-center gap-2">
            <Medal className="h-4 w-4 text-accent" />
            <h3 className="font-semibold text-fg">Top scorers — {featured?.year}</h3>
          </div>
          {overviewQ.isLoading ? (
            <RowsSkeleton rows={6} />
          ) : (
            <ol className="space-y-1.5">
              {(ov?.top_scorers ?? []).slice(0, 8).map((s, i) => (
                <li key={s.player_id}>
                  <Link
                    to={`/players/${s.player_id}`}
                    className="flex items-center gap-3 rounded-lg px-2 py-1.5 hover:bg-elevated"
                  >
                    <span className="w-5 text-center text-xs font-bold text-muted">{i + 1}</span>
                    <span className="flex-1 truncate text-sm text-fg">{s.name}</span>
                    <span className="text-sm font-bold tabular-nums text-accent">{s.goals}</span>
                  </Link>
                </li>
              ))}
            </ol>
          )}
        </Card>
      </section>

      {/* Recent results + podium */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="font-semibold text-fg">Latest results — {featured?.year}</h3>
            <Link to={`/matches?edition=${featured?.id}`} className="text-sm text-accent hover:underline">
              All matches
            </Link>
          </div>
          {recentQ.isLoading ? (
            <RowsSkeleton rows={5} />
          ) : (
            <div className="space-y-2">
              {(recentQ.data?.items ?? []).map((m) => (
                <MatchRow key={m.id} match={m} showYear={false} />
              ))}
            </div>
          )}
        </div>

        <Card className="p-4">
          <h3 className="mb-3 font-semibold text-fg">Final standings — {featured?.year}</h3>
          <div className="space-y-2">
            {[
              { label: "Champions", team: featured?.champion, tone: "text-accent" },
              { label: "Runners-up", team: featured?.runner_up, tone: "text-fg" },
              { label: "Third place", team: featured?.third_place, tone: "text-muted" },
            ].map((row) => (
              <div key={row.label} className="flex items-center justify-between rounded-xl border border-border bg-surface px-3 py-2.5">
                <span className="text-xs uppercase tracking-wide text-muted">{row.label}</span>
                {row.team ? <TeamBadge team={row.team} size={22} /> : <span className="text-muted">—</span>}
              </div>
            ))}
          </div>
          {featured?.end_date && (
            <p className="mt-3 text-xs text-muted">Final played {formatDate(featured.end_date)}.</p>
          )}
        </Card>
      </section>

      {editionsQ.isLoading && <CardGridSkeleton />}
    </div>
  );
}
