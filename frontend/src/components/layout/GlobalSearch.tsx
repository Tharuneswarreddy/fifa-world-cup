import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { api } from "@/lib/api";
import { useDebounce } from "@/lib/useDebounce";
import type { SearchHit } from "@/types/api";
import { Flag } from "@/components/ui/TeamBadge";

export function GlobalSearch() {
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const debounced = useDebounce(q, 250);
  const navigate = useNavigate();
  const boxRef = useRef<HTMLDivElement>(null);

  const { data } = useQuery({
    queryKey: ["search", debounced],
    queryFn: () => api.search(debounced),
    enabled: debounced.trim().length >= 2,
  });

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  function go(path: string) {
    setOpen(false);
    setQ("");
    navigate(path);
  }

  const groups: { label: string; hits: SearchHit[]; to: (h: SearchHit) => string }[] = [
    { label: "Teams", hits: data?.teams ?? [], to: (h) => `/teams/${h.id}` },
    { label: "Players", hits: data?.players ?? [], to: (h) => `/players/${h.id}` },
    { label: "Tournaments", hits: data?.editions ?? [], to: (h) => `/tournaments/${h.id}` },
  ];
  const hasResults = groups.some((g) => g.hits.length > 0);

  return (
    <div ref={boxRef} className="relative w-full max-w-md">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
      <input
        value={q}
        onChange={(e) => {
          setQ(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder="Search teams, players, tournaments…"
        className="w-full rounded-xl border border-border bg-surface py-2 pl-9 pr-3 text-sm text-fg placeholder:text-muted focus:border-accent"
        aria-label="Global search"
      />
      {open && debounced.trim().length >= 2 && (
        <div className="absolute z-50 mt-2 max-h-[60vh] w-full overflow-auto rounded-xl border border-border bg-elevated shadow-pop">
          {!hasResults && <div className="px-4 py-3 text-sm text-muted">No matches for “{debounced}”.</div>}
          {groups.map(
            (g) =>
              g.hits.length > 0 && (
                <div key={g.label} className="py-1">
                  <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-muted">
                    {g.label}
                  </div>
                  {g.hits.map((h) => (
                    <button
                      key={`${h.type}-${h.id}`}
                      onClick={() => go(g.to(h))}
                      className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-surface"
                    >
                      {h.type === "team" && (
                        <Flag team={{ id: h.id, name: h.title, slug: h.slug ?? "", is_defunct: false }} size={18} />
                      )}
                      <span className="flex-1 truncate text-fg">{h.title}</span>
                      {h.subtitle && <span className="text-xs text-muted">{h.subtitle}</span>}
                    </button>
                  ))}
                </div>
              ),
          )}
        </div>
      )}
    </div>
  );
}
