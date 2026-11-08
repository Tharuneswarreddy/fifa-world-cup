"""Tournament (competition-edition) endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Pagination, build_page, pagination
from app.db.session import get_db
from app.models import CompetitionEdition, Match, MatchGoal, Player, Team
from app.schemas.common import Page
from app.schemas.entities import (
    EditionOverview,
    EditionSummary,
    EditionTopScorer,
    MatchSummary,
    TeamSummary,
)
from app.services.mappers import edition_summary, match_summary, team_summary
from app.services.stats import edition_ref_map

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


async def _get_edition(session: AsyncSession, edition_id: int) -> CompetitionEdition:
    edition = await session.get(CompetitionEdition, edition_id)
    if not edition:
        raise HTTPException(404, "Tournament edition not found")
    return edition


async def _edition_top_scorers(
    session: AsyncSession, edition_id: int, limit: int = 10
) -> list[EditionTopScorer]:
    rows = (
        await session.execute(
            select(MatchGoal.player_id, func.count(MatchGoal.id).label("g"))
            .join(Match, Match.id == MatchGoal.match_id)
            .where(Match.edition_id == edition_id, MatchGoal.own_goal.is_(False))
            .group_by(MatchGoal.player_id)
            .order_by(func.count(MatchGoal.id).desc())
            .limit(limit)
        )
    ).all()
    ids = [pid for pid, _ in rows]
    pmap = {
        p.id: p
        for p in (await session.scalars(select(Player).where(Player.id.in_(ids)))).all()
    } if ids else {}
    return [
        EditionTopScorer(
            player_id=pid,
            name=pmap[pid].name,
            slug=pmap[pid].slug,
            team=team_summary(pmap[pid].primary_team),
            goals=g,
        )
        for pid, g in rows
        if pid in pmap
    ]


async def _edition_teams(session: AsyncSession, edition_id: int) -> list[TeamSummary]:
    home = select(Match.home_team_id.label("tid")).where(Match.edition_id == edition_id)
    away = select(Match.away_team_id.label("tid")).where(Match.edition_id == edition_id)
    ids = {r[0] for r in (await session.execute(home.union(away))).all()}
    if not ids:
        return []
    teams = (await session.scalars(select(Team).where(Team.id.in_(ids)).order_by(Team.name))).all()
    return [team_summary(t) for t in teams]


@router.get("", response_model=Page[EditionSummary])
async def list_tournaments(
    competition: str | None = Query(None, description="competition code filter"),
    status: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
    pg: Pagination = Depends(pagination),
):
    from app.models import Competition

    stmt = select(CompetitionEdition).join(Competition)
    count_stmt = select(func.count()).select_from(CompetitionEdition).join(Competition)
    if competition:
        stmt = stmt.where(Competition.code == competition)
        count_stmt = count_stmt.where(Competition.code == competition)
    if status:
        stmt = stmt.where(CompetitionEdition.status == status)
        count_stmt = count_stmt.where(CompetitionEdition.status == status)
    total = await session.scalar(count_stmt) or 0
    editions = (
        await session.scalars(
            stmt.order_by(CompetitionEdition.year.desc())
            .offset(pg.offset)
            .limit(pg.page_size)
        )
    ).all()
    return build_page([edition_summary(e) for e in editions], total, pg)


@router.get("/{edition_id}", response_model=EditionOverview)
async def tournament_overview(edition_id: int, session: AsyncSession = Depends(get_db)):
    edition = await _get_edition(session, edition_id)
    base = edition_summary(edition).model_dump()
    return EditionOverview(
        **base,
        top_scorers=await _edition_top_scorers(session, edition_id),
        teams=await _edition_teams(session, edition_id),
        provenance={
            "source": edition.source_key,
            "confidence": edition.data_confidence,
            "note": "Match data: martj42 (CC0). Placements seeded/verified or derived from final.",
        },
    )


@router.get("/{edition_id}/fixtures", response_model=list[MatchSummary])
async def tournament_fixtures(edition_id: int, session: AsyncSession = Depends(get_db)):
    await _get_edition(session, edition_id)
    refs = await edition_ref_map(session)
    matches = (
        await session.scalars(
            select(Match)
            .where(Match.edition_id == edition_id)
            .order_by(Match.match_date, Match.id)
        )
    ).all()
    return [match_summary(m, refs.get(m.edition_id)) for m in matches]


@router.get("/{edition_id}/records")
async def tournament_records(edition_id: int, session: AsyncSession = Depends(get_db)):
    await _get_edition(session, edition_id)
    scorers = await _edition_top_scorers(session, edition_id, limit=15)
    high = (
        await session.scalars(
            select(Match)
            .where(Match.edition_id == edition_id)
            .order_by(
                (func.coalesce(Match.home_score, 0) + func.coalesce(Match.away_score, 0)).desc()
            )
            .limit(10)
        )
    ).all()
    return {
        "top_scorers": [s.model_dump() for s in scorers],
        "highest_scoring_matches": [
            {
                "home": m.home_team.name,
                "away": m.away_team.name,
                "home_score": m.home_score,
                "away_score": m.away_score,
                "goals": (m.home_score or 0) + (m.away_score or 0),
                "match_id": m.id,
            }
            for m in high
        ],
    }


@router.get("/{edition_id}/groups")
async def tournament_groups(edition_id: int, session: AsyncSession = Depends(get_db)):
    await _get_edition(session, edition_id)
    # Group assignments are not present in the open martj42 dataset.
    return {
        "available": False,
        "reason": "Group-stage composition is not available from the current open data source.",
        "groups": [],
    }


@router.get("/{edition_id}/bracket")
async def tournament_bracket(edition_id: int, session: AsyncSession = Depends(get_db)):
    edition = await _get_edition(session, edition_id)
    refs = await edition_ref_map(session)
    matches = (
        await session.scalars(
            select(Match)
            .where(Match.edition_id == edition_id)
            .order_by(Match.match_date, Match.id)
        )
    ).all()
    if not matches:
        return {"available": False, "reason": "No matches recorded.", "final": None}
    final = matches[-1]
    third = None
    if len(matches) >= 2:
        tp = matches[-2]
        if {tp.home_team_id, tp.away_team_id}.isdisjoint({final.home_team_id, final.away_team_id}):
            third = tp
    return {
        "available": True,
        "note": "Full round-by-round bracket is not in the open source; final and third-place "
        "play-off are derived from the fixture chronology and verified placements.",
        "champion": team_summary(edition.champion).model_dump() if edition.champion else None,
        "final": match_summary(final, refs.get(final.edition_id)).model_dump(),
        "third_place_match": (
            match_summary(third, refs.get(third.edition_id)).model_dump() if third else None
        ),
    }
