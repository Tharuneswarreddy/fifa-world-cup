"""Player endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Pagination, build_page, pagination
from app.db.session import get_db
from app.models import CompetitionEdition, Match, MatchGoal, Player
from app.schemas.common import Page
from app.schemas.entities import (
    PlayerDetail,
    PlayerEditionGoals,
    PlayerSummary,
)
from app.services.mappers import team_summary

router = APIRouter(prefix="/players", tags=["players"])


def _goals_subquery():
    return (
        select(MatchGoal.player_id.label("pid"), func.count().label("goals"))
        .join(Match, Match.id == MatchGoal.match_id)
        .where(Match.edition_id.isnot(None), MatchGoal.own_goal.is_(False))
        .group_by(MatchGoal.player_id)
        .subquery()
    )


@router.get("", response_model=Page[PlayerSummary])
async def list_players(
    search: str | None = Query(None),
    team: int | None = Query(None, description="primary team id"),
    sort: str = Query("goals", pattern="^(goals|name)$"),
    session: AsyncSession = Depends(get_db),
    pg: Pagination = Depends(pagination),
):
    goals_sq = _goals_subquery()
    stmt = select(Player, func.coalesce(goals_sq.c.goals, 0).label("g")).outerjoin(
        goals_sq, goals_sq.c.pid == Player.id
    )
    count_stmt = select(func.count()).select_from(Player)
    if search:
        stmt = stmt.where(Player.name.ilike(f"%{search}%"))
        count_stmt = count_stmt.where(Player.name.ilike(f"%{search}%"))
    if team:
        stmt = stmt.where(Player.primary_team_id == team)
        count_stmt = count_stmt.where(Player.primary_team_id == team)
    stmt = stmt.order_by(Player.name) if sort == "name" else stmt.order_by(
        func.coalesce(goals_sq.c.goals, 0).desc(), Player.name
    )
    total = await session.scalar(count_stmt) or 0
    rows = (
        await session.execute(stmt.offset(pg.offset).limit(pg.page_size))
    ).all()
    items = [
        PlayerSummary(
            id=p.id,
            name=p.name,
            slug=p.slug,
            primary_team=team_summary(p.primary_team),
            goals=g,
        )
        for p, g in rows
    ]
    return build_page(items, total, pg)


@router.get("/{player_id}", response_model=PlayerDetail)
async def get_player(player_id: int, session: AsyncSession = Depends(get_db)):
    player = await session.get(Player, player_id)
    if not player:
        raise HTTPException(404, "Player not found")
    goals = (
        await session.scalars(
            select(MatchGoal)
            .join(Match, Match.id == MatchGoal.match_id)
            .where(MatchGoal.player_id == player_id, Match.edition_id.isnot(None))
        )
    ).all()
    total_goals = sum(1 for g in goals if not g.own_goal)
    penalties = sum(1 for g in goals if g.penalty and not g.own_goal)
    own_goals = sum(1 for g in goals if g.own_goal)

    # Goals per edition.
    rows = (
        await session.execute(
            select(CompetitionEdition.id, CompetitionEdition.year, func.count(MatchGoal.id))
            .join(Match, Match.id == MatchGoal.match_id)
            .join(CompetitionEdition, CompetitionEdition.id == Match.edition_id)
            .where(MatchGoal.player_id == player_id, MatchGoal.own_goal.is_(False))
            .group_by(CompetitionEdition.id, CompetitionEdition.year)
            .order_by(CompetitionEdition.year)
        )
    ).all()
    by_edition = [
        PlayerEditionGoals(edition_id=eid, year=yr, goals=n) for eid, yr, n in rows
    ]
    years = [e.year for e in by_edition]

    return PlayerDetail(
        id=player.id,
        name=player.name,
        slug=player.slug,
        primary_team=team_summary(player.primary_team),
        goals=total_goals,
        tournaments=len(by_edition),
        total_goals=total_goals,
        penalties=penalties,
        own_goals=own_goals,
        first_year=min(years) if years else None,
        last_year=max(years) if years else None,
        goals_by_edition=by_edition,
        birth_date=player.birth_date,
        position=player.position,
        height_cm=player.height_cm,
        appearances=None,  # not recorded in the open source
        provenance={
            "source": "martj42",
            "license": "CC0-1.0",
            "note": "Only goals are available in the source; appearances/profile not recorded.",
        },
    )
