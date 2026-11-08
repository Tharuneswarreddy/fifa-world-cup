import type { ElementType, ReactNode } from "react";
import { classNames } from "@/lib/format";

export function Card({
  children,
  className,
  as: Tag = "div",
  interactive = false,
  ...rest
}: {
  children: ReactNode;
  className?: string;
  as?: ElementType;
  interactive?: boolean;
} & Record<string, unknown>) {
  return (
    <Tag
      className={classNames(
        "rounded-2xl border border-border bg-surface shadow-card",
        interactive && "transition-colors hover:border-accent/50 hover:bg-elevated",
        className,
      )}
      {...rest}
    >
      {children}
    </Tag>
  );
}

export function StatCard({
  label,
  value,
  hint,
  accent = false,
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  accent?: boolean;
}) {
  return (
    <Card className="p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-muted">{label}</div>
      <div
        className={classNames(
          "mt-1 text-2xl font-bold tabular-nums",
          accent ? "text-accent" : "text-fg",
        )}
      >
        {value}
      </div>
      {hint !== undefined && <div className="mt-0.5 text-xs text-muted">{hint}</div>}
    </Card>
  );
}

type Tone = "muted" | "success" | "warning" | "danger" | "accent";
const TONES: Record<Tone, string> = {
  muted: "bg-elevated text-muted border-border",
  success: "bg-success/15 text-success border-success/30",
  warning: "bg-warning/15 text-warning border-warning/30",
  danger: "bg-danger/15 text-danger border-danger/30",
  accent: "bg-accent/15 text-accent border-accent/30",
};

export function Badge({ children, tone = "muted", className }: { children: ReactNode; tone?: Tone; className?: string }) {
  return (
    <span
      className={classNames(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium",
        TONES[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}

type Variant = "primary" | "outline" | "ghost" | "subtle";
const VARIANTS: Record<Variant, string> = {
  primary: "bg-accent text-accent-fg hover:brightness-110 font-semibold",
  outline: "border border-border bg-transparent text-fg hover:bg-elevated",
  ghost: "bg-transparent text-muted hover:bg-elevated hover:text-fg",
  subtle: "bg-elevated text-fg hover:brightness-110",
};

export function buttonClass(variant: Variant = "primary", className?: string): string {
  return classNames(
    "inline-flex items-center justify-center gap-2 rounded-xl px-3.5 py-2 text-sm transition disabled:opacity-50 disabled:pointer-events-none",
    VARIANTS[variant],
    className,
  );
}

export function Button({
  children,
  variant = "primary",
  className,
  ...rest
}: { children: ReactNode; variant?: Variant } & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button className={buttonClass(variant, className)} {...rest}>
      {children}
    </button>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={classNames(
        "inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent",
        className,
      )}
      role="status"
      aria-label="Loading"
    />
  );
}
