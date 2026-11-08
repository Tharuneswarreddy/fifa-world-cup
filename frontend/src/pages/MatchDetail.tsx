import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Goal, MapPin } from "lucide-react";
import { api } from "@/lib/api";
import { decidedByLabel, formatDate } from "@/lib/format";
import { Badge, Card } from "@/components/ui/primitives";
import { ErrorState, Skeleton } from "@/components/ui/states";
import { DataSourceLabel } from "@/components/ui/misc";
import { Flag } from "@/components/ui/TeamBadge";

export default function MatchDetail() {
  const { id } = useParams();
  const q = useQuery({ queryKey: ["match", Number(id)], queryFn: () => api.match(Number(id)) });

  if (q.isLoading) return <Skeleton className="h-64 w-full rounded-2xl" />;
  if (q.isError || !q.data) return <ErrorState onRetry={() => q.refetch()} />;
  const m = q.data;
  const extra = decidedByLabel(m.decided_by);

  const homeGoals = m.goals.filter((g) => g.team_id === m.home.id);
  const awayGoals = m.goals.filter((g) => g.team_id === m.away.id);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between text-sm text-muted">
        <span>
          {m.edition ? (
            <Link to={`/tournaments/${m.edition.id}`} className="hover:text-accent">
              {m.edition.name}
            </Link>
          ) : (
            m.tournament_label
          )}
        </span>
        <span>{formatDate(m.match_date, { weekday: "short", year: "numeric", month: "short", day: "numeric" })}</span>
      </div>

      <Card className="hero-gradient p-6">
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4">
          <div className="flex flex-col items-center gap-2 text-center">
            <Flag team={m.home} size={48} />
            <Link to={`/teams/${m.home.id}`} className="font-semibold text-fg hover:text-accent">
              {m.home.name}
            </Link>
          </div>
          <div className="text-center">
            <div className="text-4xl font-black tabular-nums text-fg">
              {m.home_score ?? "–"} <span className="text-muted">:</span> {m.away_score ?? "–"}
            </div>
            {extra && <div className="mt-1 text-xs text-muted">{extra}</div>}
            {m.shootout && (
              <div className="mt-1 text-xs text-accent">Shootout won by {m.shootout.winner_team_id === m.home.id ? m.home.name : m.away.name}</div>
            )}
          </div>
          <div className="flex flex-col items-center gap-2 text-center">
            <Flag team={m.away} size={48} />
            <Link to={`/teams/${m.away.id}`} className="font-semibold text-fg hover:text-accent">
              {m.away.name}
            </Link>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap items-center justify-center gap-3 text-xs text-muted">
          {(m.city || m.country_name) && (
            <span className="inline-flex items-center gap-1">
              <MapPin className="h-3 w-3" /> {[m.city, m.country_name].filter(Boolean).join(", ")}
            </span>
          )}
          {m.neutral && <Badge tone="muted">Neutral venue</Badge>}
        </div>
      </Card>

      <Card className="p-5">
        <div className="mb-3 flex items-center gap-2">
          <Goal className="h-4 w-4 text-accent" />
          <h3 className="font-semibold text-fg">Goals</h3>
        </div>
        {m.goals.length === 0 ? (
          <p className="text-sm text-muted">No goalscorer data recorded for this match.</p>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            <GoalList goals={homeGoals} align="left" />
            <GoalList goals={awayGoals} align="right" />
          </div>
        )}
      </Card>

      <DataSourceLabel provenance={m.provenance} />
    </div>
  );
}

function GoalList({ goals, align }: { goals: { minute?: number | null; player_name?: string | null; player_id?: number | null; own_goal: boolean; penalty: boolean }[]; align: "left" | "right" }) {
  return (
    <ul className={align === "right" ? "space-y-1.5 text-right" : "space-y-1.5"}>
      {goals.map((g, i) => (
        <li key={i} className="text-sm">
          <span className="font-mono text-xs text-muted">{g.minute != null ? `${g.minute}'` : ""}</span>{" "}
          {g.player_id ? (
            <Link to={`/players/${g.player_id}`} className="text-fg hover:text-accent">
              {g.player_name}
            </Link>
          ) : (
            <span className="text-fg">{g.player_name}</span>
          )}
          {g.penalty && <span className="text-muted"> (pen)</span>}
          {g.own_goal && <span className="text-muted"> (o.g.)</span>}
        </li>
      ))}
    </ul>
  );
}
