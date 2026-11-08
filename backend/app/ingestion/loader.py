"""Historical data loader for the martj42 international-results dataset (CC0).

Reads results.csv / shootouts.csv / goalscorers.csv / former_names.csv and
populates the normalized schema. Idempotent: matches are keyed by a stable
`external_ref`, so re-running updates rather than duplicates.

Scope: by default only "FIFA World Cup" (the finals tournaments) is ingested,
keeping all-time team/player records cleanly scoped to World Cup finals.
Qualification can be included with include_qualifiers=True.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.reference_data import (
    CONFEDERATIONS,
    COUNTRY_META,
    MENS_WORLD_CUP_EDITIONS,
)
from app.models import (
    Competition,
    CompetitionEdition,
    Confederation,
    DataSource,
    Match,
    MatchGoal,
    PenaltyShootout,
    Player,
    Team,
    TeamAlias,
)

WC_FINALS_LABEL = "FIFA World Cup"
WC_QUAL_LABEL = "FIFA World Cup qualification"
SOURCE_MARTJ42 = "martj42"
SOURCE_SEED = "seed"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "n-a"


def _bool(value: str | None) -> bool:
    return str(value).strip().upper() in {"TRUE", "1", "YES", "T"}


def _int(value: str | None) -> int | None:
    if value is None:
        return None
    value = value.strip()
    if value in {"", "NA", "N/A", "null", "None"}:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _date(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


@dataclass
class ImportStats:
    teams_created: int = 0
    players_created: int = 0
    matches_created: int = 0
    matches_updated: int = 0
    goals_created: int = 0
    shootouts_created: int = 0
    editions_created: int = 0
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "teams_created": self.teams_created,
            "players_created": self.players_created,
            "matches_created": self.matches_created,
            "matches_updated": self.matches_updated,
            "goals_created": self.goals_created,
            "shootouts_created": self.shootouts_created,
            "editions_created": self.editions_created,
            "notes": self.notes,
        }


# --------------------------------------------------------------------------- #
# Loader
# --------------------------------------------------------------------------- #
class HistoryLoader:
    def __init__(self, session: AsyncSession, data_dir: Path):
        self.session = session
        self.data_dir = data_dir
        self.stats = ImportStats()
        self.teams: dict[str, Team] = {}
        self.players: dict[str, Player] = {}
        self.confeds: dict[str, Confederation] = {}
        self.competitions: dict[str, Competition] = {}
        self.editions: dict[int, CompetitionEdition] = {}
        self.match_by_key: dict[tuple[str, str, str], Match] = {}

    # ---- reference / provenance ---- #
    async def ensure_sources(self) -> None:
        existing = {
            s.key: s
            for s in (await self.session.scalars(select(DataSource))).all()
        }
        defs = [
            dict(
                key=SOURCE_MARTJ42,
                name="martj42 - International football results",
                url="https://github.com/martj42/international_results",
                license="CC0-1.0 (public domain)",
                license_url="https://creativecommons.org/publicdomain/zero/1.0/",
                description="Match results, goalscorers and shootouts for international men's football since 1872.",
            ),
            dict(
                key=SOURCE_SEED,
                name="Curated verified seed",
                url=None,
                license="Public-record facts (FIFA tournament records)",
                license_url=None,
                description="Hosts, champions, finalists and formats of each World Cup edition.",
            ),
            dict(
                key="api_football",
                name="API-Football (API-SPORTS)",
                url="https://www.api-football.com/",
                license="Commercial API - subject to provider terms",
                license_url="https://www.api-football.com/documentation-v3",
                description="Live/current enrichment provider (free plan, 100 req/day).",
            ),
        ]
        for d in defs:
            if d["key"] in existing:
                existing[d["key"]].last_synced_at = datetime.now().astimezone()
            else:
                self.session.add(DataSource(**d))
        await self.session.flush()

    async def ensure_confederations(self) -> None:
        self.confeds = {
            c.code: c
            for c in (await self.session.scalars(select(Confederation))).all()
        }
        for code, name in CONFEDERATIONS:
            if code not in self.confeds:
                conf = Confederation(code=code, name=name)
                self.session.add(conf)
                self.confeds[code] = conf
        await self.session.flush()

    # ---- teams / players ---- #
    async def preload_entities(self) -> None:
        for t in (await self.session.scalars(select(Team))).all():
            self.teams[t.name] = t
        for p in (await self.session.scalars(select(Player))).all():
            self.players[p.slug] = p

    def get_team(self, name: str) -> Team:
        name = name.strip()
        team = self.teams.get(name)
        if team:
            return team
        iso2, fifa_code, confed_code, defunct = COUNTRY_META.get(
            name, (None, None, None, False)
        )
        confed = self.confeds.get(confed_code) if confed_code else None
        team = Team(
            name=name,
            slug=slugify(name),
            team_type="national",
            iso2=iso2,
            fifa_code=fifa_code,
            is_defunct=defunct,
            confederation_id=confed.id if confed else None,
            source_key=SOURCE_MARTJ42,
        )
        self.session.add(team)
        self.teams[name] = team
        self.stats.teams_created += 1
        return team

    def get_player(self, name: str, team: Team | None, own_goal: bool) -> Player:
        name = name.strip()
        slug = slugify(name)
        player = self.players.get(slug)
        if player:
            if team and not own_goal and player.primary_team_id is None:
                player.primary_team_id = team.id
            return player
        player = Player(
            name=name,
            slug=slug,
            primary_team_id=(team.id if team and not own_goal else None),
            source_key=SOURCE_MARTJ42,
        )
        self.session.add(player)
        self.players[slug] = player
        self.stats.players_created += 1
        return player

    # ---- competitions / editions ---- #
    async def ensure_competitions(self) -> None:
        self.competitions = {
            c.code: c
            for c in (await self.session.scalars(select(Competition))).all()
        }
        defs = [
            ("mens_world_cup", "FIFA World Cup", "men", "national"),
            ("womens_world_cup", "FIFA Women's World Cup", "women", "national"),
            ("club_world_cup", "FIFA Club World Cup", "men", "club"),
            ("wc_qualification", "FIFA World Cup Qualification", "men", "national"),
        ]
        for code, name, gender, kind in defs:
            if code not in self.competitions:
                comp = Competition(code=code, name=name, gender=gender, kind=kind)
                self.session.add(comp)
                self.competitions[code] = comp
        await self.session.flush()

    async def seed_editions(self) -> None:
        comp = self.competitions["mens_world_cup"]
        existing = {
            e.year: e
            for e in (
                await self.session.scalars(
                    select(CompetitionEdition).where(
                        CompetitionEdition.competition_id == comp.id
                    )
                )
            ).all()
        }
        for ed in MENS_WORLD_CUP_EDITIONS:
            year = ed["year"]
            edition = existing.get(year)
            champion = self.get_team(ed["champion"]) if ed.get("champion") else None
            runner_up = self.get_team(ed["runner_up"]) if ed.get("runner_up") else None
            third = self.get_team(ed["third"]) if ed.get("third") else None
            await self.session.flush()  # ensure team ids
            values = dict(
                name=f"{year} FIFA World Cup",
                host_name=ed.get("host"),
                num_teams=ed.get("teams"),
                format=ed.get("format"),
                status=ed.get("status", "completed"),
                champion_team_id=champion.id if champion else None,
                runner_up_team_id=runner_up.id if runner_up else None,
                third_place_team_id=third.id if third else None,
                data_confidence="verified",
                source_key=SOURCE_SEED,
            )
            if edition:
                for k, v in values.items():
                    setattr(edition, k, v)
            else:
                edition = CompetitionEdition(
                    competition_id=comp.id,
                    year=year,
                    slug=f"mens-world-cup-{year}",
                    **values,
                )
                self.session.add(edition)
                self.stats.editions_created += 1
            self.editions[year] = edition
        await self.session.flush()

    # ---- aliases ---- #
    async def load_former_names(self) -> None:
        path = self.data_dir / "former_names.csv"
        if not path.exists():
            return
        existing_pairs = {
            (a.team_id, a.alias)
            for a in (await self.session.scalars(select(TeamAlias))).all()
        }
        for row in read_csv(path):
            current = row.get("current", "").strip()
            former = row.get("former", "").strip()
            if not current or not former or current not in self.teams:
                continue
            team = self.teams[current]
            if (team.id, former) in existing_pairs:
                continue
            self.session.add(TeamAlias(team_id=team.id, alias=former))
        await self.session.flush()

    # ---- matches ---- #
    def _competition_and_edition(
        self, label: str, match_date: date
    ) -> tuple[int | None, int | None]:
        if label == WC_FINALS_LABEL:
            comp = self.competitions["mens_world_cup"]
            edition = self.editions.get(match_date.year)
            return comp.id, (edition.id if edition else None)
        if label == WC_QUAL_LABEL:
            return self.competitions["wc_qualification"].id, None
        return None, None

    async def load_results(self, labels: set[str]) -> None:
        rows = read_csv(self.data_dir / "results.csv")
        wanted = [r for r in rows if r["tournament"] in labels]
        # Preload existing matches for idempotency.
        existing = {
            m.external_ref: m
            for m in (await self.session.scalars(select(Match))).all()
            if m.external_ref
        }
        for r in wanted:
            d = _date(r["date"])
            home = self.get_team(r["home_team"])
            away = self.get_team(r["away_team"])
            label = r["tournament"]
            ext = f"martj42:{r['date']}:{r['home_team']}:{r['away_team']}:{label}"
            hs, as_ = _int(r["home_score"]), _int(r["away_score"])
            await self.session.flush()  # team ids
            comp_id, edition_id = self._competition_and_edition(label, d)
            winner_id = None
            decided = "regulation"
            if hs is not None and as_ is not None:
                if hs > as_:
                    winner_id = home.id
                elif as_ > hs:
                    winner_id = away.id
            match = existing.get(ext)
            values = dict(
                competition_id=comp_id,
                edition_id=edition_id,
                match_date=d,
                home_team_id=home.id,
                away_team_id=away.id,
                home_score=hs,
                away_score=as_,
                neutral=_bool(r["neutral"]),
                city=r.get("city") or None,
                country_name=r.get("country") or None,
                status="finished",
                winner_team_id=winner_id,
                decided_by=decided,
                tournament_label=label,
                source_key=SOURCE_MARTJ42,
            )
            if match:
                for k, v in values.items():
                    setattr(match, k, v)
                self.stats.matches_updated += 1
            else:
                match = Match(external_ref=ext, **values)
                self.session.add(match)
                self.stats.matches_created += 1
            self.match_by_key[(r["date"], r["home_team"], r["away_team"])] = match
        await self.session.flush()

    async def load_shootouts(self) -> None:
        path = self.data_dir / "shootouts.csv"
        if not path.exists():
            return
        existing_match_ids = {
            s.match_id
            for s in (await self.session.scalars(select(PenaltyShootout))).all()
        }
        for r in read_csv(path):
            key = (r["date"], r["home_team"], r["away_team"])
            match = self.match_by_key.get(key)
            if not match:
                continue
            winner = self.get_team(r["winner"]) if r.get("winner") else None
            first = self.get_team(r["first_shooter"]) if r.get("first_shooter") else None
            await self.session.flush()
            match.decided_by = "penalties"
            if winner:
                match.winner_team_id = winner.id
            if match.id in existing_match_ids:
                continue
            self.session.add(
                PenaltyShootout(
                    match_id=match.id,
                    winner_team_id=winner.id if winner else None,
                    first_shooter_team_id=first.id if first else None,
                    source_key=SOURCE_MARTJ42,
                )
            )
            self.stats.shootouts_created += 1
        await self.session.flush()

    async def load_goalscorers(self) -> None:
        path = self.data_dir / "goalscorers.csv"
        if not path.exists():
            return
        # Idempotency: skip matches that already have goals recorded.
        matches_with_goals = {
            row[0]
            for row in (
                await self.session.execute(select(MatchGoal.match_id).distinct())
            ).all()
        }
        for r in read_csv(path):
            key = (r["date"], r["home_team"], r["away_team"])
            match = self.match_by_key.get(key)
            if not match or match.id in matches_with_goals:
                continue
            scorer = (r.get("scorer") or "").strip()
            if not scorer:
                continue
            own_goal = _bool(r.get("own_goal"))
            beneficiary = self.get_team(r["team"]) if r.get("team") else None
            await self.session.flush()
            player = self.get_player(scorer, beneficiary, own_goal)
            await self.session.flush()
            self.session.add(
                MatchGoal(
                    match_id=match.id,
                    team_id=beneficiary.id if beneficiary else match.home_team_id,
                    player_id=player.id,
                    minute=_int(r.get("minute")),
                    own_goal=own_goal,
                    penalty=_bool(r.get("penalty")),
                    source_key=SOURCE_MARTJ42,
                )
            )
            self.stats.goals_created += 1
        await self.session.flush()

    # ---- aggregates ---- #
    async def recompute_edition_aggregates(self) -> None:
        """Compute per-edition counts, status (from dates) and final placements.

        Placements are taken from the verified seed when available; otherwise they
        are DERIVED from the data (champion = winner of the final/last match,
        runner-up = the loser, third = winner of the third-place play-off), which
        keeps future editions self-updating without hardcoding results.
        """
        today = date.today()
        for edition in self.editions.values():
            matches = (
                await self.session.scalars(
                    select(Match)
                    .where(Match.edition_id == edition.id)
                    .order_by(Match.match_date, Match.id)
                )
            ).all()
            edition.num_matches = len(matches)
            edition.total_goals = sum(
                (m.home_score or 0) + (m.away_score or 0) for m in matches
            )
            if not matches:
                edition.status = "upcoming"
                continue

            dates = [m.match_date for m in matches]
            edition.start_date = min(dates)
            edition.end_date = max(dates)
            if max(dates) < today:
                edition.status = "completed"
            elif min(dates) > today:
                edition.status = "upcoming"
            else:
                edition.status = "ongoing"

            # Derive placements only when the seed did not supply a champion.
            if edition.status == "completed" and edition.champion_team_id is None:
                final = matches[-1]
                if final.winner_team_id:
                    edition.champion_team_id = final.winner_team_id
                    edition.runner_up_team_id = (
                        final.away_team_id
                        if final.winner_team_id == final.home_team_id
                        else final.home_team_id
                    )
                    edition.source_key = "derived"
                    edition.data_confidence = "derived"
                if len(matches) >= 2:
                    third_place = matches[-2]
                    final_teams = {final.home_team_id, final.away_team_id}
                    tp_teams = {third_place.home_team_id, third_place.away_team_id}
                    if third_place.winner_team_id and not (tp_teams & final_teams):
                        edition.third_place_team_id = third_place.winner_team_id
        await self.session.flush()

    # ---- orchestration ---- #
    async def run(self, include_qualifiers: bool = False) -> ImportStats:
        labels = {WC_FINALS_LABEL}
        if include_qualifiers:
            labels.add(WC_QUAL_LABEL)
            self.stats.notes.append("Qualification matches included.")
        await self.ensure_sources()
        await self.ensure_confederations()
        await self.preload_entities()
        await self.ensure_competitions()
        await self.seed_editions()
        await self.load_results(labels)
        await self.load_shootouts()
        await self.load_goalscorers()
        await self.load_former_names()
        await self.recompute_edition_aggregates()
        await self.session.commit()
        return self.stats
