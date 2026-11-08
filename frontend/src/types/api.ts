// Types mirroring the backend Pydantic response schemas (app/schemas).

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface Provenance {
  source?: string | null;
  license?: string | null;
  confidence?: string | null;
  note?: string | null;
}

export interface TeamSummary {
  id: number;
  name: string;
  slug: string;
  fifa_code?: string | null;
  iso2?: string | null;
  flag_url?: string | null;
  confederation?: string | null;
  is_defunct: boolean;
}

export interface TeamWCStats {
  tournaments: number;
  matches_played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  titles: number;
  finals: number;
  best_finish?: string | null;
  win_pct: number;
}

export interface TeamParticipation {
  edition_id: number;
  year: number;
  finish?: string | null;
  matches: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
}

export interface TeamDetail extends TeamSummary {
  stats: TeamWCStats;
  titles_years: number[];
  participations: TeamParticipation[];
  provenance?: Provenance | null;
}

export interface CompetitionOut {
  id: number;
  code: string;
  name: string;
  gender: string;
  kind: string;
  edition_count: number;
}

export interface EditionSummary {
  id: number;
  competition_code: string;
  year: number;
  name: string;
  slug: string;
  host_name?: string | null;
  status: string;
  num_teams?: number | null;
  num_matches?: number | null;
  total_goals?: number | null;
  format?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  champion?: TeamSummary | null;
  runner_up?: TeamSummary | null;
  third_place?: TeamSummary | null;
  data_confidence?: string | null;
}

export interface EditionTopScorer {
  player_id: number;
  name: string;
  slug: string;
  team?: TeamSummary | null;
  goals: number;
}

export interface EditionOverview extends EditionSummary {
  top_scorers: EditionTopScorer[];
  teams: TeamSummary[];
  provenance?: Provenance | null;
}

export interface PlayerSummary {
  id: number;
  name: string;
  slug: string;
  primary_team?: TeamSummary | null;
  goals?: number | null;
  tournaments?: number | null;
}

export interface PlayerEditionGoals {
  edition_id: number;
  year: number;
  goals: number;
}

export interface PlayerDetail extends PlayerSummary {
  total_goals: number;
  penalties: number;
  own_goals: number;
  first_year?: number | null;
  last_year?: number | null;
  goals_by_edition: PlayerEditionGoals[];
  birth_date?: string | null;
  position?: string | null;
  height_cm?: number | null;
  appearances?: number | null;
  provenance?: Provenance | null;
}

export interface MatchEditionRef {
  id: number;
  year: number;
  name: string;
}

export interface MatchSummary {
  id: number;
  match_date: string;
  home: TeamSummary;
  away: TeamSummary;
  home_score?: number | null;
  away_score?: number | null;
  winner_team_id?: number | null;
  decided_by?: string | null;
  neutral: boolean;
  city?: string | null;
  country_name?: string | null;
  status: string;
  tournament_label?: string | null;
  edition?: MatchEditionRef | null;
}

export interface GoalOut {
  minute?: number | null;
  player_id?: number | null;
  player_name?: string | null;
  player_slug?: string | null;
  team_id: number;
  own_goal: boolean;
  penalty: boolean;
}

export interface MatchDetail extends MatchSummary {
  goals: GoalOut[];
  shootout?: { winner_team_id?: number | null; first_shooter_team_id?: number | null } | null;
  provenance?: Provenance | null;
}

export interface RecordRow {
  rank: number;
  label: string;
  value: number;
  subtitle?: string | null;
  team?: TeamSummary | null;
  player_id?: number | null;
  player_slug?: string | null;
}

export interface Leaderboard {
  key: string;
  title: string;
  unit: string;
  rows: RecordRow[];
}

export interface HeadToHead {
  team_a_id: number;
  team_b_id: number;
  matches: number;
  team_a_wins: number;
  team_b_wins: number;
  draws: number;
  team_a_goals: number;
  team_b_goals: number;
  recent: MatchSummary[];
}

export interface TeamComparison {
  team_a: TeamDetail;
  team_b: TeamDetail;
  head_to_head: HeadToHead;
}

export interface SearchHit {
  type: string;
  id: number;
  title: string;
  subtitle?: string | null;
  slug?: string | null;
}

export interface SearchResults {
  query: string;
  teams: SearchHit[];
  players: SearchHit[];
  editions: SearchHit[];
}

export interface MapParticipation {
  team_id: number;
  name: string;
  iso2?: string | null;
  flag_url?: string | null;
  appearances: number;
  titles: number;
  best_finish?: string | null;
}

export interface DataStatus {
  sources: { key: string; name: string; url?: string | null; license?: string | null; last_synced_at?: string | null }[];
  totals: Record<string, number>;
  competition_coverage: { competition: string; name: string; editions: number }[];
  api_football_quota?: Record<string, unknown> | null;
  generated_at: string;
}
