import { useState } from "react";
import { Link } from "react-router-dom";
import type { TeamSummary } from "@/types/api";
import { classNames } from "@/lib/format";

function initials(name: string): string {
  const parts = name.split(/\s+/).filter(Boolean);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

export function Flag({ team, size = 20 }: { team?: TeamSummary | null; size?: number }) {
  const [err, setErr] = useState(false);
  const px = { width: size, height: Math.round(size * 0.68) };
  if (!team) return <span className="inline-block rounded-sm bg-elevated" style={px} />;
  if (team.flag_url && !err) {
    return (
      <img
        src={team.flag_url}
        alt=""
        loading="lazy"
        onError={() => setErr(true)}
        className="inline-block rounded-sm object-cover ring-1 ring-border"
        style={px}
      />
    );
  }
  // Fallback monogram (defunct nations, missing flags).
  return (
    <span
      className="inline-flex items-center justify-center rounded-sm bg-elevated text-[9px] font-bold text-muted ring-1 ring-border"
      style={px}
      aria-hidden
    >
      {team.fifa_code ?? initials(team.name)}
    </span>
  );
}

export function TeamBadge({
  team,
  size = 20,
  link = true,
  className,
  muted = false,
}: {
  team?: TeamSummary | null;
  size?: number;
  link?: boolean;
  className?: string;
  muted?: boolean;
}) {
  if (!team) return <span className="text-muted">—</span>;
  const content = (
    <span className={classNames("inline-flex items-center gap-2", className)}>
      <Flag team={team} size={size} />
      <span className={classNames("truncate", muted ? "text-muted" : "font-medium text-fg")}>
        {team.name}
      </span>
    </span>
  );
  if (!link) return content;
  return (
    <Link to={`/teams/${team.id}`} className="hover:text-accent">
      {content}
    </Link>
  );
}
