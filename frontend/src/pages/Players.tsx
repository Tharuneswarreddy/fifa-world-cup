import { useState } from "react";
import { Link } from "react-router-dom";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useDebounce } from "@/lib/useDebounce";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/primitives";
import { EmptyState, ErrorState, RowsSkeleton } from "@/components/ui/states";
import { Flag } from "@/components/ui/TeamBadge";
import { Pagination, SearchInput, Tabs } from "@/components/ui/misc";

export default function Players() {
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("goals");
  const [page, setPage] = useState(1);
  const debounced = useDebounce(search, 300);

  const q = useQuery({
    queryKey: ["players", debounced, sort, page],
    queryFn: () => api.players({ search: debounced, sort, page, page_size: 24 }),
    placeholderData: keepPreviousData,
  });

  return (
    <div>
      <PageHeader
        title="Players"
        subtitle="World Cup goalscorers. The open dataset records goals (not appearances), so rankings are by goals scored."
      />
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <SearchInput
          value={search}
          onChange={(v) => {
            setSearch(v);
            setPage(1);
          }}
          placeholder="Search players…"
          className="sm:max-w-xs"
        />
        <Tabs
          tabs={[
            { key: "goals", label: "By goals" },
            { key: "name", label: "A–Z" },
          ]}
          active={sort}
          onChange={(k) => {
            setSort(k);
            setPage(1);
          }}
        />
      </div>

      {q.isLoading ? (
        <RowsSkeleton rows={12} />
      ) : q.isError ? (
        <ErrorState onRetry={() => q.refetch()} />
      ) : q.data!.items.length === 0 ? (
        <EmptyState title="No players found" message="Try a different search." />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {q.data!.items.map((p, i) => (
              <Card key={p.id} as={Link} to={`/players/${p.id}`} interactive className="flex items-center gap-3 p-3">
                {sort === "goals" && (
                  <span className="w-6 text-center text-sm font-bold text-muted">
                    {(q.data!.page - 1) * q.data!.page_size + i + 1}
                  </span>
                )}
                <Flag team={p.primary_team ?? undefined} size={22} />
                <div className="min-w-0 flex-1">
                  <div className="truncate font-medium text-fg">{p.name}</div>
                  <div className="truncate text-xs text-muted">{p.primary_team?.name ?? "—"}</div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold tabular-nums text-accent">{p.goals ?? 0}</div>
                  <div className="text-[10px] uppercase text-muted">goals</div>
                </div>
              </Card>
            ))}
          </div>
          <div className="mt-5">
            <Pagination page={q.data!.page} pages={q.data!.pages} total={q.data!.total} onPage={setPage} />
          </div>
        </>
      )}
    </div>
  );
}
