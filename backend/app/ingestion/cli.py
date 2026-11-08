"""Ingestion command-line interface.

Usage (from backend/ with the venv active):

    python -m app.ingestion.cli sources
    python -m app.ingestion.cli import-history [--include-qualifiers]
    python -m app.ingestion.cli validate
    python -m app.ingestion.cli sync-status          # API-Football account/quota
    python -m app.ingestion.cli sync-tournament --year 2026   # API-Football (uses quota)
"""
from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select

from app.core.config import BACKEND_DIR, get_settings
from app.db.session import AsyncSessionLocal
from app.ingestion.loader import HistoryLoader
from app.models import (
    Competition,
    CompetitionEdition,
    DataSource,
    ImportJob,
    Match,
    MatchGoal,
    Player,
    Team,
)

DEFAULT_DATA_DIR = BACKEND_DIR.parent / "data" / "raw" / "martj42"


async def cmd_sources(_: argparse.Namespace) -> None:
    async with AsyncSessionLocal() as session:
        sources = (await session.scalars(select(DataSource))).all()
        if not sources:
            print("No data sources registered yet. Run 'import-history' first.")
            return
        for s in sources:
            print(f"- {s.key}: {s.name}")
            print(f"    license: {s.license}")
            print(f"    url: {s.url}")
            print(f"    last synced: {s.last_synced_at}")


async def cmd_import_history(args: argparse.Namespace) -> None:
    data_dir = Path(args.data_dir)
    if not (data_dir / "results.csv").exists():
        raise SystemExit(
            f"results.csv not found in {data_dir}. Download the martj42 dataset first "
            "(see scripts/download_data or DATA_SOURCES.md)."
        )
    async with AsyncSessionLocal() as session:
        loader = HistoryLoader(session, data_dir)
        stats = await loader.run(include_qualifiers=args.include_qualifiers)
        # Record the import job for provenance.
        session.add(
            ImportJob(
                source_key="martj42",
                command="import-history",
                status="success",
                finished_at=datetime.now().astimezone(),
                records_created=stats.matches_created,
                records_updated=stats.matches_updated,
                notes=json.dumps(stats.as_dict()),
            )
        )
        await session.commit()
    print(json.dumps(stats.as_dict(), indent=2))


async def cmd_validate(_: argparse.Namespace) -> None:
    async with AsyncSessionLocal() as session:
        async def count(model) -> int:
            return await session.scalar(select(func.count()).select_from(model)) or 0

        report: dict[str, object] = {
            "teams": await count(Team),
            "players": await count(Player),
            "matches": await count(Match),
            "goals": await count(MatchGoal),
            "editions": await count(CompetitionEdition),
            "competitions": await count(Competition),
        }
        # Integrity checks.
        issues: list[str] = []
        completed_no_champion = (
            await session.scalars(
                select(CompetitionEdition.year)
                .where(CompetitionEdition.status == "completed")
                .where(CompetitionEdition.champion_team_id.is_(None))
            )
        ).all()
        if completed_no_champion:
            issues.append(f"Completed editions without a champion: {completed_no_champion}")
        editions_no_matches = (
            await session.scalars(
                select(CompetitionEdition.year)
                .where(CompetitionEdition.status == "completed")
                .where((CompetitionEdition.num_matches == 0) | (CompetitionEdition.num_matches.is_(None)))
            )
        ).all()
        if editions_no_matches:
            issues.append(f"Completed editions with no matches: {editions_no_matches}")
        report["issues"] = issues or ["none"]
        print(json.dumps(report, indent=2, default=str))


async def cmd_sync_status(_: argparse.Namespace) -> None:
    from app.providers.api_football import APIFootballClient

    settings = get_settings()
    if not settings.api_football_configured:
        raise SystemExit("API_FOOTBALL_KEY not configured in backend/.env")
    client = APIFootballClient()
    try:
        status = await client.get_status()
        print(json.dumps(status, indent=2))
    finally:
        await client.aclose()


async def cmd_sync_tournament(args: argparse.Namespace) -> None:
    from app.providers.api_football import APIFootballClient

    settings = get_settings()
    if not settings.api_football_configured:
        raise SystemExit("API_FOOTBALL_KEY not configured in backend/.env")
    print(
        f"[sync-tournament] API-Football enrichment for {args.year} is quota-limited "
        f"(100 req/day). This command fetches current-tournament fixtures where the "
        f"free plan supports them. Verify coverage with 'sync-status' first."
    )
    client = APIFootballClient()
    try:
        # League 1 = FIFA World Cup (verify via /leagues before heavy use).
        data = await client.get("fixtures", params={"league": 1, "season": args.year})
        print(f"Fetched {data.get('results', 0)} fixtures. Remaining budget tracked in logs.")
    finally:
        await client.aclose()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="app.ingestion.cli", description="FIFA data ingestion")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sources", help="List registered data sources").set_defaults(func=cmd_sources)

    p_imp = sub.add_parser("import-history", help="Import martj42 historical dataset")
    p_imp.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    p_imp.add_argument("--include-qualifiers", action="store_true")
    p_imp.set_defaults(func=cmd_import_history)

    sub.add_parser("validate", help="Run data-quality checks").set_defaults(func=cmd_validate)
    sub.add_parser("sync-status", help="API-Football account & quota").set_defaults(func=cmd_sync_status)

    p_sync = sub.add_parser("sync-tournament", help="API-Football current-tournament sync")
    p_sync.add_argument("--year", type=int, required=True)
    p_sync.set_defaults(func=cmd_sync_tournament)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()
