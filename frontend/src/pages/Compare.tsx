import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "@/lib/api";
import { useDebounce } from "@/lib/useDebounce";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/primitives";
import { ErrorState, Skeleton } from "@/components/ui/states";
import { SearchInput } from "@/components/ui/misc";
import { Flag } from "@/components/ui/TeamBadge";
import { AXIS_COLOR, CHART_COLORS, ChartTooltip, GRID_COLOR } from "@/components/charts/ChartContainer";
import type { TeamDetail, TeamSummary } from "@/types/api";

function TeamPicker({ label, value, onPick }: { label: string; value?: number; onPick: (id: number) => void }) {
  const [search, setSearch] = useState("");
  const debounced = useDebounce(search, 250);
  const q = useQuery({
    queryKey: ["teams", "pick", debounced],
    queryFn: () => api.teams({ search: debounced, page_size: 8 }),
    enabled: debounced.length >= 1,
  });
  return (
    <Card className="p-4">
      <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">{label}</div>
      <SearchInput value={search} onChange={setSearch} placeholder="Search a team…" />
      {debounced.length >= 1 && (
        <div className="mt-2 max-h-56 space-y-1 overflow-auto">
          {(q.data?.items ?? []).map((t: TeamSummary) => (
            <button
              key={t.id}
              onClick={() => {
                onPick(t.id);
                setSearch("");
              }}
              className={
                "flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm hover:bg-elevated " +
                (value === t.id ? "bg-elevated" : "")
              }
            >
              <Flag team={t} size={18} /> <span className="text-fg">{t.name}</span>
            </button>
          ))}
        </div>
      )}
    </Card>
  );
}

const METRICS: { key: keyof TeamDetail["stats"]; label: string }[] = [
  { key: "titles", label: "Titles" },
  { key: "tournaments", label: "Tournaments" },
  { key: "matches_played", label: "Played" },
  { key: "wins", label: "Wins" },
  { key: "goals_for", label: "Goals for" },
  { key: "win_pct", label: "Win %" },
];

export default function Compare() {
  const [params, setParams] = useSearchParams();
  const a = params.get("a") ? Number(params.get("a")) : undefined;
  const b = params.get("b") ? Number(params.get("b")) : undefined;

  function set(key: "a" | "b", id: number) {
    const p = new URLSearchParams(params);
    p.set(key, String(id));
    setParams(p);
  }

  const q = useQuery({
    queryKey: ["compare", a, b],
    queryFn: () => api.compareTeams(a!, b!),
    enabled: !!a && !!b,
  });

  return (
    <div className="space-y-6">
      <PageHeader title="Team Comparison" subtitle="Compare two nations' World Cup finals records head-to-head." />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <TeamPicker label="Team A" value={a} onPick={(id) => set("a", id)} />
        <TeamPicker label="Team B" value={b} onPick={(id) => set("b", id)} />
      </div>

      {!a || !b ? (
        <Card className="p-8 text-center text-sm text-muted">Pick two teams to compare.</Card>
      ) : q.isLoading ? (
        <Skeleton className="h-64 w-full rounded-2xl" />
      ) : q.isError || !q.data ? (
        <ErrorState onRetry={() => q.refetch()} />
      ) : (
        <ComparisonView data={q.data} />
      )}
    </div>
  );
}

function ComparisonView({ data }: { data: import("@/types/api").TeamComparison }) {
  const { team_a: A, team_b: B, head_to_head: h } = data;
  const chartData = METRICS.map((m) => ({
    metric: m.label,
    [A.name]: A.stats[m.key] as number,
    [B.name]: B.stats[m.key] as number,
  }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2">
        <div className="flex items-center justify-end gap-2">
          <span className="font-semibold text-fg">{A.name}</span>
          <Flag team={A} size={28} />
        </div>
        <span className="text-xs text-muted">vs</span>
        <div className="flex items-center gap-2">
          <Flag team={B} size={28} />
          <span className="font-semibold text-fg">{B.name}</span>
        </div>
      </div>

      <Card className="divide-y divide-border">
        {METRICS.map((m) => {
          const av = A.stats[m.key] as number;
          const bv = B.stats[m.key] as number;
          return (
            <div key={m.key} className="grid grid-cols-[1fr_auto_1fr] items-center gap-2 px-4 py-2.5">
              <div className={"text-right text-sm font-bold tabular-nums " + (av >= bv ? "text-accent" : "text-muted")}>{av}</div>
              <div className="w-28 text-center text-[11px] uppercase tracking-wide text-muted">{m.label}</div>
              <div className={"text-sm font-bold tabular-nums " + (bv >= av ? "text-accent" : "text-muted")}>{bv}</div>
            </div>
          );
        })}
      </Card>

      <Card className="p-4">
        <h3 className="mb-3 font-semibold text-fg">Head-to-head (World Cup finals)</h3>
        {h.matches === 0 ? (
          <p className="text-sm text-muted">These teams have never met at a World Cup finals.</p>
        ) : (
          <div className="grid grid-cols-3 gap-3 text-center">
            <div>
              <div className="text-2xl font-bold text-accent tabular-nums">{h.team_a_wins}</div>
              <div className="text-xs text-muted">{A.name} wins</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-fg tabular-nums">{h.draws}</div>
              <div className="text-xs text-muted">Draws · {h.matches} played</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-accent tabular-nums">{h.team_b_wins}</div>
              <div className="text-xs text-muted">{B.name} wins</div>
            </div>
          </div>
        )}
      </Card>

      <Card className="p-4">
        <h3 className="mb-3 font-semibold text-fg">Side-by-side metrics</h3>
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={chartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
              <CartesianGrid stroke={GRID_COLOR} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="metric" stroke={AXIS_COLOR} tick={{ fontSize: 11 }} />
              <YAxis stroke={AXIS_COLOR} tick={{ fontSize: 11 }} />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: "hsl(var(--elevated))" }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey={A.name} fill={CHART_COLORS[0]} radius={[4, 4, 0, 0]} />
              <Bar dataKey={B.name} fill={CHART_COLORS[1]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
