import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { CalendarDays, LayoutGrid, ListTree, Medal, ShieldHalf, Trophy } from "lucide-react";
import { api } from "@/lib/api";
import { formatDate, num } from "@/lib/format";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge, Card, StatCard } from "@/components/ui/primitives";
import { EmptyState, ErrorState, RowsSkeleton, Skeleton } from "@/components/ui/states";
import { DataSourceLabel, Tabs } from "@/components/ui/misc";
import { TeamBadge } from "@/components/ui/TeamBadge";
import { MatchRow } from "@/components/matches/MatchRow";

const TABS = [
  { key: "overview", label: "Overview", icon: <Trophy className="h-4 w-4" /> },
  { key: "teams", label: "Teams", icon: <ShieldHalf className="h-4 w-4" /> },
  { key: "groups", label: "Groups", icon: <LayoutGrid className="h-4 w-4" /> },
  { key: "fixtures", label: "Fixtures", icon: <CalendarDays className="h-4 w-4" /> },
  { key: "bracket", label: "Bracket", icon: <ListTree className="h-4 w-4" /> },
  { key: "records", label: "Records", icon: <Medal className="h-4 w-4" /> },
];

export default function TournamentDetail() {
  const { id } = useParams();
  const editionId = Number(id);
  const [tab, setTab] = useState("overview");

  const ovQ = useQuery({ queryKey: ["tournament", editionId], queryFn: () => api.tournament(editionId) });
  const fixturesQ = useQuery({
    queryKey: ["tournament", editionId, "fixtures"],
    queryFn: () => api.tournamentFixtures(editionId),
    enabled: tab === "fixtures",
  });
  const bracketQ = useQuery({
    queryKey: ["tournament", editionId, "bracket"],
    queryFn: () => api.tournamentBracket(editionId),
    enabled: tab === "bracket",
  });

  if (ovQ.isLoading) return <Skeleton className="h-64 w-full rounded-2xl" />;
  if (ovQ.isError || !ovQ.data) return <ErrorState onRetry={() => ovQ.refetch()} />;
  const ov = ovQ.data;

  return (
    <div className="space-y-6">
      <PageHeader
        title={ov.name}
        subtitle={`Hosted by ${ov.host_name ?? "—"}${ov.format ? ` · ${ov.format}` : ""}`}
        actions={<Badge tone="accent">{ov.status}</Badge>}
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Teams" value={num(ov.num_teams)} />
        <StatCard label="Matches" value={num(ov.num_matches)} />
        <StatCard label="Goals" value={num(ov.total_goals)} accent />
        <StatCard
          label="Goals / match"
          value={ov.num_matches ? ((ov.total_goals ?? 0) / ov.num_matches).toFixed(2) : "—"}
        />
      </div>

      <Tabs tabs={TABS} active={tab} onChange={setTab} />

      {tab === "overview" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <Card className="p-5 lg:col-span-1">
            <h3 className="mb-3 font-semibold text-fg">Final standings</h3>
            <div className="space-y-2">
              {[
                ["Champions", ov.champion, "accent"],
                ["Runners-up", ov.runner_up, "muted"],
                ["Third place", ov.third_place, "muted"],
              ].map(([label, team]) => (
                <div key={label as string} className="flex items-center justify-between rounded-xl border border-border bg-surface px-3 py-2.5">
                  <span className="text-xs uppercase tracking-wide text-muted">{label as string}</span>
                  {team ? <TeamBadge team={team as never} size={22} /> : <span className="text-muted">—</span>}
                </div>
              ))}
            </div>
            <div className="mt-4 space-y-1 text-sm text-muted">
              {ov.start_date && <div>Dates: {formatDate(ov.start_date)} – {formatDate(ov.end_date)}</div>}
            </div>
            <DataSourceLabel provenance={ov.provenance} className="mt-4" />
          </Card>

          <Card className="p-5 lg:col-span-2">
            <h3 className="mb-3 font-semibold text-fg">Top scorers</h3>
            {ov.top_scorers.length === 0 ? (
              <EmptyState title="No goal data" message="Goalscorer data is not available for this edition." />
            ) : (
              <ol className="grid grid-cols-1 gap-1.5 sm:grid-cols-2">
                {ov.top_scorers.map((s, i) => (
                  <li key={s.player_id}>
                    <Link to={`/players/${s.player_id}`} className="flex items-center gap-3 rounded-lg px-2 py-1.5 hover:bg-elevated">
                      <span className="w-5 text-center text-xs font-bold text-muted">{i + 1}</span>
                      <TeamBadge team={s.team ?? undefined} link={false} size={16} className="hidden sm:flex" />
                      <span className="flex-1 truncate text-sm text-fg">{s.name}</span>
                      <span className="text-sm font-bold tabular-nums text-accent">{s.goals}</span>
                    </Link>
                  </li>
                ))}
              </ol>
            )}
          </Card>
        </div>
      )}

      {tab === "teams" && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {ov.teams.map((t) => (
            <Card key={t.id} as={Link} to={`/teams/${t.id}`} interactive className="flex items-center gap-2 p-3">
              <TeamBadge team={t} link={false} size={24} />
            </Card>
          ))}
        </div>
      )}

      {tab === "groups" && (
        <EmptyState
          title="Group tables not available"
          message="The open martj42 dataset records match results but not the group-stage composition, so per-group standings cannot be shown without fabricating data. Match-by-match results are available under Fixtures."
          icon={<LayoutGrid className="h-8 w-8" />}
        />
      )}

      {tab === "fixtures" && (
        <div>
          {fixturesQ.isLoading ? (
            <RowsSkeleton rows={10} />
          ) : (
            <div className="space-y-2">
              {(fixturesQ.data ?? []).map((m) => (
                <MatchRow key={m.id} match={m} showYear={false} />
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "bracket" && (
        <div>
          {bracketQ.isLoading ? (
            <RowsSkeleton rows={3} />
          ) : bracketQ.data?.available ? (
            <div className="space-y-4">
              <Card className="p-5">
                <div className="mb-3 flex items-center gap-2">
                  <Trophy className="h-5 w-5 text-accent" />
                  <h3 className="font-semibold text-fg">Final</h3>
                </div>
                <MatchRow match={bracketQ.data.final} showYear={false} />
                {bracketQ.data.third_place_match && (
                  <>
                    <div className="mb-2 mt-5 flex items-center gap-2">
                      <Medal className="h-4 w-4 text-muted" />
                      <h3 className="font-semibold text-fg">Third-place play-off</h3>
                    </div>
                    <MatchRow match={bracketQ.data.third_place_match} showYear={false} />
                  </>
                )}
                <p className="mt-4 text-xs text-muted">{bracketQ.data.note}</p>
              </Card>
            </div>
          ) : (
            <EmptyState title="Bracket not available" message={bracketQ.data?.reason} />
          )}
        </div>
      )}

      {tab === "records" && <TournamentRecords editionId={editionId} />}
    </div>
  );
}

function TournamentRecords({ editionId }: { editionId: number }) {
  const q = useQuery({
    queryKey: ["tournament", editionId, "records"],
    queryFn: () => api.tournament(editionId),
  });
  if (q.isLoading) return <RowsSkeleton rows={6} />;
  const scorers = q.data?.top_scorers ?? [];
  return (
    <Card className="p-5">
      <h3 className="mb-3 font-semibold text-fg">Golden Boot race</h3>
      <div className="space-y-1.5">
        {scorers.map((s, i) => (
          <div key={s.player_id} className="flex items-center gap-3">
            <span className="w-5 text-center text-xs font-bold text-muted">{i + 1}</span>
            <Link to={`/players/${s.player_id}`} className="flex-1 truncate text-sm text-fg hover:text-accent">
              {s.name}
            </Link>
            <div className="h-2 w-40 overflow-hidden rounded-full bg-elevated">
              <div
                className="h-full rounded-full bg-accent"
                style={{ width: `${(s.goals / (scorers[0]?.goals || 1)) * 100}%` }}
              />
            </div>
            <span className="w-6 text-right text-sm font-bold tabular-nums text-accent">{s.goals}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
