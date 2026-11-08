"""Build the baked-in production SQLite database from the martj42 (CC0) dataset.

Produces backend/app/data/fifa.db, which is committed to the repo and shipped in
the Docker image so the deployed app needs no external database.

Run locally (from backend/ with the venv active):
    python scripts/build_sqlite.py

Re-run any time to refresh the data. Safe/idempotent: it rebuilds from scratch.
"""
from __future__ import annotations

import asyncio
import sys
import urllib.request
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.db.base import Base  # noqa: E402
import app.models  # noqa: E402,F401  (register models on Base.metadata)
from app.ingestion.loader import HistoryLoader  # noqa: E402

MARTJ42_BASE = "https://raw.githubusercontent.com/martj42/international_results/master"
CSV_FILES = ["results.csv", "shootouts.csv", "goalscorers.csv", "former_names.csv"]

DATA_DIR = BACKEND_DIR.parent / "data" / "raw" / "martj42"
DB_PATH = BACKEND_DIR / "app" / "data" / "fifa.db"


def ensure_csvs(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    if (data_dir / "results.csv").exists():
        print(f"Using existing CSVs in {data_dir}")
        return
    print(f"Downloading martj42 dataset (CC0) into {data_dir}")
    for name in CSV_FILES:
        target = data_dir / name
        urllib.request.urlretrieve(f"{MARTJ42_BASE}/{name}", target)  # noqa: S310
        print(f"  OK  {name}  ({target.stat().st_size / 1024:,.0f} KB)")


async def build() -> None:
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    ensure_csvs(DATA_DIR)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    url = f"sqlite+aiosqlite:///{DB_PATH.as_posix()}"
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        loader = HistoryLoader(session, DATA_DIR)
        stats = await loader.run()
    await engine.dispose()

    size_mb = DB_PATH.stat().st_size / (1024 * 1024)
    print(f"\nBuilt {DB_PATH} ({size_mb:.1f} MB)")
    print(
        f"  teams={stats.teams_created} players={stats.players_created} "
        f"matches={stats.matches_created} goals={stats.goals_created} "
        f"editions={stats.editions_created}"
    )


if __name__ == "__main__":
    asyncio.run(build())
