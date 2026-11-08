"""ORM -> response-schema mapping helpers."""
from __future__ import annotations

from app.models import CompetitionEdition, Match, Team
from app.schemas.entities import (
    EditionSummary,
    MatchEditionRef,
    MatchSummary,
    TeamSummary,
)

FLAG_BASE = "https://flagcdn.com"


def flag_url(iso2: str | None) -> str | None:
    return f"{FLAG_BASE}/{iso2}.svg" if iso2 else None


def team_summary(team: Team | None) -> TeamSummary | None:
    if team is None:
        return None
    return TeamSummary(
        id=team.id,
        name=team.name,
        slug=team.slug,
        fifa_code=team.fifa_code,
        iso2=team.iso2,
        flag_url=flag_url(team.iso2),
        confederation=team.confederation.code if team.confederation else None,
        is_defunct=team.is_defunct,
    )


def edition_summary(edition: CompetitionEdition) -> EditionSummary:
    return EditionSummary(
        id=edition.id,
        competition_code=edition.competition.code if edition.competition else "",
        year=edition.year,
        name=edition.name,
        slug=edition.slug,
        host_name=edition.host_name,
        status=edition.status,
        num_teams=edition.num_teams,
        num_matches=edition.num_matches,
        total_goals=edition.total_goals,
        format=edition.format,
        start_date=edition.start_date,
        end_date=edition.end_date,
        champion=team_summary(edition.champion),
        runner_up=team_summary(edition.runner_up),
        third_place=team_summary(edition.third_place),
        data_confidence=edition.data_confidence,
    )


def match_summary(match: Match, edition_ref: MatchEditionRef | None = None) -> MatchSummary:
    return MatchSummary(
        id=match.id,
        match_date=match.match_date,
        home=team_summary(match.home_team),
        away=team_summary(match.away_team),
        home_score=match.home_score,
        away_score=match.away_score,
        winner_team_id=match.winner_team_id,
        decided_by=match.decided_by,
        neutral=match.neutral,
        city=match.city,
        country_name=match.country_name,
        status=match.status,
        tournament_label=match.tournament_label,
        edition=edition_ref,
    )
