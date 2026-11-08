import axios from "axios";
import type {
  CompetitionOut,
  DataStatus,
  EditionOverview,
  EditionSummary,
  Leaderboard,
  MapParticipation,
  MatchDetail,
  MatchSummary,
  Page,
  PlayerDetail,
  PlayerSummary,
  SearchResults,
  TeamComparison,
  TeamDetail,
  TeamSummary,
} from "@/types/api";

const BASE = import.meta.env.VITE_API_BASE ?? "/api";

export const http = axios.create({ baseURL: BASE, timeout: 20000 });

function clean(params: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== ""),
  );
}

export const api = {
  health: () => http.get("/health").then((r) => r.data),

  competitions: () => http.get<CompetitionOut[]>("/v1/competitions").then((r) => r.data),

  tournaments: (params: { competition?: string; status?: string; page?: number; page_size?: number } = {}) =>
    http.get<Page<EditionSummary>>("/v1/tournaments", { params: clean(params) }).then((r) => r.data),

  tournament: (id: number) => http.get<EditionOverview>(`/v1/tournaments/${id}`).then((r) => r.data),

  tournamentFixtures: (id: number) =>
    http.get<MatchSummary[]>(`/v1/tournaments/${id}/fixtures`).then((r) => r.data),

  tournamentBracket: (id: number) => http.get(`/v1/tournaments/${id}/bracket`).then((r) => r.data),

  tournamentGroups: (id: number) => http.get(`/v1/tournaments/${id}/groups`).then((r) => r.data),

  teams: (params: { search?: string; confederation?: string; page?: number; page_size?: number } = {}) =>
    http.get<Page<TeamSummary>>("/v1/teams", { params: clean(params) }).then((r) => r.data),

  team: (id: number) => http.get<TeamDetail>(`/v1/teams/${id}`).then((r) => r.data),

  teamMatches: (id: number, page = 1) =>
    http.get<Page<MatchSummary>>(`/v1/teams/${id}/matches`, { params: { page } }).then((r) => r.data),

  compareTeams: (a: number, b: number) =>
    http.get<TeamComparison>("/v1/teams/compare", { params: { a, b } }).then((r) => r.data),

  players: (params: { search?: string; team?: number; sort?: string; page?: number; page_size?: number } = {}) =>
    http.get<Page<PlayerSummary>>("/v1/players", { params: clean(params) }).then((r) => r.data),

  player: (id: number) => http.get<PlayerDetail>(`/v1/players/${id}`).then((r) => r.data),

  matches: (params: { edition?: number; team?: number; year?: number; page?: number; page_size?: number } = {}) =>
    http.get<Page<MatchSummary>>("/v1/matches", { params: clean(params) }).then((r) => r.data),

  match: (id: number) => http.get<MatchDetail>(`/v1/matches/${id}`).then((r) => r.data),

  records: (limit = 15) => http.get<Leaderboard[]>("/v1/records", { params: { limit } }).then((r) => r.data),

  search: (q: string) => http.get<SearchResults>("/v1/search", { params: { q } }).then((r) => r.data),

  mapParticipation: (competition = "mens_world_cup") =>
    http.get<MapParticipation[]>("/v1/map/participation", { params: { competition } }).then((r) => r.data),

  dataStatus: () => http.get<DataStatus>("/v1/data-status").then((r) => r.data),
};
