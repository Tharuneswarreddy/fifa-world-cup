"""FastAPI application entrypoint for the FIFA World Cup Intelligence Platform."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger("app")

app = FastAPI(
    title="FIFA World Cup Intelligence Platform",
    version="0.1.0",
    description=(
        "Public, read-only API for historical and current FIFA World Cup data. "
        "Historical match data: martj42 (CC0). Enrichment: API-Football (free tier)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok", "service": "fifa-wc-api", "version": app.version}


app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
