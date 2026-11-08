import { useState, type ReactNode } from "react";
import { NavLink } from "react-router-dom";
import {
  BarChart3,
  CalendarDays,
  GitCompareArrows,
  Globe2,
  Home,
  Menu,
  ShieldHalf,
  Trophy,
  Users,
  X,
  Database,
} from "lucide-react";
import { classNames } from "@/lib/format";
import { ThemeToggle } from "@/components/ui/misc";
import { GlobalSearch } from "./GlobalSearch";

const NAV = [
  { to: "/", label: "Home", icon: Home, end: true },
  { to: "/tournaments", label: "Tournaments", icon: Trophy },
  { to: "/teams", label: "Teams", icon: ShieldHalf },
  { to: "/players", label: "Players", icon: Users },
  { to: "/matches", label: "Matches", icon: CalendarDays },
  { to: "/records", label: "Records", icon: BarChart3 },
  { to: "/compare", label: "Compare", icon: GitCompareArrows },
  { to: "/map", label: "World Map", icon: Globe2 },
  { to: "/data", label: "Data Status", icon: Database },
];

function NavItems({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex flex-col gap-1">
      {NAV.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          onClick={onNavigate}
          className={({ isActive }) =>
            classNames(
              "flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition",
              isActive ? "bg-accent/15 text-accent" : "text-muted hover:bg-elevated hover:text-fg",
            )
          }
        >
          <item.icon className="h-[18px] w-[18px]" />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}

function Brand() {
  return (
    <div className="flex items-center gap-2.5">
      <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent text-accent-fg">
        <Trophy className="h-5 w-5" />
      </div>
      <div className="leading-tight">
        <div className="text-sm font-bold text-fg">World Cup</div>
        <div className="text-[11px] font-medium uppercase tracking-wider text-muted">Intelligence</div>
      </div>
    </div>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  return (
    <div className="min-h-screen bg-bg">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-60 flex-col border-r border-border bg-surface px-4 py-5 lg:flex">
        <Brand />
        <div className="mt-8 flex-1">
          <NavItems />
        </div>
        <div className="border-t border-border pt-3 text-[11px] text-muted">
          Data: martj42 (CC0) · API-Football
        </div>
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setMobileOpen(false)} />
          <aside className="absolute inset-y-0 left-0 flex w-64 flex-col border-r border-border bg-surface px-4 py-5">
            <div className="flex items-center justify-between">
              <Brand />
              <button className="text-muted" onClick={() => setMobileOpen(false)} aria-label="Close menu">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="mt-8 flex-1">
              <NavItems onNavigate={() => setMobileOpen(false)} />
            </div>
          </aside>
        </div>
      )}

      {/* Main column */}
      <div className="lg:pl-60">
        <header className="sticky top-0 z-40 border-b border-border bg-bg/85 backdrop-blur">
          <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-3">
            <button
              className="text-muted lg:hidden"
              onClick={() => setMobileOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="flex-1">
              <GlobalSearch />
            </div>
            <ThemeToggle />
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
      </div>
    </div>
  );
}
