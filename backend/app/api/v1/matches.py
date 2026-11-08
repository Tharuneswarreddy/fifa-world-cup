"""Match endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import Pagination, build_page, pagination
from app.db.session import get_db
from app.models import Competition, Match, MatchGoal
from app.schemas.common import Page
from app.schemas.entities import GoalOut, MatchDetail, MatchSummary, ShootoutOut
from app.services.mappers import match_summary
from app.services.stats import edition_ref_map

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=Page[MatchSummary])
async def list_matches(
    edition: int | None = Query(None),
    team: int | None = Query(None),
    year: int | None = Query(None),
    competition: str | None = Query(None),
    finals_only: bool = Query(True),
    session: AsyncSession = Depends(get_db),
    pg: Pagination = Depends(pagination),
):
    stmt = select(Match)
    count_stmt = select(func.count()).select_from(Match)

    conditions = []
    if finals_only:
        conditions.append(Match.edition_id.isnot(None))
    if edition:
        conditions.append(Match.edition_id == edition)
    if team:
        conditions.append(or_(Match.home_team_id == team, Match.away_team_id == team))
    if year:
        conditions.append(extract("year", Match.match_date) == year)
    for c in conditions:
        stmt = stmt.where(c)
        count_stmt = count_stmt.where(c)
    if competition:
        stmt = stmt.join(Competition).where(Competition.code == competition)
        count_stmt = count_stmt.join(Competition).where(Competition.code == competition)

    total = await session.scalar(count_stmt) or 0
    refs = await edition_ref_map(session)
    matches = (
        await session.scalars(
            stmt.order_by(Match.match_date.desc(), Match.id.desc())
            .offset(pg.offset)
            .limit(pg.page_size)
        )
    ).all()
    return build_page(
        [match_summary(m, refs.get(m.edition_id)) for m in matches], total, pg
    )


@router.get("/{match_id}", response_model=MatchDetail)
async def get_match(match_id: int, session: AsyncSession = Depends(get_db)):
    match = (
        await session.scalars(
            select(Match).options(selectinload(Match.shootout)).where(Match.id == match_id)
        )
    ).first()
    if not match:
        raise HTTPException(404, "Match not found")
    refs = await edition_ref_map(session)
    goals = (
        await session.scalars(
            select(MatchGoal)
            .where(MatchGoal.match_id == match_id)
            .order_by(MatchGoal.minute.nulls_last(), MatchGoal.id)
        )
    ).all()
    base = match_summary(match, refs.get(match.edition_id)).model_dump()
    shootout = None
    if match.shootout:
        shootout = ShootoutOut(
            winner_team_id=match.shootout.winner_team_id,
            first_shooter_team_id=match.shootout.first_shooter_team_id,
        )
    return MatchDetail(
        **base,
        goals=[
            GoalOut(
                minute=g.minute,
                player_id=g.player_id,
                player_name=g.player.name if g.player else None,
                player_slug=g.player.slug if g.player else None,
                team_id=g.team_id,
                own_goal=g.own_goal,
                penalty=g.penalty,
            )
            for g in goals
        ],
        shootout=shootout,
        provenance={
            "source": match.source_key,
            "license": "CC0-1.0",
            "note": "Historical matches may have fewer recorded details than modern ones.",
        },
    )
