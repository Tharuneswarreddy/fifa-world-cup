import { Link } from "react-router-dom";
import { buttonClass } from "@/components/ui/primitives";

export default function NotFound() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 text-center">
      <div className="text-6xl font-black text-accent">404</div>
      <p className="text-muted">That page is offside. Let’s get you back onside.</p>
      <Link to="/" className={buttonClass("primary")}>
        Back to dashboard
      </Link>
    </div>
  );
}
