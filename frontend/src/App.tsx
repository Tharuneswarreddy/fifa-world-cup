import { Suspense, lazy, useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { Spinner } from "@/components/ui/primitives";

const Home = lazy(() => import("@/pages/Home"));
const Tournaments = lazy(() => import("@/pages/Tournaments"));
const TournamentDetail = lazy(() => import("@/pages/TournamentDetail"));
const Teams = lazy(() => import("@/pages/Teams"));
const TeamDetail = lazy(() => import("@/pages/TeamDetail"));
const Players = lazy(() => import("@/pages/Players"));
const PlayerDetail = lazy(() => import("@/pages/PlayerDetail"));
const Matches = lazy(() => import("@/pages/Matches"));
const MatchDetail = lazy(() => import("@/pages/MatchDetail"));
const Records = lazy(() => import("@/pages/Records"));
const Compare = lazy(() => import("@/pages/Compare"));
const MapPage = lazy(() => import("@/pages/MapPage"));
const DataStatusPage = lazy(() => import("@/pages/DataStatusPage"));
const NotFound = lazy(() => import("@/pages/NotFound"));

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

export default function App() {
  return (
    <AppShell>
      <ScrollToTop />
      <Suspense
        fallback={
          <div className="flex min-h-[50vh] items-center justify-center text-muted">
            <Spinner className="h-6 w-6" />
          </div>
        }
      >
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/tournaments" element={<Tournaments />} />
          <Route path="/tournaments/:id" element={<TournamentDetail />} />
          <Route path="/teams" element={<Teams />} />
          <Route path="/teams/:id" element={<TeamDetail />} />
          <Route path="/players" element={<Players />} />
          <Route path="/players/:id" element={<PlayerDetail />} />
          <Route path="/matches" element={<Matches />} />
          <Route path="/matches/:id" element={<MatchDetail />} />
          <Route path="/records" element={<Records />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/data" element={<DataStatusPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </AppShell>
  );
}
