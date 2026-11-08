"""Player models.

martj42 only provides a goalscorer's name and team, so most profile fields are
intentionally nullable and surfaced as "not recorded" in the UI when absent.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Player(Base, TimestampMixin):
    __tablename__ = "player"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)

    primary_team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"), index=True)

    # Enriched profile fields (not available from martj42; nullable on purpose).
    birth_date: Mapped[date | None] = mapped_column(Date)
    position: Mapped[str | None] = mapped_column(String(40))
    height_cm: Mapped[int | None] = mapped_column()
    photo_url: Mapped[str | None] = mapped_column(String(500))

    source_key: Mapped[str | None] = mapped_column(String(64))

    primary_team = relationship("Team", lazy="joined")
