import { useSearchParams } from "react-router-dom";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState, ErrorState, RowsSkeleton } from "@/components/ui/states";
import { Pagination } from "@/components/ui/misc";
import { MatchRow } from "@/components/matches/MatchRow";

export default function Matches() {
  const [params, setParams] = useSearchParams();
  const edition = params.get("edition") ? Number(params.get("edition")) : undefined;
  const page = params.get("page") ? Number(params.get("page")) : 1;

  const editionsQ = useQuery({ queryKey: ["tournaments", "all"], queryFn: () => api.tournaments({ page_size: 40 }) });
  const q = useQuery({
    queryKey: ["matches", edition, page],
    queryFn: () => api.matches({ edition, page, page_size: 30 }),
    placeholderData: keepPreviousData,
  });

  function update(next: Record<string, string | undefined>) {
    const p = new URLSearchParams(params);
    for (const [k, v] of Object.entries(next)) {
      if (v === undefined || v === "") p.delete(k);
      else p.set(k, v);
    }
    setParams(p);
  }

  return (
    <div>
      <PageHeader title="Fixtures & Results" subtitle="Every World Cup finals match, with scores, extra time and shootouts." />

      <div className="mb-5">
        <select
          value={edition ?? ""}
          onChange={(e) => update({ edition: e.target.value || undefined, page: "1" })}
          className="rounded-xl border border-border bg-surface px-3 py-2 text-sm text-fg focus:border-accent"
        >
          <option value="">All tournaments</option>
          {(editionsQ.data?.items ?? []).map((e) => (
            <option key={e.id} value={e.id}>
              {e.year} — {e.host_name}
            </option>
          ))}
        </select>
      </div>

      {q.isLoading ? (
        <RowsSkeleton rows={12} />
      ) : q.isError ? (
        <ErrorState onRetry={() => q.refetch()} />
      ) : q.data!.items.length === 0 ? (
        <EmptyState title="No matches" />
      ) : (
        <>
          <div className="space-y-2">
            {q.data!.items.map((m) => (
              <MatchRow key={m.id} match={m} />
            ))}
          </div>
          <div className="mt-5">
            <Pagination
              page={q.data!.page}
              pages={q.data!.pages}
              total={q.data!.total}
              onPage={(p) => update({ page: String(p) })}
            />
          </div>
        </>
      )}
    </div>
  );
}
