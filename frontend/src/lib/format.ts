export function formatDate(iso?: string | null, opts?: Intl.DateTimeFormatOptions): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString(undefined, opts ?? { year: "numeric", month: "short", day: "numeric" });
}

export function num(value?: number | null): string {
  if (value === null || value === undefined) return "—";
  return value.toLocaleString();
}

/** Score string that falls back to a dash for unrecorded scores. */
export function scoreline(home?: number | null, away?: number | null): string {
  if (home === null || home === undefined || away === null || away === undefined) return "– : –";
  return `${home} : ${away}`;
}

export function decidedByLabel(decidedBy?: string | null): string | null {
  switch (decidedBy) {
    case "penalties":
      return "after penalties";
    case "extra_time":
      return "after extra time";
    default:
      return null;
  }
}

const CONFED_NAMES: Record<string, string> = {
  UEFA: "Europe",
  CONMEBOL: "South America",
  CONCACAF: "N. & C. America",
  CAF: "Africa",
  AFC: "Asia",
  OFC: "Oceania",
};

export function confederationName(code?: string | null): string {
  if (!code) return "—";
  return CONFED_NAMES[code] ?? code;
}

export function classNames(...parts: (string | false | null | undefined)[]): string {
  return parts.filter(Boolean).join(" ");
}

export function statusLabel(status: string): { label: string; tone: "success" | "warning" | "muted" } {
  switch (status) {
    case "completed":
      return { label: "Completed", tone: "muted" };
    case "ongoing":
      return { label: "Ongoing", tone: "success" };
    case "upcoming":
      return { label: "Upcoming", tone: "warning" };
    default:
      return { label: status, tone: "muted" };
  }
}
