"""Competition endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Competition, CompetitionEdition
from app.schemas.entities import CompetitionOut
from app.services.mappers import edition_summary

router = APIRouter(prefix="/competitions", tags=["competitions"])


async def _edition_counts(session: AsyncSession) -> dict[int, int]:
    rows = (
        await session.execute(
            select(CompetitionEdition.competition_id, func.count())
            .group_by(CompetitionEdition.competition_id)
        )
    ).all()
    return {cid: n for cid, n in rows}


@router.get("", response_model=list[CompetitionOut])
async def list_competitions(session: AsyncSession = Depends(get_db)):
    comps = (await session.scalars(select(Competition).order_by(Competition.id))).all()
    counts = await _edition_counts(session)
    return [
        CompetitionOut(
            id=c.id,
            code=c.code,
            name=c.name,
            gender=c.gender,
            kind=c.kind,
            edition_count=counts.get(c.id, 0),
        )
        for c in comps
    ]


@router.get("/{competition_id}", response_model=dict)
async def get_competition(competition_id: int, session: AsyncSession = Depends(get_db)):
    comp = await session.get(Competition, competition_id)
    if not comp:
        raise HTTPException(404, "Competition not found")
    editions = (
        await session.scalars(
            select(CompetitionEdition)
            .where(CompetitionEdition.competition_id == comp.id)
            .order_by(CompetitionEdition.year.desc())
        )
    ).all()
    return {
        "competition": CompetitionOut(
            id=comp.id,
            code=comp.code,
            name=comp.name,
            gender=comp.gender,
            kind=comp.kind,
            edition_count=len(editions),
        ),
        "editions": [edition_summary(e) for e in editions],
    }
