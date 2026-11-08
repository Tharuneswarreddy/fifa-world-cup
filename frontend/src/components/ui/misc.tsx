import type { ReactNode } from "react";
import { ChevronLeft, ChevronRight, Database, Moon, Search, Sun } from "lucide-react";
import type { Provenance } from "@/types/api";
import { classNames } from "@/lib/format";
import { useTheme } from "@/lib/theme";
import { buttonClass } from "./primitives";

export function DataSourceLabel({ provenance, className }: { provenance?: Provenance | null; className?: string }) {
  if (!provenance) return null;
  const bits = [provenance.source, provenance.license, provenance.confidence].filter(Boolean);
  return (
    <div className={classNames("flex items-start gap-1.5 text-xs text-muted", className)}>
      <Database className="mt-0.5 h-3.5 w-3.5 shrink-0" />
      <span>
        Source: {bits.join(" · ") || "—"}
        {provenance.note ? ` — ${provenance.note}` : ""}
      </span>
    </div>
  );
}

export function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button
      onClick={toggle}
      className={buttonClass("ghost", "!px-2")}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
      title="Toggle theme"
    >
      {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  );
}

export function SearchInput({
  value,
  onChange,
  placeholder = "Search…",
  className,
  autoFocus,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
}) {
  return (
    <div className={classNames("relative", className)}>
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
      <input
        value={value}
        autoFocus={autoFocus}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-xl border border-border bg-surface py-2 pl-9 pr-3 text-sm text-fg placeholder:text-muted focus:border-accent"
      />
    </div>
  );
}

export function Pagination({
  page,
  pages,
  total,
  onPage,
}: {
  page: number;
  pages: number;
  total: number;
  onPage: (p: number) => void;
}) {
  if (pages <= 1) return <div className="text-xs text-muted">{total} total</div>;
  return (
    <div className="flex items-center justify-between gap-3 text-sm">
      <span className="text-xs text-muted">
        Page {page} of {pages} · {total} total
      </span>
      <div className="flex gap-2">
        <button className={buttonClass("outline", "!px-2")} disabled={page <= 1} onClick={() => onPage(page - 1)}>
          <ChevronLeft className="h-4 w-4" />
        </button>
        <button className={buttonClass("outline", "!px-2")} disabled={page >= pages} onClick={() => onPage(page + 1)}>
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

export function Tabs({
  tabs,
  active,
  onChange,
}: {
  tabs: { key: string; label: string; icon?: ReactNode }[];
  active: string;
  onChange: (k: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-1 rounded-xl border border-border bg-surface p-1">
      {tabs.map((t) => (
        <button
          key={t.key}
          onClick={() => onChange(t.key)}
          className={classNames(
            "inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition",
            active === t.key ? "bg-accent text-accent-fg" : "text-muted hover:bg-elevated hover:text-fg",
          )}
        >
          {t.icon}
          {t.label}
        </button>
      ))}
    </div>
  );
}
