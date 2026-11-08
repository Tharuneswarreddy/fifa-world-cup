import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { confederationName } from "@/lib/format";
import { useDebounce } from "@/lib/useDebounce";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/primitives";
import { CardGridSkeleton, EmptyState, ErrorState } from "@/components/ui/states";
import { Flag } from "@/components/ui/TeamBadge";
import { Pagination, SearchInput } from "@/components/ui/misc";

const CONFEDS = ["UEFA", "CONMEBOL", "CONCACAF", "CAF", "AFC", "OFC"];

export default function Teams() {
  const [search, setSearch] = useState("");
  const [confed, setConfed] = useState("");
  const [page, setPage] = useState(1);
  const debounced = useDebounce(search, 300);

  const q = useQuery({
    queryKey: ["teams", debounced, confed, page],
    queryFn: () => api.teams({ search: debounced, confederation: confed, page, page_size: 24 }),
    placeholderData: keepPreviousData,
  });

  return (
    <div>
      <PageHeader
        title="Teams"
        subtitle="National teams that have appeared at the World Cup finals."
      />
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center">
        <SearchInput
          value={search}
          onChange={(v) => {
            setSearch(v);
            setPage(1);
          }}
          placeholder="Search teams…"
          className="sm:max-w-xs"
        />
        <div className="flex flex-wrap gap-1.5">
          <FilterChip active={confed === ""} onClick={() => { setConfed(""); setPage(1); }}>
            All
          </FilterChip>
          {CONFEDS.map((c) => (
            <FilterChip key={c} active={confed === c} onClick={() => { setConfed(c); setPage(1); }}>
              {c}
            </FilterChip>
          ))}
        </div>
      </div>

      {q.isLoading ? (
        <CardGridSkeleton count={12} height="h-20" />
      ) : q.isError ? (
        <ErrorState onRetry={() => q.refetch()} />
      ) : q.data!.items.length === 0 ? (
        <EmptyState title="No teams found" message="Try a different search or confederation filter." />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {q.data!.items.map((t) => (
              <Card key={t.id} as={Link} to={`/teams/${t.id}`} interactive className="flex items-center gap-3 p-4">
                <Flag team={t} size={32} />
                <div className="min-w-0 flex-1">
                  <div className="truncate font-semibold text-fg">{t.name}</div>
                  <div className="text-xs text-muted">
                    {confederationName(t.confederation)}
                    {t.is_defunct && " · historical"}
                  </div>
                </div>
                {t.fifa_code && <span className="font-mono text-xs text-muted">{t.fifa_code}</span>}
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

function FilterChip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={
        "rounded-lg border px-2.5 py-1.5 text-xs font-medium transition " +
        (active ? "border-accent bg-accent/15 text-accent" : "border-border bg-surface text-muted hover:text-fg")
      }
    >
      {children}
    </button>
  );
}
