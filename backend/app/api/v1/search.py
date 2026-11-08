"""Global search endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.entities import SearchHit, SearchResults
from app.services.stats import search_entities

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResults)
async def search(
    q: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_db),
):
    teams, players, editions = await search_entities(session, q.strip())
    return SearchResults(
        query=q,
        teams=[
            SearchHit(
                type="team",
                id=t.id,
                title=t.name,
                subtitle=t.confederation.code if t.confederation else None,
                slug=t.slug,
            )
            for t in teams
        ],
        players=[
            SearchHit(
                type="player",
                id=p.id,
                title=p.name,
                subtitle=p.primary_team.name if p.primary_team else None,
                slug=p.slug,
            )
            for p in players
        ],
        editions=[
            SearchHit(type="edition", id=e.id, title=e.name, subtitle=str(e.year), slug=e.slug)
            for e in editions
        ],
    )
