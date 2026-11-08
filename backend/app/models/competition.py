"""Competition, edition, stage and group models (tournament structure)."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Competition(Base, TimestampMixin):
    """A competition family (Men's World Cup, Women's World Cup, ...)."""

    __tablename__ = "competition"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    gender: Mapped[str] = mapped_column(String(10), default="men")
    kind: Mapped[str] = mapped_column(String(20), default="national")
    description: Mapped[str | None] = mapped_column(Text)

    editions = relationship(
        "CompetitionEdition", back_populates="competition", order_by="CompetitionEdition.year"
    )


class CompetitionEdition(Base, TimestampMixin):
    """A single tournament, e.g. the 1930 FIFA World Cup."""

    __tablename__ = "competition_edition"

    id: Mapped[int] = mapped_column(primary_key=True)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competition.id"), index=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)

    host_name: Mapped[str | None] = mapped_column(String(200))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    num_teams: Mapped[int | None] = mapped_column(Integer)
    num_matches: Mapped[int | None] = mapped_column(Integer)  # computed from matches
    total_goals: Mapped[int | None] = mapped_column(Integer)  # computed from matches
    format: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="completed")  # completed/ongoing/upcoming

    champion_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"))
    runner_up_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"))
    third_place_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"))

    data_confidence: Mapped[str] = mapped_column(String(20), default="verified")
    source_key: Mapped[str | None] = mapped_column(String(64))

    competition = relationship("Competition", back_populates="editions", lazy="joined")
    champion = relationship("Team", foreign_keys=[champion_team_id], lazy="joined")
    runner_up = relationship("Team", foreign_keys=[runner_up_team_id], lazy="joined")
    third_place = relationship("Team", foreign_keys=[third_place_team_id], lazy="joined")
    stages = relationship(
        "TournamentStage", back_populates="edition", cascade="all, delete-orphan"
    )
    groups = relationship(
        "TournamentGroup", back_populates="edition", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("competition_id", "year", name="uq_competition_year"),
    )


class TournamentStage(Base):
    """A stage within an edition (Group Stage, Round of 16, Final, ...)."""

    __tablename__ = "tournament_stage"

    id: Mapped[int] = mapped_column(primary_key=True)
    edition_id: Mapped[int] = mapped_column(
        ForeignKey("competition_edition.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(80))
    stage_type: Mapped[str] = mapped_column(String(20))  # group / knockout / final / third_place
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    edition = relationship("CompetitionEdition", back_populates="stages")

    __table_args__ = (
        UniqueConstraint("edition_id", "name", name="uq_stage_edition_name"),
    )


class TournamentGroup(Base):
    __tablename__ = "tournament_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    edition_id: Mapped[int] = mapped_column(
        ForeignKey("competition_edition.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(40))

    edition = relationship("CompetitionEdition", back_populates="groups")
    standings = relationship(
        "GroupStanding", back_populates="group", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("edition_id", "name", name="uq_group_edition_name"),
    )


class GroupStanding(Base):
    __tablename__ = "group_standing"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("tournament_group.id", ondelete="CASCADE"), index=True
    )
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    played: Mapped[int | None] = mapped_column(Integer)
    won: Mapped[int | None] = mapped_column(Integer)
    drawn: Mapped[int | None] = mapped_column(Integer)
    lost: Mapped[int | None] = mapped_column(Integer)
    goals_for: Mapped[int | None] = mapped_column(Integer)
    goals_against: Mapped[int | None] = mapped_column(Integer)
    points: Mapped[int | None] = mapped_column(Integer)
    rank: Mapped[int | None] = mapped_column(Integer)
    qualified: Mapped[bool | None] = mapped_column(Boolean)

    group = relationship("TournamentGroup", back_populates="standings")
    team = relationship("Team", lazy="joined")
