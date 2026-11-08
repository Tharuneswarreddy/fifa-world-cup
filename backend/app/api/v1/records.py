"""Records & leaderboards endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.entities import Leaderboard
from app.services.stats import leaderboards

router = APIRouter(tags=["records"])


@router.get("/records", response_model=list[Leaderboard])
@router.get("/leaderboards", response_model=list[Leaderboard])
async def get_records(
    limit: int = Query(15, ge=3, le=50),
    session: AsyncSession = Depends(get_db),
):
    return await leaderboards(session, limit=limit)
