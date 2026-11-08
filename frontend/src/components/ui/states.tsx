import type { ReactNode } from "react";
import { AlertTriangle, Inbox } from "lucide-react";
import { classNames } from "@/lib/format";
import { Button, Card } from "./primitives";

export function Skeleton({ className }: { className?: string }) {
  return <div className={classNames("skeleton rounded-lg", className)} />;
}

export function CardGridSkeleton({ count = 6, height = "h-28" }: { count?: number; height?: string }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} className={classNames("rounded-2xl", height)} />
      ))}
    </div>
  );
}

export function RowsSkeleton({ rows = 6 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full rounded-xl" />
      ))}
    </div>
  );
}

export function EmptyState({
  title = "Nothing here yet",
  message,
  icon,
}: {
  title?: string;
  message?: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <Card className="flex flex-col items-center justify-center gap-2 px-6 py-12 text-center">
      <div className="text-muted">{icon ?? <Inbox className="h-8 w-8" />}</div>
      <div className="font-semibold text-fg">{title}</div>
      {message && <div className="max-w-md text-sm text-muted">{message}</div>}
    </Card>
  );
}

export function ErrorState({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <Card className="flex flex-col items-center justify-center gap-3 px-6 py-12 text-center">
      <AlertTriangle className="h-8 w-8 text-warning" />
      <div className="font-semibold text-fg">Could not load data</div>
      <div className="max-w-md text-sm text-muted">
        {message ?? "Something went wrong talking to the API. Check that the backend is running."}
      </div>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          Retry
        </Button>
      )}
    </Card>
  );
}
