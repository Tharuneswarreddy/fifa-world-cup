"""Response schemas for the public API (v1)."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from app.schemas.common import Provenance


# --------------------------------------------------------------------------- #
# Teams
# --------------------------------------------------------------------------- #
class TeamSummary(BaseModel):
    id: int
    name: str
    slug: str
    fifa_code: str | None = None
    iso2: str | None = None
    flag_url: str | None = None
    confederation: str | None = None
    is_defunct: bool = False


class TeamWCStats(BaseModel):
    tournaments: int
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    titles: int
    finals: int
    best_finish: str | None = None
    win_pct: float


class TeamParticipation(BaseModel):
    edition_id: int
    year: int
    finish: str | None = None
    matches: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int


class TeamDetail(TeamSummary):
    stats: TeamWCStats
    titles_years: list[int] = []
    participations: list[TeamParticipation] = []
    provenance: Provenance | None = None


# --------------------------------------------------------------------------- #
# Competitions / editions
# --------------------------------------------------------------------------- #
class CompetitionOut(BaseModel):
    id: int
    code: str
    name: str
    gender: str
    kind: str
    edition_count: int = 0


class EditionSummary(BaseModel):
    id: int
    competition_code: str
    year: int
    name: str
    slug: str
    host_name: str | None = None
    status: str
    num_teams: int | None = None
    num_matches: int | None = None
    total_goals: int | None = None
    format: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    champion: TeamSummary | None = None
    runner_up: TeamSummary | None = None
    third_place: TeamSummary | None = None
    data_confidence: str | None = None


class EditionTopScorer(BaseModel):
    player_id: int
    name: str
    slug: str
    team: TeamSummary | None = None
    goals: int


class EditionOverview(EditionSummary):
    top_scorers: list[EditionTopScorer] = []
    teams: list[TeamSummary] = []
    provenance: Provenance | None = None


# --------------------------------------------------------------------------- #
# Players
# --------------------------------------------------------------------------- #
class PlayerSummary(BaseModel):
    id: int
    name: str
    slug: str
    primary_team: TeamSummary | None = None
    goals: int | None = None
    tournaments: int | None = None


class PlayerEditionGoals(BaseModel):
    edition_id: int
    year: int
    goals: int


class PlayerDetail(PlayerSummary):
    total_goals: int
    penalties: int
    own_goals: int
    first_year: int | None = None
    last_year: int | None = None
    goals_by_edition: list[PlayerEditionGoals] = []
    # Profile fields unavailable from the open dataset are explicitly null.
    birth_date: date | None = None
    position: str | None = None
    height_cm: int | None = None
    appearances: int | None = None  # not recorded in source
    provenance: Provenance | None = None


# --------------------------------------------------------------------------- #
# Matches
# --------------------------------------------------------------------------- #
class MatchEditionRef(BaseModel):
    id: int
    year: int
    name: str


class MatchSummary(BaseModel):
    id: int
    match_date: date
    home: TeamSummary
    away: TeamSummary
    home_score: int | None = None
    away_score: int | None = None
    winner_team_id: int | None = None
    decided_by: str | None = None
    neutral: bool = False
    city: str | None = None
    country_name: str | None = None
    status: str
    tournament_label: str | None = None
    edition: MatchEditionRef | None = None


class GoalOut(BaseModel):
    minute: int | None = None
    player_id: int | None = None
    player_name: str | None = None
    player_slug: str | None = None
    team_id: int
    own_goal: bool = False
    penalty: bool = False


class ShootoutOut(BaseModel):
    winner_team_id: int | None = None
    first_shooter_team_id: int | None = None


class MatchDetail(MatchSummary):
    goals: list[GoalOut] = []
    shootout: ShootoutOut | None = None
    provenance: Provenance | None = None


# --------------------------------------------------------------------------- #
# Records / leaderboards
# --------------------------------------------------------------------------- #
class RecordRow(BaseModel):
    rank: int
    label: str
    value: float
    subtitle: str | None = None
    team: TeamSummary | None = None
    player_id: int | None = None
    player_slug: str | None = None


class Leaderboard(BaseModel):
    key: str
    title: str
    unit: str
    rows: list[RecordRow]


# --------------------------------------------------------------------------- #
# Comparison / head-to-head
# --------------------------------------------------------------------------- #
class HeadToHead(BaseModel):
    team_a_id: int
    team_b_id: int
    matches: int
    team_a_wins: int
    team_b_wins: int
    draws: int
    team_a_goals: int
    team_b_goals: int
    recent: list[MatchSummary] = []


class TeamComparison(BaseModel):
    team_a: TeamDetail
    team_b: TeamDetail
    head_to_head: HeadToHead


# --------------------------------------------------------------------------- #
# Search / map / data-status
# --------------------------------------------------------------------------- #
class SearchHit(BaseModel):
    type: str  # team | player | edition | match
    id: int
    title: str
    subtitle: str | None = None
    slug: str | None = None


class SearchResults(BaseModel):
    query: str
    teams: list[SearchHit] = []
    players: list[SearchHit] = []
    editions: list[SearchHit] = []


class MapParticipation(BaseModel):
    team_id: int
    name: str
    iso2: str | None = None
    flag_url: str | None = None
    appearances: int
    titles: int
    best_finish: str | None = None


class DataSourceOut(BaseModel):
    key: str
    name: str
    url: str | None = None
    license: str | None = None
    last_synced_at: str | None = None


class DataStatus(BaseModel):
    sources: list[DataSourceOut]
    totals: dict[str, int]
    competition_coverage: list[dict]
    api_football_quota: dict | None = None
    generated_at: str
