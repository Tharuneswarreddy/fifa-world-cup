"""Metadata endpoints: data status and world-map participation."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import (
    Competition,
    CompetitionEdition,
    DataSource,
    Match,
    MatchGoal,
    Player,
    Team,
)
from app.schemas.entities import (
    DataSourceOut,
    DataStatus,
    MapParticipation,
)
from app.services.mappers import flag_url
from app.services.stats import _edition_placements

router = APIRouter(tags=["meta"])


@router.get("/data-status", response_model=DataStatus)
async def data_status(session: AsyncSession = Depends(get_db)):
    sources = (await session.scalars(select(DataSource))).all()

    async def count(model) -> int:
        return await session.scalar(select(func.count()).select_from(model)) or 0

    totals = {
        "teams": await count(Team),
        "players": await count(Player),
        "matches": await count(Match),
        "goals": await count(MatchGoal),
        "editions": await count(CompetitionEdition),
    }
    # Per-competition coverage.
    comp_rows = (
        await session.execute(
            select(
                Competition.code,
                Competition.name,
                func.count(CompetitionEdition.id),
            )
            .outerjoin(CompetitionEdition, CompetitionEdition.competition_id == Competition.id)
            .group_by(Competition.id)
            .order_by(Competition.id)
        )
    ).all()
    coverage = [
        {"competition": code, "name": name, "editions": n} for code, name, n in comp_rows
    ]
    return DataStatus(
        sources=[
            DataSourceOut(
                key=s.key,
                name=s.name,
                url=s.url,
                license=s.license,
                last_synced_at=s.last_synced_at.isoformat() if s.last_synced_at else None,
            )
            for s in sources
        ],
        totals=totals,
        competition_coverage=coverage,
        api_football_quota=None,  # populated only by the explicit sync-status CLI (quota-limited)
        generated_at=datetime.now().astimezone().isoformat(),
    )


@router.get("/map/participation", response_model=list[MapParticipation])
async def map_participation(
    competition: str = Query("mens_world_cup"),
    session: AsyncSession = Depends(get_db),
):
    # Aggregate appearances/titles per team over the chosen competition's finals.
    matches = (
        await session.scalars(
            select(Match)
            .join(CompetitionEdition, CompetitionEdition.id == Match.edition_id)
            .join(Competition, Competition.id == CompetitionEdition.competition_id)
            .where(Competition.code == competition)
        )
    ).all()
    placements = await _edition_placements(session)

    appearances: dict[int, set[int]] = {}
    for m in matches:
        for tid in (m.home_team_id, m.away_team_id):
            appearances.setdefault(tid, set()).add(m.edition_id)

    titles: dict[int, int] = {}
    finals: dict[int, int] = {}
    thirds: dict[int, int] = {}
    for p in placements.values():
        if p["champion"]:
            titles[p["champion"]] = titles.get(p["champion"], 0) + 1
        for key in ("champion", "runner_up"):
            if p[key]:
                finals[p[key]] = finals.get(p[key], 0) + 1
        if p["third"]:
            thirds[p["third"]] = thirds.get(p["third"], 0) + 1

    if not appearances:
        return []
    teams = (
        await session.scalars(select(Team).where(Team.id.in_(appearances.keys())))
    ).all()
    result = []
    for t in teams:
        n_titles = titles.get(t.id, 0)
        if n_titles:
            best = "Champion"
        elif finals.get(t.id):
            best = "Runner-up"
        elif thirds.get(t.id):
            best = "Third place"
        else:
            best = "Qualified"
        result.append(
            MapParticipation(
                team_id=t.id,
                name=t.name,
                iso2=t.iso2,
                flag_url=flag_url(t.iso2),
                appearances=len(appearances.get(t.id, set())),
                titles=n_titles,
                best_finish=best,
            )
        )
    result.sort(key=lambda r: (-r.appearances, r.name))
    return result
