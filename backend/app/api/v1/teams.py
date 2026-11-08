"""Team endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Pagination, build_page, pagination
from app.db.session import get_db
from app.models import Confederation, Match, Team
from app.schemas.common import Page
from app.schemas.entities import (
    MatchSummary,
    TeamComparison,
    TeamDetail,
    TeamSummary,
)
from app.services.mappers import match_summary, team_summary
from app.services.stats import (
    edition_ref_map,
    head_to_head,
    team_participations,
    team_title_years,
    team_wc_stats,
)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=Page[TeamSummary])
async def list_teams(
    search: str | None = Query(None),
    confederation: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
    pg: Pagination = Depends(pagination),
):
    stmt = select(Team)
    count_stmt = select(func.count()).select_from(Team)
    if search:
        stmt = stmt.where(Team.name.ilike(f"%{search}%"))
        count_stmt = count_stmt.where(Team.name.ilike(f"%{search}%"))
    if confederation:
        stmt = stmt.join(Confederation).where(Confederation.code == confederation)
        count_stmt = count_stmt.join(Confederation).where(Confederation.code == confederation)
    total = await session.scalar(count_stmt) or 0
    teams = (
        await session.scalars(
            stmt.order_by(Team.name).offset(pg.offset).limit(pg.page_size)
        )
    ).all()
    return build_page([team_summary(t) for t in teams], total, pg)


async def _team_detail(session: AsyncSession, team: Team) -> TeamDetail:
    base = team_summary(team).model_dump()
    return TeamDetail(
        **base,
        stats=await team_wc_stats(session, team.id),
        titles_years=await team_title_years(session, team.id),
        participations=await team_participations(session, team.id),
        provenance={
            "source": "martj42",
            "license": "CC0-1.0",
            "note": "All-time totals are scoped to World Cup finals.",
        },
    )


@router.get("/compare", response_model=TeamComparison)
async def compare_teams(
    a: int = Query(..., description="team id A"),
    b: int = Query(..., description="team id B"),
    session: AsyncSession = Depends(get_db),
):
    team_a = await session.get(Team, a)
    team_b = await session.get(Team, b)
    if not team_a or not team_b:
        raise HTTPException(404, "One or both teams not found")
    return TeamComparison(
        team_a=await _team_detail(session, team_a),
        team_b=await _team_detail(session, team_b),
        head_to_head=await head_to_head(session, a, b),
    )


@router.get("/{team_id}", response_model=TeamDetail)
async def get_team(team_id: int, session: AsyncSession = Depends(get_db)):
    team = await session.get(Team, team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    return await _team_detail(session, team)


@router.get("/{team_id}/matches", response_model=Page[MatchSummary])
async def team_matches(
    team_id: int,
    session: AsyncSession = Depends(get_db),
    pg: Pagination = Depends(pagination),
):
    team = await session.get(Team, team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    where = (
        Match.edition_id.isnot(None),
        or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
    )
    total = await session.scalar(
        select(func.count()).select_from(Match).where(*where)
    ) or 0
    refs = await edition_ref_map(session)
    matches = (
        await session.scalars(
            select(Match)
            .where(*where)
            .order_by(Match.match_date.desc())
            .offset(pg.offset)
            .limit(pg.page_size)
        )
    ).all()
    return build_page(
        [match_summary(m, refs.get(m.edition_id)) for m in matches], total, pg
    )
