import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Trophy } from "lucide-react";
import { api } from "@/lib/api";
import { num, statusLabel } from "@/lib/format";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge, Card } from "@/components/ui/primitives";
import { CardGridSkeleton, ErrorState } from "@/components/ui/states";
import { TeamBadge } from "@/components/ui/TeamBadge";

export default function Tournaments() {
  const q = useQuery({ queryKey: ["tournaments", "all"], queryFn: () => api.tournaments({ page_size: 40 }) });

  return (
    <div>
      <PageHeader
        title="Tournament Explorer"
        subtitle="Every edition of the FIFA World Cup — hosts, champions and tournament scale."
      />
      {q.isLoading ? (
        <CardGridSkeleton count={9} height="h-40" />
      ) : q.isError ? (
        <ErrorState onRetry={() => q.refetch()} />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {q.data!.items.map((e) => {
            const status = statusLabel(e.status);
            return (
              <Card key={e.id} as={Link} to={`/tournaments/${e.id}`} interactive className="block p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-2xl font-black text-fg">{e.year}</div>
                    <div className="text-sm text-muted">{e.host_name}</div>
                  </div>
                  <Badge tone={status.tone}>{status.label}</Badge>
                </div>
                <div className="mt-4 flex items-center gap-2 rounded-xl border border-border bg-elevated/60 px-3 py-2">
                  <Trophy className="h-4 w-4 text-accent" />
                  {e.champion ? (
                    <TeamBadge team={e.champion} size={20} link={false} />
                  ) : (
                    <span className="text-sm text-muted">To be decided</span>
                  )}
                </div>
                <div className="mt-4 grid grid-cols-3 gap-2 text-center text-sm">
                  <div>
                    <div className="font-bold text-fg">{num(e.num_teams)}</div>
                    <div className="text-[10px] uppercase text-muted">Teams</div>
                  </div>
                  <div>
                    <div className="font-bold text-fg">{num(e.num_matches)}</div>
                    <div className="text-[10px] uppercase text-muted">Matches</div>
                  </div>
                  <div>
                    <div className="font-bold text-fg">{num(e.total_goals)}</div>
                    <div className="text-[10px] uppercase text-muted">Goals</div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
