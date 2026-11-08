"""Test fixtures: an isolated in-memory SQLite DB and an ASGI test client.

No PostgreSQL and no external network are touched. The real get_db dependency is
overridden to use the test session.
"""
from __future__ import annotations

from datetime import date

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  register models on Base.metadata
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import (
    Competition,
    CompetitionEdition,
    Confederation,
    Match,
    MatchGoal,
    Player,
    Team,
)

TEST_URL = "sqlite+aiosqlite:///:memory:"


async def _seed(session) -> None:
    uefa = Confederation(code="UEFA", name="Europe")
    conmebol = Confederation(code="CONMEBOL", name="South America")
    session.add_all([uefa, conmebol])
    await session.flush()

    comp = Competition(code="mens_world_cup", name="FIFA World Cup", gender="men", kind="national")
    session.add(comp)
    await session.flush()

    a = Team(name="Alpha", slug="alpha", iso2="aa", fifa_code="ALP", confederation_id=uefa.id)
    b = Team(name="Beta", slug="beta", iso2="bb", fifa_code="BET", confederation_id=conmebol.id)
    session.add_all([a, b])
    await session.flush()

    edition = CompetitionEdition(
        competition_id=comp.id,
        year=2022,
        name="2022 FIFA World Cup",
        slug="mens-world-cup-2022",
        host_name="Testland",
        num_teams=2,
        num_matches=2,
        total_goals=6,
        status="completed",
        champion_team_id=a.id,
        runner_up_team_id=b.id,
    )
    session.add(edition)
    await session.flush()

    # Match 1: Alpha 3-1 Beta (Alpha win, Beta loss).
    m1 = Match(
        competition_id=comp.id,
        edition_id=edition.id,
        match_date=date(2022, 11, 20),
        home_team_id=a.id,
        away_team_id=b.id,
        home_score=3,
        away_score=1,
        winner_team_id=a.id,
        decided_by="regulation",
        external_ref="t:m1",
    )
    # Match 2: Alpha 1-1 Beta, decided on penalties (counts as a DRAW for both in all-time W/D/L).
    m2 = Match(
        competition_id=comp.id,
        edition_id=edition.id,
        match_date=date(2022, 12, 18),
        home_team_id=a.id,
        away_team_id=b.id,
        home_score=1,
        away_score=1,
        winner_team_id=a.id,  # shootout winner, but score is level
        decided_by="penalties",
        external_ref="t:m2",
    )
    session.add_all([m1, m2])
    await session.flush()

    scorer = Player(name="Star Striker", slug="star-striker", primary_team_id=a.id)
    session.add(scorer)
    await session.flush()
    session.add_all(
        [
            MatchGoal(match_id=m1.id, team_id=a.id, player_id=scorer.id, minute=10),
            MatchGoal(match_id=m1.id, team_id=a.id, player_id=scorer.id, minute=55),
            MatchGoal(match_id=m1.id, team_id=b.id, player_id=None, minute=70),
        ]
    )
    await session.commit()


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine(
        TEST_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestSession = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSession() as s:
        await _seed(s)

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
    await engine.dispose()
