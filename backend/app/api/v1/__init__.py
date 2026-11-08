"""Aggregate all v1 routers under /api/v1."""
from fastapi import APIRouter

from app.api.v1 import (
    competitions,
    matches,
    meta,
    players,
    records,
    search,
    teams,
    tournaments,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(competitions.router)
api_router.include_router(tournaments.router)
api_router.include_router(teams.router)
api_router.include_router(players.router)
api_router.include_router(matches.router)
api_router.include_router(records.router)
api_router.include_router(search.router)
api_router.include_router(meta.router)
