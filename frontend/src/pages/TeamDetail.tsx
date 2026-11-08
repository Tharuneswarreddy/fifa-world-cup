import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { GitCompareArrows, Trophy } from "lucide-react";
import { api } from "@/lib/api";
import { confederationName } from "@/lib/format";
import { Badge, Card, StatCard, buttonClass } from "@/components/ui/primitives";
import { ErrorState, RowsSkeleton, Skeleton } from "@/components/ui/states";
import { DataSourceLabel } from "@/components/ui/misc";
import { Flag } from "@/components/ui/TeamBadge";
import { MatchRow } from "@/components/matches/MatchRow";

export default function TeamDetail() {
  const { id } = useParams();
  const teamId = Number(id);
  const q = useQuery({ queryKey: ["team", teamId], queryFn: () => api.team(teamId) });
  const matchesQ = useQuery({ queryKey: ["team", teamId, "matches"], queryFn: () => api.teamMatches(teamId, 1) });

  if (q.isLoading) return <Skeleton className="h-64 w-full rounded-2xl" />;
  if (q.isError || !q.data) return <ErrorState onRetry={() => q.refetch()} />;
  const t = q.data;
  const s = t.stats;

  return (
    <div className="space-y-6">
      <Card className="hero-gradient p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <Flag team={t} size={56} />
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-black text-fg sm:text-3xl">{t.name}</h1>
                {t.is_defunct && <Badge tone="muted">Historical</Badge>}
              </div>
              <p className="text-sm text-muted">
                {confederationName(t.confederation)}
                {t.fifa_code ? ` · ${t.fifa_code}` : ""}
              </p>
              {s.best_finish && (
                <div className="mt-2">
                  <Badge tone="accent">
                    <Trophy className="h-3 w-3" /> {s.best_finish}
                  </Badge>
                </div>
              )}
            </div>
          </div>
          <Link to={`/compare?a=${t.id}`} className={buttonClass("outline")}>
            <GitCompareArrows className="h-4 w-4" /> Compare
          </Link>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <StatCard label="Titles" value={s.titles} accent />
        <StatCard label="Tournaments" value={s.tournaments} />
        <StatCard label="Played" value={s.matches_played} />
        <StatCard label="W / D / L" value={`${s.wins}/${s.draws}/${s.losses}`} />
        <StatCard label="Goals ±" value={`${s.goals_for}:${s.goals_against}`} hint={`GD ${s.goal_difference >= 0 ? "+" : ""}${s.goal_difference}`} />
        <StatCard label="Win %" value={`${s.win_pct}%`} />
      </div>

      {t.titles_years.length > 0 && (
        <Card className="p-4">
          <h3 className="mb-2 text-sm font-semibold text-fg">World Cup titles</h3>
          <div className="flex flex-wrap gap-2">
            {t.titles_years.map((y) => (
              <Badge key={y} tone="accent">
                <Trophy className="h-3 w-3" /> {y}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="p-4">
          <h3 className="mb-3 font-semibold text-fg">Tournament-by-tournament</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase text-muted">
                  <th className="py-2 pr-2">Year</th>
                  <th className="pr-2">Finish</th>
                  <th className="px-1 text-center">P</th>
                  <th className="px-1 text-center">W</th>
                  <th className="px-1 text-center">D</th>
                  <th className="px-1 text-center">L</th>
                  <th className="px-1 text-center">GF</th>
                  <th className="px-1 text-center">GA</th>
                </tr>
              </thead>
              <tbody>
                {t.participations.map((p) => (
                  <tr key={p.edition_id} className="border-b border-border/50">
                    <td className="py-1.5 pr-2">
                      <Link to={`/tournaments/${p.edition_id}`} className="font-medium text-fg hover:text-accent">
                        {p.year}
                      </Link>
                    </td>
                    <td className="pr-2 text-muted">{p.finish ?? "—"}</td>
                    <td className="px-1 text-center tabular-nums">{p.matches}</td>
                    <td className="px-1 text-center tabular-nums">{p.wins}</td>
                    <td className="px-1 text-center tabular-nums">{p.draws}</td>
                    <td className="px-1 text-center tabular-nums">{p.losses}</td>
                    <td className="px-1 text-center tabular-nums">{p.goals_for}</td>
                    <td className="px-1 text-center tabular-nums">{p.goals_against}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <DataSourceLabel provenance={t.provenance} className="mt-3" />
        </Card>

        <div>
          <h3 className="mb-3 font-semibold text-fg">Recent World Cup matches</h3>
          {matchesQ.isLoading ? (
            <RowsSkeleton rows={6} />
          ) : (
            <div className="space-y-2">
              {(matchesQ.data?.items ?? []).slice(0, 8).map((m) => (
                <MatchRow key={m.id} match={m} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
