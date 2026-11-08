"""Statistics engine.

All records are computed from normalized match/goal data and scoped to World Cup
*finals* (edition_id is not null). Matches decided by a penalty shootout count as
draws in all-time W/D/L totals (FIFA convention); the shootout winner is retained
separately on the match.
"""
from __future__ import annotations

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CompetitionEdition, Match, MatchGoal, Player, Team
from app.schemas.entities import (
    HeadToHead,
    Leaderboard,
    MatchEditionRef,
    RecordRow,
    TeamParticipation,
    TeamWCStats,
)
from app.services.mappers import match_summary, team_summary


# --------------------------------------------------------------------------- #
# Shared lookups
# --------------------------------------------------------------------------- #
async def edition_ref_map(session: AsyncSession) -> dict[int, MatchEditionRef]:
    rows = (
        await session.execute(
            select(CompetitionEdition.id, CompetitionEdition.year, CompetitionEdition.name)
        )
    ).all()
    return {r.id: MatchEditionRef(id=r.id, year=r.year, name=r.name) for r in rows}


async def _edition_placements(session: AsyncSession) -> dict[int, dict[str, int | None]]:
    rows = (
        await session.execute(
            select(
                CompetitionEdition.id,
                CompetitionEdition.year,
                CompetitionEdition.champion_team_id,
                CompetitionEdition.runner_up_team_id,
                CompetitionEdition.third_place_team_id,
            )
        )
    ).all()
    return {
        r.id: {
            "year": r.year,
            "champion": r.champion_team_id,
            "runner_up": r.runner_up_team_id,
            "third": r.third_place_team_id,
        }
        for r in rows
    }


def _finish_label(team_id: int, placement: dict[str, int | None]) -> str | None:
    if placement["champion"] == team_id:
        return "Champion"
    if placement["runner_up"] == team_id:
        return "Runner-up"
    if placement["third"] == team_id:
        return "Third place"
    return None


# --------------------------------------------------------------------------- #
# Team records
# --------------------------------------------------------------------------- #
async def team_wc_stats(session: AsyncSession, team_id: int) -> TeamWCStats:
    matches = (
        await session.scalars(
            select(Match).where(
                Match.edition_id.isnot(None),
                or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
            )
        )
    ).all()
    placements = await _edition_placements(session)

    w = d = loss = gf = ga = 0
    editions: set[int] = set()
    for m in matches:
        if m.edition_id:
            editions.add(m.edition_id)
        is_home = m.home_team_id == team_id
        mine = m.home_score if is_home else m.away_score
        theirs = m.away_score if is_home else m.home_score
        if mine is None or theirs is None:
            continue
        gf += mine
        ga += theirs
        if mine > theirs:
            w += 1
        elif mine < theirs:
            loss += 1
        else:
            d += 1

    titles = sum(1 for p in placements.values() if p["champion"] == team_id)
    finals = sum(
        1
        for p in placements.values()
        if team_id in (p["champion"], p["runner_up"])
    )
    thirds = sum(1 for p in placements.values() if p["third"] == team_id)
    played = w + d + loss

    if titles:
        best = f"Champions ({titles}×)" if titles > 1 else "Champions"
    elif finals:
        best = "Runners-up"
    elif thirds:
        best = "Third place"
    elif editions:
        best = "Qualified (round data not in source)"
    else:
        best = None

    return TeamWCStats(
        tournaments=len(editions),
        matches_played=played,
        wins=w,
        draws=d,
        losses=loss,
        goals_for=gf,
        goals_against=ga,
        goal_difference=gf - ga,
        titles=titles,
        finals=finals,
        best_finish=best,
        win_pct=round((w / played) * 100, 1) if played else 0.0,
    )


async def team_participations(session: AsyncSession, team_id: int) -> list[TeamParticipation]:
    matches = (
        await session.scalars(
            select(Match).where(
                Match.edition_id.isnot(None),
                or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
            )
        )
    ).all()
    placements = await _edition_placements(session)
    by_edition: dict[int, TeamParticipation] = {}
    for m in matches:
        eid = m.edition_id
        if eid is None:
            continue
        part = by_edition.get(eid)
        if part is None:
            placement = placements.get(eid, {"champion": None, "runner_up": None, "third": None})
            part = TeamParticipation(
                edition_id=eid,
                year=placement.get("year", 0) or 0,
                finish=_finish_label(team_id, placement),
                matches=0,
                wins=0,
                draws=0,
                losses=0,
                goals_for=0,
                goals_against=0,
            )
            by_edition[eid] = part
        is_home = m.home_team_id == team_id
        mine = m.home_score if is_home else m.away_score
        theirs = m.away_score if is_home else m.home_score
        part.matches += 1
        if mine is None or theirs is None:
            continue
        part.goals_for += mine
        part.goals_against += theirs
        if mine > theirs:
            part.wins += 1
        elif mine < theirs:
            part.losses += 1
        else:
            part.draws += 1
    return sorted(by_edition.values(), key=lambda p: p.year, reverse=True)


async def team_title_years(session: AsyncSession, team_id: int) -> list[int]:
    rows = (
        await session.scalars(
            select(CompetitionEdition.year)
            .where(CompetitionEdition.champion_team_id == team_id)
            .order_by(CompetitionEdition.year)
        )
    ).all()
    return list(rows)


# --------------------------------------------------------------------------- #
# Head-to-head
# --------------------------------------------------------------------------- #
async def head_to_head(session: AsyncSession, a: int, b: int) -> HeadToHead:
    matches = (
        await session.scalars(
            select(Match)
            .where(
                Match.edition_id.isnot(None),
                or_(
                    and_(Match.home_team_id == a, Match.away_team_id == b),
                    and_(Match.home_team_id == b, Match.away_team_id == a),
                ),
            )
            .order_by(Match.match_date.desc())
        )
    ).all()
    refs = await edition_ref_map(session)
    a_w = b_w = draw = a_g = b_g = 0
    for m in matches:
        a_home = m.home_team_id == a
        a_s = m.home_score if a_home else m.away_score
        b_s = m.away_score if a_home else m.home_score
        if a_s is None or b_s is None:
            continue
        a_g += a_s
        b_g += b_s
        if a_s > b_s:
            a_w += 1
        elif b_s > a_s:
            b_w += 1
        else:
            draw += 1
    return HeadToHead(
        team_a_id=a,
        team_b_id=b,
        matches=len(matches),
        team_a_wins=a_w,
        team_b_wins=b_w,
        draws=draw,
        team_a_goals=a_g,
        team_b_goals=b_g,
        recent=[match_summary(m, refs.get(m.edition_id)) for m in matches[:10]],
    )


# --------------------------------------------------------------------------- #
# Leaderboards
# --------------------------------------------------------------------------- #
async def _teams_map(session: AsyncSession, ids: list[int]) -> dict[int, Team]:
    if not ids:
        return {}
    return {t.id: t for t in (await session.scalars(select(Team).where(Team.id.in_(ids)))).all()}


async def _players_map(session: AsyncSession, ids: list[int]) -> dict[int, Player]:
    if not ids:
        return {}
    return {p.id: p for p in (await session.scalars(select(Player).where(Player.id.in_(ids)))).all()}


async def leaderboards(session: AsyncSession, limit: int = 15) -> list[Leaderboard]:
    boards: list[Leaderboard] = []

    # Top scorers (exclude own goals). Aggregate on ids, then fetch entities.
    rows = (
        await session.execute(
            select(MatchGoal.player_id, func.count(MatchGoal.id).label("g"))
            .join(Match, Match.id == MatchGoal.match_id)
            .where(Match.edition_id.isnot(None), MatchGoal.own_goal.is_(False))
            .group_by(MatchGoal.player_id)
            .order_by(func.count(MatchGoal.id).desc())
            .limit(limit)
        )
    ).all()
    pmap = await _players_map(session, [pid for pid, _ in rows])
    boards.append(
        Leaderboard(
            key="top_scorers",
            title="All-time top scorers",
            unit="goals",
            rows=[
                RecordRow(
                    rank=i + 1,
                    label=pmap[pid].name if pid in pmap else "Unknown",
                    value=float(g),
                    player_id=pid,
                    player_slug=pmap[pid].slug if pid in pmap else None,
                )
                for i, (pid, g) in enumerate(rows)
            ],
        )
    )

    # Most titles.
    rows = (
        await session.execute(
            select(CompetitionEdition.champion_team_id, func.count().label("n"))
            .where(CompetitionEdition.champion_team_id.isnot(None))
            .group_by(CompetitionEdition.champion_team_id)
            .order_by(func.count().desc())
            .limit(limit)
        )
    ).all()
    tmap = await _teams_map(session, [tid for tid, _ in rows])
    boards.append(
        Leaderboard(
            key="most_titles",
            title="Most titles",
            unit="titles",
            rows=[
                RecordRow(rank=i + 1, label=tmap[tid].name, value=float(n), team=team_summary(tmap[tid]))
                for i, (tid, n) in enumerate(rows)
                if tid in tmap
            ],
        )
    )

    # Most matches played (home or away, finals only).
    home = select(Match.home_team_id.label("tid")).where(Match.edition_id.isnot(None))
    away = select(Match.away_team_id.label("tid")).where(Match.edition_id.isnot(None))
    appearances = home.union_all(away).subquery()
    rows = (
        await session.execute(
            select(appearances.c.tid, func.count().label("n"))
            .group_by(appearances.c.tid)
            .order_by(func.count().desc())
            .limit(limit)
        )
    ).all()
    tmap = await _teams_map(session, [tid for tid, _ in rows])
    boards.append(
        Leaderboard(
            key="most_matches",
            title="Most matches played",
            unit="matches",
            rows=[
                RecordRow(rank=i + 1, label=tmap[tid].name, value=float(n), team=team_summary(tmap[tid]))
                for i, (tid, n) in enumerate(rows)
                if tid in tmap
            ],
        )
    )

    # Most goals scored by a team.
    hg = select(Match.home_team_id.label("tid"), Match.home_score.label("g")).where(
        Match.edition_id.isnot(None)
    )
    ag = select(Match.away_team_id.label("tid"), Match.away_score.label("g")).where(
        Match.edition_id.isnot(None)
    )
    goals_sub = hg.union_all(ag).subquery()
    rows = (
        await session.execute(
            select(goals_sub.c.tid, func.coalesce(func.sum(goals_sub.c.g), 0).label("g"))
            .group_by(goals_sub.c.tid)
            .order_by(func.coalesce(func.sum(goals_sub.c.g), 0).desc())
            .limit(limit)
        )
    ).all()
    tmap = await _teams_map(session, [tid for tid, _ in rows])
    boards.append(
        Leaderboard(
            key="team_goals",
            title="Most goals (team, all-time)",
            unit="goals",
            rows=[
                RecordRow(rank=i + 1, label=tmap[tid].name, value=float(g), team=team_summary(tmap[tid]))
                for i, (tid, g) in enumerate(rows)
                if tid in tmap
            ],
        )
    )

    # Highest-scoring matches.
    rows = (
        await session.scalars(
            select(Match)
            .where(Match.edition_id.isnot(None))
            .order_by((func.coalesce(Match.home_score, 0) + func.coalesce(Match.away_score, 0)).desc())
            .limit(limit)
        )
    ).all()
    refs = await edition_ref_map(session)
    boards.append(
        Leaderboard(
            key="highest_scoring",
            title="Highest-scoring matches",
            unit="goals",
            rows=[
                RecordRow(
                    rank=i + 1,
                    label=f"{m.home_team.name} {m.home_score}-{m.away_score} {m.away_team.name}",
                    value=float((m.home_score or 0) + (m.away_score or 0)),
                    subtitle=f"{refs.get(m.edition_id).year if refs.get(m.edition_id) else ''}",
                )
                for i, m in enumerate(rows)
            ],
        )
    )
    return boards


# --------------------------------------------------------------------------- #
# Search
# --------------------------------------------------------------------------- #
async def search_entities(session: AsyncSession, q: str, limit: int = 8):
    like = f"%{q}%"
    teams = (
        await session.scalars(
            select(Team).where(Team.name.ilike(like)).order_by(Team.name).limit(limit)
        )
    ).all()
    players = (
        await session.scalars(
            select(Player).where(Player.name.ilike(like)).order_by(Player.name).limit(limit)
        )
    ).all()
    editions = (
        await session.scalars(
            select(CompetitionEdition)
            .where(CompetitionEdition.name.ilike(like))
            .order_by(CompetitionEdition.year.desc())
            .limit(limit)
        )
    ).all()
    return teams, players, editions
