import { Link } from "react-router-dom";
import type { MatchSummary } from "@/types/api";
import { Flag } from "@/components/ui/TeamBadge";
import { classNames, decidedByLabel, formatDate } from "@/lib/format";

export function MatchRow({ match, showYear = true }: { match: MatchSummary; showYear?: boolean }) {
  const homeWin = match.winner_team_id === match.home.id;
  const awayWin = match.winner_team_id === match.away.id;
  const extra = decidedByLabel(match.decided_by);
  return (
    <Link
      to={`/matches/${match.id}`}
      className="group grid grid-cols-[1fr_auto_1fr] items-center gap-2 rounded-xl border border-border bg-surface px-3 py-2.5 transition hover:border-accent/50 hover:bg-elevated sm:gap-4"
    >
      <div className="flex min-w-0 items-center justify-end gap-2 text-right">
        <span className={classNames("truncate text-sm", homeWin ? "font-semibold text-fg" : "text-muted")}>
          {match.home.name}
        </span>
        <Flag team={match.home} size={20} />
      </div>
      <div className="flex flex-col items-center">
        <span className="rounded-lg bg-elevated px-2.5 py-1 text-sm font-bold tabular-nums text-fg">
          {match.home_score ?? "–"} <span className="text-muted">:</span> {match.away_score ?? "–"}
        </span>
        {extra && <span className="mt-0.5 text-[10px] text-muted">{extra}</span>}
      </div>
      <div className="flex min-w-0 items-center gap-2">
        <Flag team={match.away} size={20} />
        <span className={classNames("truncate text-sm", awayWin ? "font-semibold text-fg" : "text-muted")}>
          {match.away.name}
        </span>
      </div>
      <div className="col-span-3 flex items-center justify-center gap-2 text-[11px] text-muted">
        <span>{formatDate(match.match_date)}</span>
        {showYear && match.edition && (
          <>
            <span aria-hidden>·</span>
            <span>{match.edition.year} World Cup</span>
          </>
        )}
      </div>
    </Link>
  );
}
