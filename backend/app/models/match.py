"""Match, goal and penalty-shootout models (the factual core)."""
from __future__ import annotations

from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Match(Base, TimestampMixin):
    __tablename__ = "match"

    id: Mapped[int] = mapped_column(primary_key=True)

    competition_id: Mapped[int | None] = mapped_column(
        ForeignKey("competition.id"), index=True
    )
    edition_id: Mapped[int | None] = mapped_column(
        ForeignKey("competition_edition.id"), index=True
    )
    stage_id: Mapped[int | None] = mapped_column(ForeignKey("tournament_stage.id"))
    group_id: Mapped[int | None] = mapped_column(ForeignKey("tournament_group.id"))

    match_date: Mapped[date] = mapped_column(Date, index=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)

    # Score at the end of normal time + extra time (per martj42); excludes shootout.
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)

    neutral: Mapped[bool] = mapped_column(Boolean, default=False)
    city: Mapped[str | None] = mapped_column(String(160))
    country_name: Mapped[str | None] = mapped_column(String(160))  # venue country (historical name)

    status: Mapped[str] = mapped_column(String(20), default="finished")  # finished/scheduled

    winner_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"))  # null = draw
    decided_by: Mapped[str | None] = mapped_column(String(20))  # regulation/extra_time/penalties
    home_penalties: Mapped[int | None] = mapped_column(Integer)
    away_penalties: Mapped[int | None] = mapped_column(Integer)

    tournament_label: Mapped[str | None] = mapped_column(String(120))  # raw source label
    source_key: Mapped[str | None] = mapped_column(String(64))
    external_ref: Mapped[str | None] = mapped_column(String(120), index=True)

    home_team = relationship("Team", foreign_keys=[home_team_id], lazy="joined")
    away_team = relationship("Team", foreign_keys=[away_team_id], lazy="joined")
    goals = relationship("MatchGoal", back_populates="match", cascade="all, delete-orphan")
    shootout = relationship(
        "PenaltyShootout",
        back_populates="match",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("external_ref", name="uq_match_external_ref"),
        Index("ix_match_edition_date", "edition_id", "match_date"),
    )


class MatchGoal(Base):
    __tablename__ = "match_goal"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("match.id", ondelete="CASCADE"), index=True
    )
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), index=True)
    player_id: Mapped[int | None] = mapped_column(ForeignKey("player.id"), index=True)
    minute: Mapped[int | None] = mapped_column(Integer)
    own_goal: Mapped[bool] = mapped_column(Boolean, default=False)
    penalty: Mapped[bool] = mapped_column(Boolean, default=False)
    source_key: Mapped[str | None] = mapped_column(String(64))

    match = relationship("Match", back_populates="goals")
    team = relationship("Team", lazy="joined")
    player = relationship("Player", lazy="joined")


class PenaltyShootout(Base):
    __tablename__ = "penalty_shootout"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("match.id", ondelete="CASCADE"), unique=True, index=True
    )
    winner_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"))
    first_shooter_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"))
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)
    source_key: Mapped[str | None] = mapped_column(String(64))

    match = relationship("Match", back_populates="shootout")
    winner = relationship("Team", foreign_keys=[winner_team_id], lazy="joined")
