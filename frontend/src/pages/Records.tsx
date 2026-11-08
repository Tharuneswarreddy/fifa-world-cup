import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge, Card } from "@/components/ui/primitives";
import { ErrorState, RowsSkeleton } from "@/components/ui/states";
import { Flag } from "@/components/ui/TeamBadge";
import type { Leaderboard, RecordRow } from "@/types/api";

export default function Records() {
  const q = useQuery({ queryKey: ["records", 15], queryFn: () => api.records(15) });

  return (
    <div>
      <PageHeader
        title="Records & Leaderboards"
        subtitle="All-time World Cup finals records. Qualifiers and friendlies are excluded; shootouts count as draws (FIFA convention)."
        actions={<Badge tone="muted">Scope: Men’s World Cup finals</Badge>}
      />
      {q.isLoading ? (
        <RowsSkeleton rows={10} />
      ) : q.isError ? (
        <ErrorState onRetry={() => q.refetch()} />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {q.data!.map((board) => (
            <BoardCard key={board.key} board={board} />
          ))}
        </div>
      )}
    </div>
  );
}

function BoardCard({ board }: { board: Leaderboard }) {
  const max = board.rows[0]?.value || 1;
  return (
    <Card className="p-5">
      <h3 className="mb-3 font-semibold text-fg">{board.title}</h3>
      <div className="space-y-1.5">
        {board.rows.map((r) => (
          <RowItem key={`${r.rank}-${r.label}`} row={r} max={max} unit={board.unit} />
        ))}
      </div>
    </Card>
  );
}

function RowItem({ row, max, unit }: { row: RecordRow; max: number; unit: string }) {
  const label =
    row.player_id ? (
      <Link to={`/players/${row.player_id}`} className="truncate text-fg hover:text-accent">
        {row.label}
      </Link>
    ) : row.team ? (
      <Link to={`/teams/${row.team.id}`} className="flex items-center gap-2 truncate text-fg hover:text-accent">
        <Flag team={row.team} size={18} /> {row.label}
      </Link>
    ) : (
      <span className="truncate text-fg">{row.label}</span>
    );
  return (
    <div className="flex items-center gap-3">
      <span className="w-5 shrink-0 text-center text-xs font-bold text-muted">{row.rank}</span>
      <div className="min-w-0 flex-1">{label}</div>
      <div className="hidden h-2 w-28 overflow-hidden rounded-full bg-elevated sm:block">
        <div className="h-full rounded-full bg-accent" style={{ width: `${(row.value / max) * 100}%` }} />
      </div>
      <span className="w-14 shrink-0 text-right text-sm font-bold tabular-nums text-accent">
        {row.value.toLocaleString()}
        <span className="ml-1 text-[10px] font-normal text-muted">{unit === "goals" ? "" : ""}</span>
      </span>
    </div>
  );
}
